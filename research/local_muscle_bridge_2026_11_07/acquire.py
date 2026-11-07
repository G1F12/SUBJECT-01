"""Cycle 7 Data Acquisition and Source Audit Pipeline.
Performs reproducible public retrieval of metadata, paper full-text/supplements,
and repository records across Crossref, Europe PMC, OpenAlex, Zenodo, Figshare,
and institutional archives.
Policy: No credentials, raw data ignored in git, immutable metadata hashes recorded.
"""
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse
import json
import hashlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parents[1]
CACHE = REPO_ROOT / 'tmp/local_bridge_raw'

HEADERS = {
    'User-Agent': 'SUBJECT-01 Cycle 7 reproducibility audit (https://github.com/G1F12/SUBJECT-01)',
    'Accept': 'application/json, text/html, application/xml, */*'
}

def fetch_resource(label, url, method='GET', body=None):
    CACHE.mkdir(parents=True, exist_ok=True)
    out_file = CACHE / f"{label}.bin"
    req_data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=req_data, method=method, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
            status = resp.status
            content_type = resp.headers.get('Content-Type', '')
            sha256 = hashlib.sha256(data).hexdigest()
            out_file.write_bytes(data)
            return {
                'label': label,
                'url': url,
                'status': status,
                'bytes': len(data),
                'content_type': content_type,
                'sha256': sha256,
                'file': out_file.name,
                'obtained': True
            }
    except Exception as e:
        status_code = getattr(e, 'code', None)
        return {
            'label': label,
            'url': url,
            'status': status_code,
            'error': str(e),
            'obtained': False
        }

