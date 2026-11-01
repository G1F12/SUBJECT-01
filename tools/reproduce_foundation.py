#!/usr/bin/env python3
"""Run Foundation source in isolated temp dir and compare all 7 CSV outputs."""
import csv, os, subprocess, sys, tempfile, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'research/foundation_2026_11_01/model.py'
NAMES=['muscle_force.csv','tendon_bottleneck.csv','sprint_energy.csv','heat_budget.csv','oxygen_fick.csv','reaction_budget.csv','diffusion_grid.csv']
def data(path):
    with path.open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))
with tempfile.TemporaryDirectory() as d:
    scratch=Path(d)
    shutil.copy2(MODEL,scratch/'model.py')
    env={**os.environ,'MPLBACKEND':'Agg','PYTHONDONTWRITEBYTECODE':'1'}
    run=subprocess.run([sys.executable,str(scratch/'model.py')],cwd=scratch,env=env,capture_output=True,text=True)
    if run.returncode:
        sys.exit('FAIL: model execution failed\n'+run.stdout+'\n'+run.stderr)
    for n in NAMES:
        original=data(MODEL.parent/n)
        regenerated=data(scratch/n)
        if original!=regenerated:sys.exit('FAIL: mismatch for '+n)
    print('PASS: foundation model standalone execution and 7 CSV datasets exactly reproduced')
    print('Model output first line:',run.stdout.splitlines()[0] if run.stdout else '(none)')
