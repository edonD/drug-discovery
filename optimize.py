"""Molecule generation strategies for KRAS G12C inhibitor discovery."""
import warnings
warnings.filterwarnings('ignore')

import random
import json
import os
from rdkit import Chem
from rdkit.Chem import AllChem, BRICS, Descriptors, rdMolDescriptors
from rdkit.Chem import rdFMCS
from rdkit import DataStructs
import numpy as np


def random_fragment_combination():
    """Generate molecules by combining BRICS fragments from drug-like building blocks."""
    # Drug-like fragments commonly found in kinase/GTPase inhibitors
    fragments = [
        # Heterocyclic cores
        'c1ccc2[nH]ccc2c1',  # indole
        'c1ccc2ncccc2c1',    # quinoline
        'c1cnc2ccccc2n1',    # quinazoline
        'c1ccc2c(c1)ccn2',   # indazole
        'c1cnc(=O)[nH]c1',   # pyrimidinone
        'c1cc[nH]n1',        # pyrazole
        'c1ccncc1',          # pyridine
        'c1cncnc1',          # pyrimidine
        'c1cocn1',           # oxazole
        'c1cscn1',           # thiazole
        'c1cn[nH]c1',        # imidazole
        'c1ccoc1',           # furan
        'c1ccsc1',           # thiophene
        'c1cc2ccccc2[nH]1',  # indole
        'c1cnc2[nH]ccc2n1',  # purine-like
        # Linker fragments
        'NC(=O)',            # amide
        'NCC',              # ethylamine
        'OCC',              # ether
        'C(F)(F)F',         # trifluoromethyl
        'NS(=O)(=O)',       # sulfonamide
        'C1CC1',            # cyclopropyl
        'C1CCC1',           # cyclobutyl
        'C1CCCC1',          # cyclopentyl
        'C1CCNCC1',         # piperidine
        'C1CCOCC1',         # tetrahydropyran
        'C1CNCCN1',         # piperazine
    ]

    # Pick 2-3 fragments and try to combine
    n_frags = random.choice([2, 2, 3])
    chosen = random.sample(fragments, n_frags)

    # Try SMILES concatenation with linkers
    linkers = ['', 'C', 'CC', 'N', 'NC', 'O', 'c1ccc(cc1)', 'C(=O)N', 'NC(=O)', 'S(=O)(=O)N']
    linker = random.choice(linkers)

    if n_frags == 2:
        smi = f"{chosen[0]}{linker}{chosen[1]}"
    else:
        linker2 = random.choice(linkers)
        smi = f"{chosen[0]}{linker}{chosen[1]}{linker2}{chosen[2]}"

    mol = Chem.MolFromSmiles(smi)
    if mol:
        return Chem.MolToSmiles(mol)
    return None


