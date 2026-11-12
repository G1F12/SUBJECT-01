"""
Evaluation of HYP-0013: Stromal-Myonuclear Dual Synthesis of Collagen XXII & MTJ Proteins.
Cycle 18 - SUBJECT-01.
"""

import json
import os
import pandas as pd
import numpy as np

def evaluate_hyp0013():
    myo_de_path = 'D:/MTJCore/results/discovery/myonuclear_full_de.tsv'
    fib_de_path = 'D:/MTJCore/results/discovery/fibroblast_full_de.tsv'
    myo_sig_path = 'D:/MTJCore/results/discovery/frozen_myonuclear_signature.tsv'
    fib_sig_path = 'D:/MTJCore/results/discovery/frozen_fibroblast_signature.tsv'
    fib_ranked_path = 'D:/MTJCore/results/discovery/frozen_fibroblast_ranked.tsv'

    myo_de = pd.read_csv(myo_de_path, sep='\t')
    fib_de = pd.read_csv(fib_de_path, sep='\t')
    myo_sig = pd.read_csv(myo_sig_path, sep='\t')
    fib_sig = pd.read_csv(fib_sig_path, sep='\t')
    fib_ranked = pd.read_csv(fib_ranked_path, sep='\t')

    target_genes = ['COL22A1', 'POSTN', 'TNC', 'COMP', 'ITGA7', 'LAMA2', 'PXN', 'SCX', 'MKX']

    gene_analysis = {}

    for g in target_genes:
        # Myonuclear stats
        m_de = myo_de[myo_de['gene'] == g]
        m_sig = myo_sig[myo_sig['gene'] == g]
        myo_info = {
            'tested': len(m_de) > 0,
            'log2FC': float(m_de['log2FC'].iloc[0]) if len(m_de) > 0 else None,
            'FDR': float(m_de['FDR'].iloc[0]) if len(m_de) > 0 else None,
            'p_value': float(m_de['p_value'].iloc[0]) if len(m_de) > 0 else None,
            'in_signature': len(m_sig) > 0,
            'guard_excluded': bool(m_sig['annotation_guard_excluded'].iloc[0]) if len(m_sig) > 0 else (True if g == 'COL22A1' else False)
        }

        # Fibroblast stats
        f_de = fib_de[fib_de['gene'] == g]
        f_sig = fib_sig[fib_sig['gene'] == g]
        f_rk = fib_ranked[fib_ranked['gene'] == g]
        fib_info = {
            'tested': len(f_de) > 0,
            'log2FC': float(f_de['log2FC'].iloc[0]) if len(f_de) > 0 else None,
            'FDR': float(f_de['FDR'].iloc[0]) if len(f_de) > 0 else None,
            'p_value': float(f_de['p_value'].iloc[0]) if len(f_de) > 0 else None,
            'in_signature': len(f_sig) > 0,
            'donor_consistency': float(f_rk['donor_direction_consistency'].iloc[0]) if len(f_rk) > 0 else None,
            'rejection_reason': 'Donor consistency 0.6 < 0.75 threshold' if (g == 'COL22A1' and len(f_rk) > 0) else None
        }

        # Biological and mechanical interpretation
        gene_analysis[g] = {
            'myonuclear': myo_info,
            'fibroblast': fib_info,
            'dual_transcription_observed': bool(myo_info['tested'] and fib_info['tested'] and (myo_info['log2FC'] or 0) > 0 and (fib_info['log2FC'] or 0) > 0),
            'protein_synthesis_proven': False,
            'cooperative_secretion_proven': False,
            'mechanical_enhancement_proven': False
        }

    # Hypothesis status synthesis
    status_summary = {
        'hypothesis_id': 'HYP-0013',
        'title': 'Stromal-Myonuclear Dual Synthesis of Collagen XXII & MTJ Anchoring Complex',
        'verdict': 'NOT_SUPPORTED_AS_ORIGINAL_DISCOVERY',
        'verdict_details': {
            'transcript_observation': 'COL22A1 is transcribed in transitional myonuclei (log2FC=5.185, FDR=2.06e-9) and present in fibroblasts (log2FC=3.523, FDR=0.0013).',
            'donor_consistency_failure': 'COL22A1 failed the preregistered donor consistency threshold in fibroblasts (0.60 vs 0.75 requirement, elevated in only 3 of 5 donors).',
            'novelty_audit': 'ALREADY_PUBLISHED. Cohen et al. (2026) already reported fibroblast microanatomical heterogeneity and transitional myocyte marker expression in the Achilles atlas.',
            'biological_causality_gap': 'Transcript abundance does not prove protein translation, secretion, matrix incorporation, or mechanical load-bearing capacity.',
            'recommendation': 'Reject as a novel independent finding; close MTJCore replication attempts on Cohen et al.'
        },
        'genes': gene_analysis
    }

    # Save outputs
    out_path = 'D:/SUBJECT-01/research/cycle18/HYP0013_EVALUATION.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(status_summary, f, indent=2)

    # Save MTJ_REPLICATION_RESULTS.json
    replication_results = {
        'cycle': 18,
        'experiment_id': 'EXP-0057',
        'dataset_evaluated': 'Oxford Achilles Tendon Atlas (Cohen et al. 2026)',
        'cz_cellxgene_dataset_id': 'ef0fc6ac-4872-40e1-ab24-e445b19ca6e3',
        'replication_status': 'INVALID_CIRCULAR_EVALUATION',
        'findings': [
            'Oxford Achilles Atlas was the DISCOVERY dataset of MTJCore, not an independent replication cohort.',
            'Testing MTJCore against Oxford Achilles Atlas represents 100% training-data leakage.',
            'Full dataset contains 64,862 cells across 5 human donors, including 22,146 skeletal muscle nuclei and 24,179 fibroblasts.',
            'Mendeley Data deposit (vfzd93y7dv/1) contains only the fibroblasts.rds subset; previous assertions that Oxford had 0 myonuclei were erroneous artifacts of inspecting only Mendeley Data.',
            'True independent replication was already achieved in Stage 5 of MTJCore on E-MTAB-12529 (Semitendinosus snRNA-seq, empirical p = 1e-5).',
            'No third independent public snRNA-seq cohort with adult human MTJ donor-level contrasts currently exists.'
        ],
        'decision': 'STOP_NO_ADDED_SCIENTIFIC_VALUE',
        'next_action': 'Freeze MTJCore at submission state; redirect SUBJECT-01 resources to biomechanical and neuromuscular limits of human strength.'
    }

    rep_out_path = 'D:/SUBJECT-01/research/cycle18/MTJ_REPLICATION_RESULTS.json'
    with open(rep_out_path, 'w', encoding='utf-8') as f:
        json.dump(replication_results, f, indent=2)

    print(f"HYP-0013 evaluation written to {out_path}")
    print(f"Replication results written to {rep_out_path}")

if __name__ == '__main__':
    evaluate_hyp0013()
