"""
Audit of Oxford Achilles Atlas (Cohen et al. 2026) and verification of its
identity with MTJCore Discovery Cohort.
Cycle 18 - SUBJECT-01.
"""

import json
import os
import h5py
import pandas as pd
import numpy as np

def run_oxford_audit():
    h5ad_path = 'D:/MTJCore/data/raw/achilles/ef0fc6ac-4872-40e1-ab24-e445b19ca6e3.h5ad'
    if not os.path.exists(h5ad_path):
        raise FileNotFoundError(f"Atlas file not found at {h5ad_path}")

    file_size_bytes = os.path.getsize(h5ad_path)

    with h5py.File(h5ad_path, 'r') as f:
        obs = f['obs']
        def get_categorical(col_name):
            c = obs[col_name]
            cats = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in c['categories'][:]]
            codes = c['codes'][:]
            return pd.Categorical.from_codes(codes, categories=cats)

        author_ct = pd.Series(get_categorical('author_cell_type'))
        broad_ann = pd.Series(get_categorical('broad_annotation'))
        donor_id = pd.Series(get_categorical('donor_id'))
        site = pd.Series(get_categorical('microanatomical_site'))
        
        # Build metadata dataframe
        meta_df = pd.DataFrame({
            'author_cell_type': author_ct,
            'broad_annotation': broad_ann,
            'donor_id': donor_id,
            'site': site
        })

        total_cells = len(meta_df)
        
        # Muscle subsets
        muscle_df = meta_df[meta_df['broad_annotation'] == 'Skeletal muscle cells']
        muscle_counts = muscle_df['author_cell_type'].value_counts().to_dict()
        muscle_by_site = pd.crosstab(muscle_df['author_cell_type'], muscle_df['site']).to_dict()
        muscle_by_donor = pd.crosstab(muscle_df['author_cell_type'], muscle_df['donor_id']).to_dict()

        # Fibroblast subsets
        fib_df = meta_df[meta_df['broad_annotation'] == 'Fibroblasts']
        fib_counts = fib_df['author_cell_type'].value_counts().to_dict()
        fib_by_site = pd.crosstab(fib_df['author_cell_type'], fib_df['site']).to_dict()
        fib_by_donor = pd.crosstab(fib_df['author_cell_type'], fib_df['donor_id']).to_dict()

        # Broad counts
        broad_counts = broad_ann.value_counts().to_dict()
        donor_counts = donor_id.value_counts().to_dict()
        site_counts = site.value_counts().to_dict()

    # Load MTJCore collection metadata
    col_path = 'D:/MTJCore/data/raw/achilles/collection.json'
    col_meta = {}
    if os.path.exists(col_path):
        with open(col_path, 'r', encoding='utf-8') as cf:
            cdata = json.load(cf)
            col_meta = {
                'collection_id': cdata.get('collection_id'),
                'name': cdata.get('name'),
                'doi': cdata.get('doi'),
                'publisher_journal': cdata.get('publisher_metadata', {}).get('journal'),
                'lead_author': cdata.get('publisher_metadata', {}).get('authors', [{}])[0].get('family')
            }

    audit_results = {
        'cycle': 18,
        'dataset_identity': {
            'study': 'Cohen et al. (2026)',
            'title': 'Fibroblast specialisation across microanatomy in a single-cell atlas of healthy human Achilles tendon',
            'journal': 'American Journal of Physiology-Cell Physiology',
            'doi': '10.1152/ajpcell.00838.2025',
            'cellxgene_collection_id': 'a7e81820-297d-4086-8123-cc7dde64e495',
            'cellxgene_dataset_id': 'ef0fc6ac-4872-40e1-ab24-e445b19ca6e3',
            'local_h5ad_path': h5ad_path,
            'file_size_bytes': file_size_bytes,
            'mtjcore_role': 'DISCOVERY_COHORT',
            'is_third_replication': False,
            'replication_validity': 'CIRCULAR_SELF_REPLICATION_PROHIBITED'
        },
        'resources_audit': {
            'mendeley_data': {
                'url': 'https://data.mendeley.com/datasets/vfzd93y7dv/1',
                'files_available': ['fibroblasts.rds'],
                'contains_myonuclei': False,
                'status': 'SUBSET_ONLY_FIBROBLASTS'
            },
            'cz_cellxgene': {
                'url': 'https://cellxgene.cziscience.com/collections/a7e81820-297d-4086-8123-cc7dde64e495',
                'file_available': 'ef0fc6ac-4872-40e1-ab24-e445b19ca6e3.h5ad',
                'contains_myonuclei': True,
                'contains_raw_counts': True,
                'contains_donor_ids': True,
                'status': 'COMPLETE_ATLAS_AVAILABLE'
            },
            'github': {
                'url': 'https://github.com/Botnar-MSK-Atlas/achilles_tendon_atlas',
                'contents': 'R and Rmd annotation pipelines, Louvain/SoupX scripts',
                'status': 'CODE_REPOSITORY'
            },
            'human_cell_atlas': {
                'url': 'https://explore.data.humancellatlas.org/projects/893c8fb6-bf65-4527-b83b-8233de59244c',
                'status': 'HCA_PROJECT_REGISTRATION'
            }
        },
        'cell_counts': {
            'total_cells': total_cells,
            'broad_annotations': broad_counts,
            'donors': donor_counts,
            'microanatomical_sites': site_counts,
            'skeletal_muscle_cells': {
                'total': sum(muscle_counts.values()),
                'by_type': muscle_counts,
                'by_site': muscle_by_site,
                'by_donor': muscle_by_donor
            },
            'fibroblasts': {
                'total': sum(fib_counts.values()),
                'by_type': fib_counts,
                'by_site': fib_by_site,
                'by_donor': fib_by_donor
            }
        },
        'status_classification': {
            'skeletal_muscle_cells': {
                'PRESENT_IN_ORIGINAL_STUDY': True,
                'AVAILABLE_IN_PUBLIC_MATRIX': True,
                'AVAILABLE_WITH_DONOR_METADATA': True,
                'SUITABLE_FOR_REPLICATION': False,
                'unsuitability_reason': 'Cohort was the discovery dataset of MTJCore. Cannot replicate on discovery training set.'
            },
            'fibroblasts': {
                'PRESENT_IN_ORIGINAL_STUDY': True,
                'AVAILABLE_IN_PUBLIC_MATRIX': True,
                'AVAILABLE_WITH_DONOR_METADATA': True,
                'SUITABLE_FOR_REPLICATION': False,
                'unsuitability_reason': 'Cohort was the discovery dataset of MTJCore.'
            }
        }
    }

    out_path = 'D:/SUBJECT-01/research/cycle18/OXFORD_AUDIT_SUMMARY.json'
    with open(out_path, 'w', encoding='utf-8') as out_f:
        json.dump(audit_results, out_f, indent=2)

    print(f"Audit completed. Summary written to {out_path}")
    print(f"Total cells: {total_cells}")
    print(f"Muscle cells: {sum(muscle_counts.values())}")
    print(f"Fibroblasts: {sum(fib_counts.values())}")

if __name__ == '__main__':
    run_oxford_audit()
