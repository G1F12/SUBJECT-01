#!/usr/bin/env python3
"""Audit archive integrity and exact repeated numerical payloads, not clinical effects."""
import argparse
import collections
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SHA256 = '65098f741450024775bcb5bda73436d1f2144391f4be46f5a1e3149723f58f6b'
PATTERN = re.compile(r'^Dataset/subject(\d+)/(pre|post)(LF|RF)_(left|right)_(\d)(?:\.xlsx)?\.csv$')


def run(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    if h.hexdigest() != SHA256:
        raise ValueError('unexpected source hash')
    groups = collections.defaultdict(list)
    raw_hashes = collections.Counter()
    recognized = set()
    header_failures = 0
    header_details = collections.Counter()
    with zipfile.ZipFile(path) as archive:
        files = [i for i in archive.infolist() if not i.is_dir()]
        for item in files:
            match = PATTERN.fullmatch(item.filename)
            if not match:
                raise ValueError('unrecognized filename: '+item.filename)
            sid, phase, fatigue, hand, repeat = match.groups()
            key = (int(sid), phase, fatigue, hand, int(repeat))
            if key in recognized:
                raise ValueError('duplicate semantic trial key')
            recognized.add(key)
            contents = archive.read(item)
            raw_hashes[hashlib.sha256(contents).hexdigest()] += 1
            header1, header2, payload = contents.split(b'\n', 2)
            expected = b',Index,,,Thumb,,' if hand == 'left' else b',Thumb,,,Index,,'
            if header1.rstrip(b'\r') != expected or header2.rstrip(b'\r') != b'Time,X,Y,Z,X,Y,Z':
                header_failures += 1
                header_details[(hand, header1.rstrip(b'\r').decode('utf8','replace'), header2.rstrip(b'\r').decode('utf8','replace'))] += 1
            digest = hashlib.sha256(payload).hexdigest()
            groups[digest].append((key, item.filename))
        expected_keys = {(s,p,f,h,r) for s in range(1,17) for p in ('pre','post')
                         for f in ('LF','RF') for h in ('left','right') for r in (1,2,3)}
        if recognized != expected_keys:
            raise ValueError('incomplete trial grid')
        repeated = []
        for digest, members in sorted(groups.items(), key=lambda x:(-len(x[1]),x[0])):
            if len(members) < 2:
                continue
            keys = [k for k, _ in members]
            payload = archive.read(members[0][1]).split(b'\n',2)[2]
            a = np.loadtxt(io.BytesIO(payload), delimiter=',')
            if a.ndim != 2 or a.shape[1] != 7 or not np.isfinite(a).all():
                raise ValueError('invalid repeated-payload numeric data')
            dt = np.diff(a[:,0])
            repeated.append({'numeric_payload_sha256':digest,'trials':len(members),
                'participants':len({k[0] for k in keys}),
                'phases':dict(sorted(collections.Counter(k[1] for k in keys).items())),
                'hands':dict(sorted(collections.Counter(k[3] for k in keys).items())),
                'repetition_numbers':dict(sorted(collections.Counter(str(k[4]) for k in keys).items())),
                'rows':len(a),'time_start_s':float(a[0,0]),'time_end_s':float(a[-1,0]),
                'all_steps_1ms':bool(np.allclose(dt,0.001,atol=1e-7,rtol=0)),
                'max_abs_force_component_N':float(np.max(np.abs(a[:,1:]))),
                'force_rms_components_N':float(np.sqrt(np.mean(a[:,1:]**2)))})
    return {'archive_sha256':SHA256,'files':len(files),'expected_grid_complete':True,
            'header_mismatches':header_failures,'unique_complete_file_hashes':len(raw_hashes),
            'header_mismatch_patterns':[{'hand':hand,'header1':h1,'header2':h2,'count':count}
                                        for (hand,h1,h2),count in sorted(header_details.items())],
            'unique_numeric_payload_hashes':len(groups),'repeated_numeric_payload_groups':repeated,
            'limits':'Only repeated-payload representatives fully parsed. Non-duplicate signal quality, physical calibration, and true missingness are unverified.'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('archive',type=Path)
    args = ap.parse_args()
    result = run(args.archive)
    out = json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    (HERE/'PRECISION_GRIP_GATE_RESULTS.json').write_text(out,encoding='utf8',newline='\n')
    print(out)
