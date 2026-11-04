"""Run all historical and new suites; preserve locked files, record only command status."""
from pathlib import Path
import subprocess,sys,json,time
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
COMMANDS=[['tools/validate_repository.py'],['tools/reproduce_foundation.py'],['tools/audit_foundation.py'],
 ['research/integrated_2026_11_01/test_model.py'],['research/integrated_2026_11_01/experiments.py','--check'],
 ['-m','unittest','discover','-s','tests','-p','test_cpe45.py'],
 ['research/cpe45_2026_11_04/test_model.py'],['research/cpe45_2026_11_04/experiments.py','--check'],
 ['research/recovery_2026_11_04/test_recovery.py'],['research/recovery_2026_11_04/reproduce.py','--check'],
 ['research/observability_2026_11_04/test_observability.py'],
 ['research/observability_2026_11_04/inspect_data.py','--check'],
 ['research/observability_2026_11_04/audit.py','--check']]

def main():
    result=[]
    for args in COMMANDS:
        if '--historical' in sys.argv and args[0].startswith('research/observability'):continue
        start=time.monotonic();p=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True,encoding='utf8',errors='replace')
        item=dict(command='python '+' '.join(args),returncode=p.returncode,elapsed_s=round(time.monotonic()-start,2),tail=(p.stdout+p.stderr)[-1600:])
        result.append(item);print(item['command'],'PASS' if p.returncode==0 else 'FAIL',flush=True)
        if p.returncode:print(item['tail'],flush=True)
    target=BASE/('historical_verification.json' if '--historical' in sys.argv else 'verification.json')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    if any(r['returncode'] for r in result):raise SystemExit(1)

if __name__=='__main__':main()