def scaffold_hop_kras():
    """Generate molecules based on known KRAS G12C pharmacophore patterns."""
    # Key pharmacophoric features of KRAS G12C inhibitors:
    # 1. Aromatic/heteroaromatic core binding in switch-II pocket
    # 2. H-bond donors/acceptors for interactions with K16, D69, H95
    # 3. Hydrophobic groups filling the cryptic pocket
    # 4. Often a covalent warhead (acrylamide) - but we explore non-covalent too

    scaffolds = [
        # Pyrimidine-based (like sotorasib core but different substitution)
        'c1cnc(N{r1})nc1{r2}',
        # Quinazoline-based
        'c1ccc2c(c1)c(=O)n(c(=O)n2{r1}){r2}',
        # Benzimidazole
        'c1ccc2c(c1)nc(n2{r1}){r2}',
        # Indazole
        'c1ccc2c(c1)c({r1})nn2{r2}',
        # Pyridopyrimidine
        'c1cnc2nccc(c2n1){r1}',
        # Pyrrolopyrimidine
        'c1cc2c([nH]1)ncnc2{r1}',
        # Thieno[2,3-d]pyrimidine
        'c1cc2c(s1)ncnc2{r1}',
        # Naphthyridine
        'c1cnc2ccncc2c1{r1}',
        # Benzothiazole
        'c1ccc2c(c1)nc(s2){r1}',
        # Triazine
        'c1nc(nc(n1){r1}){r2}',
    ]

    r_groups = [
        'N1CCNCC1',          # piperazine
        'NC1CCCC1',          # cyclopentylamine
        'NC1CCCCC1',         # cyclohexylamine
        'NC1CCC(CC1)O',     # 4-hydroxycyclohexylamine
        'N1CCN(CC1)C',      # N-methylpiperazine
        'N1CCOCC1',         # morpholine
        'NC(C)C',           # isopropylamine
        'NCC1CC1',          # cyclopropylmethylamine
        'Nc1ccccc1',        # aniline
        'Nc1ccc(F)cc1',     # 4-fluoroaniline
        'Nc1ccc(Cl)cc1',    # 4-chloroaniline
        'Nc1ccncc1',        # 4-aminopyridine
        'NC(=O)C1CC1',      # cyclopropanecarboxamide
        'N(C)c1ccccc1',     # N-methylaniline
        'NCC(=O)N1CCCC1',   # pyrrolidine acetamide
        'NC1CCN(CC1)C(=O)C', # acetyl piperazine amine
        'Oc1ccccc1',        # phenol
        'c1ccc(F)cc1',      # fluorophenyl
        'c1ccncc1',         # pyridine
        'C(=O)NC',          # N-methylamide
        'C(F)(F)F',         # CF3
        'Cl',               # chloro
        'F',                # fluoro
        'OC',               # methoxy
        'C',                # methyl
        'CC',               # ethyl
        'C#N',              # nitrile
        'S(=O)(=O)NC',      # methylsulfonamide
    ]

    scaffold = random.choice(scaffolds)
    n_sites = scaffold.count('{r')

    smi = scaffold
    for i in range(1, n_sites + 1):
        r = random.choice(r_groups)
        smi = smi.replace(f'{{r{i}}}', r)

    mol = Chem.MolFromSmiles(smi)
    if mol:
        return Chem.MolToSmiles(mol)
    return None


def mutate_molecule(smiles):
    """Mutate a molecule by swapping functional groups or atoms."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    # Strategy: random atom/bond modifications
    strategies = [
        _add_substituent,
        _swap_ring_atom,
        _add_ring,
        _remove_group,
        _change_substituent,
    ]

    for _ in range(3):  # Try up to 3 times
        strategy = random.choice(strategies)
        result = strategy(smiles)
        if result:
            return result
    return None


def _add_substituent(smiles):
    """Add a small substituent to an aromatic ring."""
    substituents = ['F', 'Cl', 'C', 'OC', 'C#N', 'C(F)(F)F', 'N', 'O', 'NC(=O)C']
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    # Find aromatic carbons
    aromatic_c = [a.GetIdx() for a in mol.GetAtoms()
                  if a.GetIsAromatic() and a.GetSymbol() == 'C'
                  and a.GetTotalNumHs() > 0]

    if not aromatic_c:
        return None

    idx = random.choice(aromatic_c)
    sub = random.choice(substituents)

    # Use RWMol for editing
    new_smi = Chem.MolToSmiles(mol)
    # Simple approach: try adding via SMILES manipulation
    # This is hacky but works for quick exploration
    try:
        rwmol = Chem.RWMol(mol)
        atom = rwmol.GetAtomWithIdx(idx)
        atom.SetNumExplicitHs(max(0, atom.GetTotalNumHs() - 1))

        sub_mol = Chem.MolFromSmiles(sub)
        if sub_mol is None:
            return None

        # Add substituent atoms
        mapping = {}
        for a in sub_mol.GetAtoms():
            new_idx = rwmol.AddAtom(a)
            mapping[a.GetIdx()] = new_idx

        for b in sub_mol.GetBonds():
            rwmol.AddBond(mapping[b.GetBeginAtomIdx()], mapping[b.GetEndAtomIdx()], b.GetBondType())

        # Connect first atom of substituent to target
        rwmol.AddBond(idx, mapping[0], Chem.BondType.SINGLE)

        new_mol = rwmol.GetMol()
        Chem.SanitizeMol(new_mol)
        return Chem.MolToSmiles(new_mol)
    except:
        return None


def _swap_ring_atom(smiles):
    """Swap a ring atom (C->N or N->C) for bioisosteric replacement."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    ring_info = mol.GetRingInfo()
    ring_atoms = set()
    for ring in ring_info.AtomRings():
        ring_atoms.update(ring)

    candidates = []
    for idx in ring_atoms:
        atom = mol.GetAtomWithIdx(idx)
        if atom.GetIsAromatic():
            if atom.GetSymbol() == 'C' and atom.GetTotalNumHs() > 0:
                candidates.append((idx, 'C_to_N'))
            elif atom.GetSymbol() == 'N':
                candidates.append((idx, 'N_to_C'))

    if not candidates:
        return None

    idx, swap_type = random.choice(candidates)

    try:
        rwmol = Chem.RWMol(mol)
        atom = rwmol.GetAtomWithIdx(idx)
        if swap_type == 'C_to_N':
            atom.SetAtomicNum(7)
            atom.SetNumExplicitHs(0)
        else:
            atom.SetAtomicNum(6)

        new_mol = rwmol.GetMol()
        Chem.SanitizeMol(new_mol)
        return Chem.MolToSmiles(new_mol)
    except:
        return None


