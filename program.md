# Autonomous Drug Discovery — KRAS G12C Inhibitor

## The Challenge

Design a novel small molecule inhibitor of **KRAS G12C**, the most important oncology drug target of the last decade.

KRAS is a protein that acts as a molecular switch in cell growth signaling. The G12C mutation (glycine → cysteine at position 12) is found in ~13% of lung cancers, ~3% of colorectal cancers, and ~2% of pancreatic cancers. For 40 years, KRAS was called **"undruggable"** — the protein has no obvious binding pocket.

In 2021, sotorasib (Lumakras, Amgen) became the first approved KRAS G12C inhibitor. In 2022, adagrasib (Krazati, Mirati) followed. Both work by forming a **covalent bond** with the mutant cysteine-12, locking KRAS in its inactive GDP-bound state.

**Your task:** Design novel molecules that bind the KRAS G12C allosteric pocket (the switch-II pocket) with high affinity, drug-like properties, and low toxicity. You are NOT trying to rediscover sotorasib — you are trying to find **structurally different** molecules that hit the same pocket, potentially with better properties.

**Why this is hard:** The switch-II pocket is shallow and solvent-exposed. Most small molecules don't bind well to flat protein surfaces. The approved drugs needed covalent binding to achieve sufficient potency. Finding non-covalent binders or novel covalent warheads is an active area of research at every major pharma company.

## Target Protein

**PDB ID: 6OIM** — KRAS G12C in complex with a covalent inhibitor (compound 12 from ARS-1620 series).

Binding site (switch-II pocket):
```
center_x = -1.5
center_y = -5.0
center_z = 1.5
box_size = [22, 22, 22]
```

The receptor file `6OIM_receptor.pdbqt` is pre-prepared at `/home/ubuntu/workspace/6OIM_receptor.pdbqt`.

**Calibration target (optional):** HIV protease 1HSG is also available for sanity-checking your docking pipeline. Known drugs dock at -10 to -14 kcal/mol there.

## Files

| File | Editable? | Purpose |
|------|-----------|---------|
| `program.md` | **NO** | This file. The mission. |
| `specs.json` | **NO** | Pass/fail criteria. |
| `evaluate.py` | YES | Molecule scoring pipeline. |
| `optimize.py` | YES | Molecule generation and optimization loop. |
| `molecules.json` | YES | Database of all evaluated molecules. |
| `best_molecules.json` | YES | Top hits that pass all specs. |
| `README.md` | YES | **Your final deliverable.** |
| `plots/` | YES | All generated plots and molecular visualizations. |
| `results.tsv` | YES | Experiment log (not committed). |

**You CANNOT modify:** `program.md`, `specs.json`, protein structure files.

**Critical rule:** Never fabricate docking scores or property predictions. Every number must come from actually running the tools.

## Evaluated Parameters

A molecule must pass ALL of these to be considered a hit:

| Parameter | Target | What It Means |
|-----------|--------|---------------|
| `docking_score` | < -7.0 kcal/mol | Predicted binding affinity to KRAS G12C switch-II pocket |
| `qed` | > 0.4 | Quantitative drug-likeness (0-1 scale) |
| `sa_score` | < 5.0 | Synthetic accessibility (1=easy, 10=impossible) |
| `lipinski_pass` | True | Passes Rule of 5 (MW<500, LogP<5, HBD≤5, HBA≤10) |
| `pains_pass` | True | Not a PAINS compound (no promiscuous interference) |
| `herg_safe` | True | Low risk of cardiac toxicity (hERG channel block) |
| `ames_safe` | True | Low mutagenicity risk |
| `novelty` | Tanimoto < 0.4 vs sotorasib | Structurally different from existing drugs |

## Scoring Tiers

| Tier | Docking Score | + Properties | What It Means |
|------|--------------|-------------|---------------|
| **Tier 1 — Hit** | < -7.0 | All pass | A legitimate starting point for medicinal chemistry |
| **Tier 2 — Lead** | < -8.5 | All pass + ADMET clean | Worth synthesizing and testing in vitro |
| **Tier 3 — Candidate** | < -10.0 | All pass + novel scaffold | Publication-worthy, potentially patentable |

For reference, known KRAS G12C inhibitors dock at -8 to -11 kcal/mol in this pocket. Scoring < -7 is the minimum bar. The goal is to find as many Tier 2+ molecules as possible with diverse scaffolds.

## The Experiment Loop

LOOP FOREVER:

1. **Generate molecules.** Use any strategy:
   - Start from known KRAS G12C inhibitor scaffolds and modify them
   - Fragment-based: combine drug-like fragments (BRICS decomposition)
   - Scaffold hopping: keep the pharmacophore, change the backbone
   - Random exploration: generate diverse SMILES and filter
   - Genetic algorithm: mutate and crossover top-scoring molecules
   - Use web search to find medicinal chemistry literature on KRAS G12C SAR

