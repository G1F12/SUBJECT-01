"""Candidate deep audit script for Cycle 7.
Fetches Kevin Moll dissertation PDF headers / metadata,
queries NCBI PMC API for PMC4263658,
and inspects Zenodo / Figshare datasets.
"""
from pathlib import Path
import urllib.request
import urllib.error
import json
import hashlib
import re

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parents[1]
CACHE = REPO_ROOT / 'tmp/local_bridge_raw'
CACHE.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'SUBJECT-01 Cycle 7 reproducibility audit (https://github.com/G1F12/SUBJECT-01)'
}

def fetch_file(label, url):
    out_file = CACHE / f"{label}.bin"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            out_file.write_bytes(data)
            return {
                'label': label,
                'url': url,
                'status': resp.status,
                'bytes': len(data),
                'sha256': hashlib.sha256(data).hexdigest(),
                'file': out_file.name,
                'success': True
            }
    except Exception as e:
        return {'label': label, 'url': url, 'error': str(e), 'success': False}

def main():
    print("=== Fetching Candidate 1 and Candidate 2 Deep Data ===")
    results = {}

    # 1. Kevin Moll Dissertation PDF
    moll_pdf_url = "https://www.db-thueringen.de/servlets/MCRFileNodeServlet/dbt_derivate_00040610/dissmoll.pdf"
    res_moll = fetch_file("moll_dissertation_pdf", moll_pdf_url)
    results['moll_dissertation_pdf'] = res_moll
    print("Moll dissertation fetch:", res_moll.get('status'), res_moll.get('bytes'), "bytes")

    # 2. Cannon 2014 from NCBI E-utilities
    ncbi_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=4263658&retmode=xml"
    res_cannon = fetch_file("cannon2014_ncbi_pmc_xml", ncbi_url)
    results['cannon2014_ncbi_pmc_xml'] = res_cannon
    print("Cannon NCBI PMC fetch:", res_cannon.get('status'), res_cannon.get('bytes'), "bytes")

    # Save summary
    out_path = BASE / 'candidate_deep_fetch.json'
    out_path.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print("Deep fetch summary written to:", out_path)

if __name__ == '__main__':
    main()
