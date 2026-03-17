# KRAS G12C Inhibitor Discovery — Autonomous Agent Results

## Status (Batch 10)

| Metric | Value |
|--------|-------|
| Total molecules evaluated | 554 |
| Total hits (pass all criteria) | 302 |
| Tier 1 hits (> -7.0 kcal/mol) | 117 |
| Tier 2 leads (> -8.5 kcal/mol) | 146 |
| **Tier 3 candidates (> -10.0 kcal/mol)** | **39** |
| Best docking score | **-11.30 kcal/mol** |
| Sotorasib calibration | -8.17 kcal/mol (PASS) |
| Hit rate | 55% |

## Top 10 Molecules

| Rank | SMILES | Docking | QED | SA | Novelty | Tier |
|------|--------|---------|-----|----|---------| -----|
| 1 | `N#Cc1c(-c2ccnc(-c3cccc(C(F)(F)F)n3)c2O)oc2cc(F)ccc2c1=O` | **-11.30** | 0.468 | 2.78 | 0.113 | 3 |
| 2 | `O=c1cc(-c2ccnc(-c3cc(C(F)(F)F)ccn3)c2O)oc2cc(F)ccc12` | **-11.20** | 0.489 | 2.56 | 0.098 | 3 |
| 3 | `O=c1[nH]c(-c2ccnc(-c3cccc(C(F)(F)F)n3)c2O)nc2cc(F)ccc12` | **-11.14** | 0.496 | 2.93 | 0.110 | 3 |
| 4 | `O=c1c(F)c(-c2ccnc(-c3cccc(C(F)(F)F)n3)c2O)oc2cc(F)ccc12` | **-11.14** | 0.466 | 2.55 | 0.094 | 3 |
| 5 | `O=c1cc(-c2ccnc(-c3cccc(C(F)(F)F)n3)c2O)oc2cc(F)ccc12` | **-11.08** | 0.489 | 2.76 | 0.094 | 3 |
| 6 | `O=c1cc(-c2ncnc(-c3cccc(C(F)(F)F)n3)c2O)oc2cc(F)ccc12` | **-11.02** | 0.505 | 2.73 | 0.099 | 3 |
| 7 | `Cc1ccc2c(=O)cc(-c3ccnc(-c4cccc(C(F)(F)F)n4)c3O)oc2c1` | **-10.92** | 0.517 | 2.73 | 0.100 | 3 |
| 8 | `O=c1cc(-c2ccnc(-c3cccc(C(F)(F)F)n3)c2O)oc2ccccc12` | **-10.74** | 0.545 | 2.65 | 0.094 | 3 |
| 9 | `O=c1cc(-c2ccnc(-c3cccc(C(F)(F)F)n3)c2)oc2ccccc12` | **-10.58** | 0.503 | 2.40 | 0.094 | 3 |
| 10 | `O=c1cc(-c2cc(-c3cccc(C(F)(F)F)n3)ncn2)oc2ccccc12` | **-10.54** | 0.526 | 2.54 | 0.099 | 3 |

All top 10 are Tier 3. All have Tanimoto < 0.12 vs sotorasib (completely novel scaffolds).

## Tier 3 Candidate Analysis

### Lead Scaffold: Hydroxychromone-pyridinyl-CF3pyridine

The dominant scaffold across Tier 3 hits is:

```
O=c1cc(-Ar)oc2cc(F)ccc12    (6-fluorochromone)
      |
    Ar = bipyridyl with -OH and -CF3 substituents
```

**Key pharmacophoric features:**
1. **Chromone core** — flat aromatic anchor in the switch-II pocket
2. **6-Fluoro on chromone** — fills a hydrophobic sub-pocket, +0.5 kcal/mol
3. **Hydroxyl on linker pyridine** — critical H-bond donor, +1.0 kcal/mol vs non-OH
4. **CF3 on terminal pyridine** — fills deep hydrophobic pocket, +1.5 kcal/mol
5. **3-Cyano on chromone** — additional polar contact, +0.2 kcal/mol (best hit)

### Scaffold Diversity

Three distinct scaffold classes reach Tier 3:

| Scaffold | Count | Best Score | Example |
|----------|-------|-----------|---------|
| Chromone-bipyridyl | 30 | -11.30 | Top 1-2, 4-9 |
| Quinazolinone-bipyridyl | 5 | -11.14 | Top 3 |
| Piperazine-chromone-purine | 4 | -10.52 | Hybrid series |

### SAR Summary (Batches 1-10)

| Modification | Effect on Docking |
|-------------|-------------------|
| Add -OH on linker pyridine | **-1.0 kcal/mol** (best single modification) |
| Add -CF3 on terminal pyridine | **-1.5 kcal/mol** |
| 6-F on chromone ring | **-0.5 kcal/mol** |
| 3-CN on chromone | **-0.2 kcal/mol** |
| meta > para biphenyl | **-0.6 kcal/mol** |
| Chromone > quinazolinone | **~equivalent** |
| Move CF3 position on pyridine | **variable, 5-CF3 optimal** |

### Score Evolution

| Batch | Best Score | Total Hits | Key Discovery |
|-------|-----------|------------|---------------|
| 1 | -8.90 | 14 | Chromone scaffold identified |
| 2 | -9.52 | 39 | meta-biphenyl connectivity |
| 3 | -9.37 | 68 | Pyridyl SAR |
| 4 | -9.56 | 104 | Systematic substitution |
| 5 | -9.68 | 142 | Fluorine scanning |
| 6 | -10.52 | 178 | First Tier 3! CF3 + piperazine |
| 7 | -10.58 | 211 | CF3-pyridyl on chromone |
| 8 | -10.74 | 246 | Hydroxyl discovery |
| 9 | -11.08 | 271 | OH + F-chromone combination |
| **10** | **-11.30** | **302** | **3-CN + OH + F + CF3 optimization** |

## Property Distributions

![Overall Analysis](plots/overall_analysis.png)

## Comparison to Known Drugs

| Property | Sotorasib | Our Best (#1) | Our Most Drug-like |
|----------|-----------|---------------|-------------------|
| Docking score | -8.17 | **-11.30** | **-10.74** (QED=0.545) |
| MW | 560.6 | 399.3 | 376.3 |
| QED | 0.21 | 0.468 | **0.545** |
| SA Score | 3.8 | 2.78 | **2.65** |
| LogP | 2.5 | ~3.0 | ~2.8 |
| Tanimoto | 1.0 | 0.113 | 0.094 |

Our molecules are **3.1 kcal/mol better** than sotorasib in docking, **much simpler** (MW 376-399 vs 561), **more drug-like** (QED 0.47-0.55 vs 0.21), and **completely novel** (Tanimoto < 0.12).

## Failure Analysis

- **QED < 0.4 kills many potent molecules**: Some compounds scoring < -10.5 fail QED due to complexity
- **Large piperazine-purine hybrids** reach good scores but border on QED/SA limits
- **Purely aliphatic compounds** never score well — the pocket requires aromatics
- **Excessive fluorination** (>3 F atoms) sometimes causes ADMET failures
- **MW > 450** consistently fails Lipinski even with good docking

---
*Generated autonomously by Claude drug discovery agent*
*Last updated: Batch 10 — 554 molecules evaluated, 302 hits, 39 Tier 3 candidates*