def _add_ring(smiles):
    """Try to extend a molecule with a small ring."""
    rings = ['C1CC1', 'C1CCC1', 'C1CCCC1', 'c1ccncc1', 'c1ccoc1', 'C1CCNCC1', 'C1CCOCC1']
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    # Find terminal atoms
    terminals = [a.GetIdx() for a in mol.GetAtoms()
                 if a.GetDegree() == 1 and a.GetSymbol() in ['C', 'N', 'O']]

    if not terminals:
        return None

    idx = random.choice(terminals)
    ring = random.choice(rings)

    try:
        ring_mol = Chem.MolFromSmiles(ring)
        if ring_mol is None:
            return None

        rwmol = Chem.RWMol(mol)
        mapping = {}
        for a in ring_mol.GetAtoms():
            new_idx = rwmol.AddAtom(a)
            mapping[a.GetIdx()] = new_idx

        for b in ring_mol.GetBonds():
            rwmol.AddBond(mapping[b.GetBeginAtomIdx()], mapping[b.GetEndAtomIdx()], b.GetBondType())

        rwmol.AddBond(idx, mapping[0], Chem.BondType.SINGLE)

        new_mol = rwmol.GetMol()
        Chem.SanitizeMol(new_mol)
        result = Chem.MolToSmiles(new_mol)

        # Check MW doesn't explode
        if Descriptors.MolWt(Chem.MolFromSmiles(result)) < 550:
            return result
    except:
        pass
    return None