def build_job_list():
    quote = urllib.parse.quote
    jobs = [
        # Candidate 1: Moll et al. 2017 & Dissertation 2018
        ('moll_crossref', 'https://api.crossref.org/works/10.1002/nbm.3723', 'GET', None),
        ('moll_openalex', 'https://api.openalex.org/works/https://doi.org/10.1002/nbm.3723', 'GET', None),
        ('moll_europepmc', 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:28340292%20SRC:MED&format=json', 'GET', None),
        ('moll_dissertation_dbt', 'https://www.db-thueringen.de/receive/dbt_mods_00034407', 'GET', None),

        # Candidate 2: Cannon et al. 2014 & knee extension 31P-MRS + VO2
        ('cannon2014_crossref', 'https://api.crossref.org/works/10.1113/jphysiol.2014.279174', 'GET', None),
        ('cannon2014_pmc_xml', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4263658/fullTextXML', 'GET', None),
        ('cannon2014_pmc_supp', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4263658/supplementaryFiles', 'GET', None),
        ('cannon2013_crossref', 'https://api.crossref.org/works/10.1152/japplphysiol.00613.2013', 'GET', None),
        ('rossiter2002_crossref', 'https://api.crossref.org/works/10.1113/jphysiol.2001.013444', 'GET', None),
        ('layec2013_crossref', 'https://api.crossref.org/works/10.1152/japplphysiol.00445.2013', 'GET', None),

        # Candidate 3: Forbes et al. / Ryan et al. NIRS & 31P-MRS
        ('forbes2009_crossref', 'https://api.crossref.org/works/10.1152/japplphysiol.91525.2008', 'GET', None),
        ('ryan2014_crossref', 'https://api.crossref.org/works/10.1113/jphysiol.2013.265686', 'GET', None),

        # Candidate 4: Open Repositories
        ('zenodo_31p_mrs_exercise', 'https://zenodo.org/api/records?size=15&q=' + quote('31P-MRS exercise'), 'GET', None),
        ('zenodo_pcr_recovery', 'https://zenodo.org/api/records?size=15&q=' + quote('phosphocreatine recovery kinetics'), 'GET', None),
        ('figshare_31p_mrs', 'https://api.figshare.com/v2/articles/search', 'POST', {'search_for': '31P-MRS exercise', 'limit': 15}),
        ('figshare_pcr_kinetics', 'https://api.figshare.com/v2/articles/search', 'POST', {'search_for': 'phosphocreatine recovery kinetics', 'limit': 15}),
        ('osf_pcr_mrs', 'https://api.osf.io/v2/nodes/?filter[title]=phosphocreatine', 'GET', None),
        ('dryad_pcr_search', 'https://datadryad.org/api/v2/search?q=' + quote('phosphocreatine'), 'GET', None),
    ]
    return jobs

def audit_retrieved_files(records):
    inspected = {}
    for r in records:
        if not r.get('obtained'):
            continue
        bin_path = CACHE / r['file']
        text = bin_path.read_bytes().decode('utf-8', errors='replace')
        lbl = r['label']

        if lbl == 'moll_dissertation_dbt':
            # Look for pdf links, download links, metadata
            pdf_links = re.findall(r'href=[\'"]([^\'"]+?\.pdf[^\'"]*)[\'"]', text, re.IGNORECASE)
            servlet_links = re.findall(r'href=[\'"]([^\'"]*MCRFileNodeServlet[^\'"]*)[\'"]', text)
            inspected['moll_dissertation'] = {
                'pdf_links': pdf_links[:5],
                'servlet_links': servlet_links[:5],
                'has_download': 'MCRFileNodeServlet' in text or '.pdf' in text.lower()
            }

        elif lbl == 'cannon2014_pmc_xml':
            doi = re.findall(r'<article-id pub-id-type="doi">(.*?)</article-id>', text)
            supplements = re.findall(r'<supplementary-material[\s\S]*?</supplementary-material>', text)
            availability = re.findall(r'<sec[^>]*>[\s\S]{0,150}?<title>[^<]*[Dd]ata [Aa]vailability[\s\S]*?</sec>', text)
            tables = re.findall(r'<table-wrap[\s\S]*?</table-wrap>', text)
            inspected['cannon2014'] = {
                'doi': doi[0] if doi else None,
                'supplementary_count': len(supplements),
                'availability': availability[0] if availability else None,
                'table_count': len(tables),
                'has_numeric_tables': len(tables) > 0
            }

        elif lbl == 'cannon2014_pmc_supp':
            inspected['cannon2014_supp_json'] = json.loads(text) if text.strip().startswith('{') else text[:200]

        elif lbl.startswith('zenodo_'):
            try:
                zdata = json.loads(text)
                hits = zdata.get('hits', {}).get('hits', [])
                inspected[lbl] = [{
                    'id': h.get('id'),
                    'doi': h.get('doi'),
                    'title': h.get('metadata', {}).get('title'),
                    'files': [f.get('key') for f in h.get('files', [])]
                } for h in hits[:5]]
            except Exception as e:
                inspected[lbl] = str(e)

        elif lbl.startswith('figshare_'):
            try:
                fdata = json.loads(text)
                inspected[lbl] = [{
                    'id': item.get('id'),
                    'doi': item.get('doi'),
                    'title': item.get('title')
                } for item in (fdata if isinstance(fdata, list) else fdata.get('items', []))[:5]]
            except Exception as e:
                inspected[lbl] = str(e)

    return inspected

def main():
    print("=== Starting Cycle 7 Acquisition Pipeline ===")
    jobs = build_job_list()
    with ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(lambda j: fetch_resource(j[0], j[1], j[2], j[3]), jobs))

    inspected = audit_retrieved_files(records)
    summary = {
        'cycle': 7,
        'date': '2026-11-07',
        'jobs_total': len(jobs),
        'obtained_count': sum(1 for r in records if r.get('obtained')),
        'records': records,
        'inspected': inspected
    }

    out_json = BASE / 'retrieval.json'
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Acquisition complete. {summary['obtained_count']}/{summary['jobs_total']} jobs obtained.")
    print(f"Results written to: {out_json}")

if __name__ == '__main__':
    main()