2. **Filter fast.** Before docking (which is slow), check:
   - Valid SMILES? (RDKit parse)
   - Passes Lipinski? (MW, LogP, HBD, HBA)
   - QED > 0.3? (loose pre-filter)
   - SA < 6? (loose pre-filter)
   - Not a PAINS hit?

3. **Dock survivors.** Run AutoDock Vina against `6OIM_receptor.pdbqt`.
   - `exhaustiveness=16` for real scoring, `exhaustiveness=8` for quick screening
   - Score < -7.0 kcal/mol = promising hit

4. **Full evaluation.** For molecules that dock well:
   - Compute all properties (QED, SA, Lipinski, TPSA, RotBonds)
   - Run ADMET prediction (hERG, AMES, solubility, metabolic stability)
   - Compute Tanimoto similarity to sotorasib — must be < 0.4 (novel)

5. **Log everything.** Every molecule evaluated goes in `molecules.json`. Hits go in `best_molecules.json`.

6. **Analyze and iterate.** After each batch:
   - What structural features correlate with good docking?
   - What functional groups appear in top hits?
   - Are there scaffold classes that consistently dock well?
   - Use this SAR (structure-activity relationship) to guide the next generation

7. **Never stop.** Keep generating, docking, and refining. The more diverse hits you find, the better.

## How to Evaluate Honestly

### Docking Score Sanity Checks
- **First, dock known drugs** as calibration: sotorasib SMILES = `C=CC(=O)N1CCN(CC1)c1c(F)ccc(NC2=NC=C(C(=O)N3CC(C)CC3=O)N2C2CCCCN2C(=O)C=C)c1F`. If it doesn't score < -8, your docking setup is wrong.
- **If a molecule scores < -12**, be skeptical. Run it again with higher exhaustiveness. Check if it's physically reasonable (not extending outside the pocket).
- **Large hydrophobic molecules always score well** — that doesn't make them drugs. Check QED and SA.
- **If everything scores > -5**, the binding site coordinates or box size may be wrong. Recalibrate.

### Property Sanity Checks
- **QED of aspirin = 0.55, QED of morphine = 0.38.** If your molecule has QED > 0.9, it's probably very simple (and boring). If < 0.2, it's probably not drug-like.
- **SA Score of aspirin = 1.6, complex natural products ~5-6.** Anything > 7 is practically unsynthesizable.
- **LogP > 5 means the molecule is too greasy.** It won't dissolve in blood. Some drugs break this rule, but it's a red flag.
- **MW > 500 is a warning.** Oral bioavailability drops sharply.

### Novelty Check
- Compute Morgan fingerprint (radius=2) Tanimoto similarity against sotorasib and adagrasib
- Similarity > 0.7 = you've basically rediscovered the same drug
- Similarity 0.4–0.7 = close analog, possibly patentable
- Similarity < 0.4 = genuinely novel scaffold

### What Goes in README.md

After every batch of molecules, update README with:

1. **Status banner** — total molecules evaluated, total hits, best docking score
2. **Top 10 molecules** — SMILES, docking score, QED, SA, novelty score
3. **SAR analysis** — what structural features make good binders? Show examples.
4. **Scaffold diversity** — how many distinct scaffolds did you find? Cluster them.
5. **Docking pose visualization** — describe or plot the binding mode of top hits
6. **Property distributions** — histograms of docking scores, QED, SA for all evaluated molecules
7. **Failure analysis** — what types of molecules consistently fail? Why?
8. **Strategy evolution** — how has your generation strategy changed based on results?
9. **Comparison to known drugs** — how do your best hits compare to sotorasib?

## Tools Available

All pre-installed:
- `rdkit` — molecular chemistry (SMILES, properties, fingerprints, BRICS)
- `vina` — molecular docking (AutoDock Vina Python bindings)
- `meeko` — SMILES → PDBQT conversion for docking
- `openbabel` — molecular format conversion, receptor preparation
- `admet-ai` — ADMET property prediction (toxicity, absorption, metabolism)
- `numpy`, `scipy`, `matplotlib` — numerics and plotting
- Web search — for KRAS G12C literature, SAR data, scaffold ideas

## Design Freedom

You choose everything:
- **Generation strategy:** genetic algorithm, fragment-based, scaffold hopping, random, RL, or any combination
- **Optimization algorithm:** evolutionary, Bayesian, greedy hill-climbing, or pure exploration
- **Batch size:** evaluate 1 molecule at a time or batch 100 then dock the best
- **Docking parameters:** exhaustiveness, box size, number of poses
- `pip install` anything else you need

Research freely: search for "KRAS G12C inhibitor SAR", "switch-II pocket pharmacophore", recent KRAS papers. Use what medicinal chemists have learned to guide your search.
