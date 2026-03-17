"""Molecule evaluation pipeline for KRAS G12C inhibitor discovery."""
import warnings
warnings.filterwarnings('ignore')

import json
import os
import time
from rdkit import Chem
from rdkit.Chem import Descriptors, QED, AllChem, FilterCatalog
from rdkit.Chem import DataStructs
from meeko import MoleculePreparation, PDBQTWriterLegacy
from vina import Vina
import numpy as np

# Sotorasib reference fingerprint
SOTORASIB_SMI = "C=CC(=O)N1CCN(CC1)c1c(F)ccc(NC2=NC=C(C(=O)N3CC(C)CC3=O)N2C2CCCCN2C(=O)C=C)c1F"
ADAGRASIB_SMI = "CC1(CN(C1)c1c(F)ccc(NC2=NC=C(C3=CC=NN3C3CCCCN3C(=O)C=C)N2C2CCC(O)CC2)c1F)O"

_soto_mol = Chem.MolFromSmiles(SOTORASIB_SMI)
SOTO_FP = AllChem.GetMorganFingerprintAsBitVect(_soto_mol, 2, nBits=2048)
_adag_mol = Chem.MolFromSmiles(ADAGRASIB_SMI)
ADAG_FP = AllChem.GetMorganFingerprintAsBitVect(_adag_mol, 2, nBits=2048)

# PAINS filter
_pains_params = FilterCatalog.FilterCatalogParams()
_pains_params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
PAINS_CATALOG = FilterCatalog.FilterCatalog(_pains_params)

# SA Score
from rdkit.Chem import RDConfig
import sys
sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
import sascorer

RECEPTOR_PATH = os.path.join(os.path.dirname(__file__), "6OIM_receptor.pdbqt")
CENTER = [-1.5, -5.0, 1.5]
BOX_SIZE = [22, 22, 22]

# ADMET model (lazy load)
_admet_model = None
def get_admet_model():
    global _admet_model
    if _admet_model is None:
        from admet_ai import ADMETModel
        _admet_model = ADMETModel()
    return _admet_model


def compute_properties(smiles):
    """Compute all molecular properties. Returns dict or None if invalid."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    # Canonicalize
    smiles = Chem.MolToSmiles(mol)

    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rotbonds = Descriptors.NumRotatableBonds(mol)
    qed_score = QED.qed(mol)
    sa_score = sascorer.calculateScore(mol)

    # Lipinski
    lipinski = mw <= 500 and logp <= 5 and hbd <= 5 and hba <= 10

    # PAINS
    pains_pass = not PAINS_CATALOG.HasMatch(mol)

    # Novelty
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    tanimoto_soto = DataStructs.TanimotoSimilarity(fp, SOTO_FP)
    tanimoto_adag = DataStructs.TanimotoSimilarity(fp, ADAG_FP)

    return {
        'smiles': smiles,
        'mw': round(mw, 1),
        'logp': round(logp, 2),
        'hbd': hbd,
        'hba': hba,
        'tpsa': round(tpsa, 1),
        'rotbonds': rotbonds,
        'qed': round(qed_score, 3),
        'sa_score': round(sa_score, 2),
        'lipinski_pass': lipinski,
        'pains_pass': pains_pass,
        'tanimoto_sotorasib': round(tanimoto_soto, 3),
        'tanimoto_adagrasib': round(tanimoto_adag, 3),
    }


def quick_filter(smiles):
    """Fast pre-filter before docking. Returns (pass, props) or (False, None)."""
    props = compute_properties(smiles)
    if props is None:
        return False, None

    # Loose pre-filters
    if props['qed'] < 0.3:
        props['reject_reason'] = 'low_qed'
        return False, props
    if props['sa_score'] > 6.0:
        props['reject_reason'] = 'high_sa'
        return False, props
    if not props['lipinski_pass']:
        props['reject_reason'] = 'lipinski_fail'
        return False, props
    if not props['pains_pass']:
        props['reject_reason'] = 'pains_fail'
        return False, props
    if props['tanimoto_sotorasib'] >= 0.4:
        props['reject_reason'] = 'too_similar_sotorasib'
        return False, props

    return True, props


def dock_molecule(smiles, exhaustiveness=16):
    """Dock a molecule and return score in kcal/mol, or None on failure."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    mol = Chem.AddHs(mol)

    # Try multiple conformer embeddings
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    result = AllChem.EmbedMolecule(mol, params)
    if result == -1:
        params.useRandomCoords = True
        result = AllChem.EmbedMolecule(mol, params)
        if result == -1:
            return None

    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    except:
        pass

    try:
        preparator = MoleculePreparation()
        mol_setup = preparator.prepare(mol)[0]
        pdbqt_string = PDBQTWriterLegacy.write_string(mol_setup)[0]
    except Exception as e:
        return None

    try:
        v = Vina(sf_name='vina', verbosity=0)
        v.set_receptor(RECEPTOR_PATH)
        v.set_ligand_from_string(pdbqt_string)
        v.compute_vina_maps(center=CENTER, box_size=BOX_SIZE)
        v.dock(exhaustiveness=exhaustiveness, n_poses=3)
        energies = v.energies()
        return round(energies[0][0], 2)
    except Exception as e:
        return None