def _remove_group(smiles):
    """Remove a terminal substituent."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    terminals = [a.GetIdx() for a in mol.GetAtoms()
                 if a.GetDegree() == 1 and a.GetSymbol() != 'H']

    if len(terminals) < 2:  # Keep at least some complexity
        return None

    idx = random.choice(terminals)

    try:
        rwmol = Chem.RWMol(mol)
        rwmol.RemoveAtom(idx)
        new_mol = rwmol.GetMol()
        Chem.SanitizeMol(new_mol)
        result = Chem.MolToSmiles(new_mol)

        if Descriptors.MolWt(Chem.MolFromSmiles(result)) > 150:
            return result
    except:
        pass
    return None


def _change_substituent(smiles):
    """Replace a terminal group with a different one."""
    result = _remove_group(smiles)
    if result:
        return _add_substituent(result)
    return None


def crossover(smi1, smi2):
    """Crossover two molecules using BRICS decomposition."""
    try:
        mol1 = Chem.MolFromSmiles(smi1)
        mol2 = Chem.MolFromSmiles(smi2)
        if mol1 is None or mol2 is None:
            return None

        frags1 = list(BRICS.BRICSDecompose(mol1))
        frags2 = list(BRICS.BRICSDecompose(mol2))

        if not frags1 or not frags2:
            return None

        # Try to combine fragments from both parents
        all_frags = list(set(frags1) | set(frags2))
        if len(all_frags) < 2:
            return None

        # Use BRICS to build new molecules
        frag_mols = [Chem.MolFromSmiles(f) for f in random.sample(all_frags, min(3, len(all_frags)))]
        frag_mols = [f for f in frag_mols if f is not None]

        if len(frag_mols) < 2:
            return None

        products = list(BRICS.BRICSBuild(frag_mols))
        if products:
            product = random.choice(products[:10])  # Pick from first 10
            smi = Chem.MolToSmiles(product)
            mw = Descriptors.MolWt(product)
            if 200 < mw < 550:
                return smi
    except:
        pass
    return None


def generate_kras_inspired():
    """Generate molecules inspired by known KRAS G12C inhibitor motifs."""
    # Key structural motifs from literature
    templates = [
        # Pyridine-pyrimidine hybrids
        'c1cnc(Nc2cccc(F)c2{sub1})nc1{sub2}',
        # Quinazoline amines
        'c1ccc2c(c1)nc(N{sub1})nc2{sub2}',
        # Benzimidazole ureas
        'c1ccc2c(c1)nc(NC(=O)N{sub1})n2{sub2}',
        # Pyrido[3,2-d]pyrimidine
        'c1cnc2nc(N{sub1})ncc2c1{sub2}',
        # Thienopyrimidine
        'c1cc2c(s1)nc(N{sub1})nc2{sub2}',
        # Pyrazolopyridine
        'c1nn2c(c1{sub1})ccnc2{sub2}',
        # Imidazo[1,2-a]pyridine
        'c1cnc2n1cc({sub1})c2{sub2}',
        # Aminopyridine amides
        'c1cc(NC(=O){sub1})ncc1{sub2}',
        # Dihydropyridine
        'C1=C(NC(=C(C1{sub1})C#N){sub2})N',
        # Tetrahydroisoquinoline
        'c1ccc2c(c1)C(CN(C2){sub1}){sub2}',
        # Naphthyridine
        'c1cc2ncc(N{sub1})cc2nc1{sub2}',
        # Chromone-like
        'O=c1cc(oc2ccccc12){sub1}',
        # Indoline amide
        'O=C(c1cc2ccccc2[nH]1){sub1}',
    ]

    subs = [
        'C1CCNCC1', 'C1CCOCC1', 'c1ccncc1', 'C1CC1',
        'C(C)C', 'CC(=O)N', 'c1ccc(F)cc1', 'c1ccc(Cl)cc1',
        'c1ccc(OC)cc1', 'c1ccncc1', 'C1CCCC1', 'C(F)(F)F',
        'CC', 'C', 'c1ccccc1', 'C1CC(O)C1', 'CC(C)(C)O',
        'c1cc(F)cc(F)c1', 'c1ccnc(N)c1', 'C1CCN(CC1)C',
        'c1ccc(-c2ccccn2)cc1', 'Cc1cnc(N)s1', 'c1csc(N)n1',
    ]

    template = random.choice(templates)
    n_subs = template.count('{sub')

    smi = template
    for i in range(1, n_subs + 1):
        sub = random.choice(subs)
        smi = smi.replace(f'{{sub{i}}}', sub)

    mol = Chem.MolFromSmiles(smi)
    if mol:
        return Chem.MolToSmiles(mol)
    return None


def generate_diverse_batch(n=50, top_hits=None):
    """Generate a diverse batch of candidate molecules."""
    candidates = set()
    attempts = 0
    max_attempts = n * 20

    while len(candidates) < n and attempts < max_attempts:
        attempts += 1

        # Choose strategy
        strategy = random.choices(
            ['kras_inspired', 'scaffold_hop', 'fragment', 'mutate', 'crossover'],
            weights=[35, 25, 15, 15, 10],
            k=1
        )[0]

        smi = None

        if strategy == 'kras_inspired':
            smi = generate_kras_inspired()
        elif strategy == 'scaffold_hop':
            smi = scaffold_hop_kras()
        elif strategy == 'fragment':
            smi = random_fragment_combination()
        elif strategy == 'mutate' and top_hits:
            parent = random.choice(top_hits)
            smi = mutate_molecule(parent)
        elif strategy == 'crossover' and top_hits and len(top_hits) >= 2:
            parents = random.sample(top_hits, 2)
            smi = crossover(parents[0], parents[1])

        if smi and smi not in candidates:
            mol = Chem.MolFromSmiles(smi)
            if mol and 150 < Descriptors.MolWt(mol) < 550:
                candidates.add(smi)

    return list(candidates)
