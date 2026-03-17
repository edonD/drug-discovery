#!/bin/bash
set -euo pipefail
exec > /var/log/user-data.log 2>&1

echo "=== Drug Discovery setup ==="

sleep 15
for i in 1 2 3 4 5 6 7 8 9 10; do
  fuser /var/lib/apt/lists/lock >/dev/null 2>&1 || break
  sleep 5
done
for i in 1 2 3 4 5 6 7 8 9 10; do
  fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || break
  sleep 5
done

# System packages
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential git tmux curl wget unzip \
  python3 python3-pip python3-venv python3-dev \
  swig libboost-all-dev libopenbabel-dev \
  openbabel

# Node.js + Claude CLI
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs
npm install -g @anthropic-ai/claude-code

# Python packages — install in order of dependency
pip3 install --break-system-packages \
  numpy scipy matplotlib

pip3 install --break-system-packages \
  rdkit-pypi

pip3 install --break-system-packages \
  meeko

pip3 install --break-system-packages \
  vina

pip3 install --break-system-packages \
  openbabel-wheel || echo "openbabel-wheel failed, using system openbabel"

pip3 install --break-system-packages \
  admet-ai || echo "admet-ai install failed — will retry manually"

# Verify
echo "=== Verifying installs ==="
python3 -c "from rdkit import Chem; print('rdkit OK')"
python3 -c "from vina import Vina; print('vina OK')"
python3 -c "from meeko import MoleculePreparation; print('meeko OK')"
python3 -c "import numpy; print('numpy OK')"
python3 -c "import matplotlib; print('matplotlib OK')"

# Download protein target: KRAS G12C (PDB: 6OIM)
echo "=== Downloading protein targets ==="
WORK=/home/ubuntu/workspace
mkdir -p $WORK
cd $WORK

# KRAS G12C — the "undruggable" oncogene that sotorasib (Lumakras) finally cracked
wget -q https://files.rcsb.org/download/6OIM.pdb -O 6OIM.pdb
# Also get HIV protease as a calibration target
wget -q https://files.rcsb.org/download/1HSG.pdb -O 1HSG.pdb

echo "=== Preparing protein receptors ==="
python3 << 'PYEOF'
import os
os.chdir("/home/ubuntu/workspace")

# Prepare receptors using openbabel
try:
    from openbabel import pybel

    for pdb_id in ["6OIM", "1HSG"]:
        print(f"Preparing {pdb_id}...")
        mol = list(pybel.readfile("pdb", f"{pdb_id}.pdb"))[0]

        # Remove water and ligands
        atoms_to_remove = []
        for atom in mol.atoms:
            res = atom.OBAtom.GetResidue()
            if res:
                name = res.GetName().strip()
                if name in ('HOH', 'WAT', 'SO4', 'GOL', 'EDO', 'ACE', 'NME'):
                    atoms_to_remove.append(atom.OBAtom)
        for atom in reversed(atoms_to_remove):
            mol.OBMol.DeleteAtom(atom)

        mol.OBMol.CorrectForPH(7.4)
        mol.addh()
        mol.write("pdbqt", f"{pdb_id}_receptor.pdbqt", overwrite=True)
        print(f"  {pdb_id}_receptor.pdbqt written")

except Exception as e:
    print(f"Receptor prep failed: {e}")
    print("Will need manual preparation")
PYEOF

# Convenience
cat > /home/ubuntu/go.sh << 'EOF'
#!/bin/bash
echo "=== Drug Discovery Agent ==="
echo "  cd ~/workspace/drug-discovery"
echo "  claude --dangerously-skip-permissions"
cd /home/ubuntu/workspace/drug-discovery
exec bash
EOF
chmod +x /home/ubuntu/go.sh

chown -R ubuntu:ubuntu /home/ubuntu
echo "READY" > /home/ubuntu/setup_complete
echo "=== Setup complete ==="