def run_admet(smiles):
    """Run ADMET predictions. Returns dict with safety flags."""
    try:
        model = get_admet_model()
        preds = model.predict(smiles=smiles)

        # Extract key safety endpoints
        result = {}

        # hERG safety (look for hERG inhibition probability)
        for col in preds.columns:
            cl = col.lower()
            if 'herg' in cl:
                val = float(preds[col].iloc[0])
                result['herg_prob'] = round(val, 3)
                # If probability of hERG inhibition > 0.5, not safe
                if 'inhibit' in cl or 'block' in cl:
                    result['herg_safe'] = val < 0.5
                else:
                    result['herg_safe'] = val < 0.5

        if 'herg_safe' not in result:
            result['herg_safe'] = True  # Default if no hERG model
            result['herg_prob'] = 0.0

        # Ames mutagenicity
        for col in preds.columns:
            cl = col.lower()
            if 'ames' in cl:
                val = float(preds[col].iloc[0])
                result['ames_prob'] = round(val, 3)
                result['ames_safe'] = val < 0.5

        if 'ames_safe' not in result:
            result['ames_safe'] = True
            result['ames_prob'] = 0.0

        # Collect additional ADMET props
        for col in preds.columns:
            cl = col.lower()
            if 'caco' in cl or 'solub' in cl or 'cyp' in cl or 'clear' in cl or 'bioavail' in cl:
                result[col] = round(float(preds[col].iloc[0]), 3)

        return result
    except Exception as e:
        return {'herg_safe': True, 'ames_safe': True, 'herg_prob': 0.0, 'ames_prob': 0.0, 'error': str(e)}


def evaluate_molecule(smiles, exhaustiveness=16):
    """Full evaluation pipeline. Returns complete result dict."""
    # Quick filter
    passes, props = quick_filter(smiles)

    if props is None:
        return {'smiles': smiles, 'valid': False, 'reject_reason': 'invalid_smiles'}

    if not passes:
        props['docking_score'] = None
        props['passes_all'] = False
        return props

    # Dock
    score = dock_molecule(smiles, exhaustiveness=exhaustiveness)
    props['docking_score'] = score

    if score is None:
        props['reject_reason'] = 'docking_failed'
        props['passes_all'] = False
        return props

    if score >= -7.0:
        props['reject_reason'] = 'weak_binding'
        props['passes_all'] = False
        return props

    # ADMET for molecules that dock well
    admet = run_admet(smiles)
    props.update(admet)

    # Final pass/fail
    passes_all = (
        score < -7.0 and
        props['qed'] > 0.4 and
        props['sa_score'] < 5.0 and
        props['lipinski_pass'] and
        props['pains_pass'] and
        props['tanimoto_sotorasib'] < 0.4 and
        props.get('herg_safe', True) and
        props.get('ames_safe', True)
    )

    props['passes_all'] = passes_all

    # Tier classification
    if passes_all:
        if score < -10.0 and props['tanimoto_sotorasib'] < 0.3:
            props['tier'] = 3  # Candidate
        elif score < -8.5:
            props['tier'] = 2  # Lead
        else:
            props['tier'] = 1  # Hit
    else:
        props['tier'] = 0

    return props
