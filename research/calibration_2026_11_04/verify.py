"""Full repository checks, preserving every historical verification artifact."""
import subprocess,sys,json,time,os
from acquire import BASE,save

def main():
    commands=[r['command'].replace(' --check',' --check-offline') if 'inspect_data.py' in r['command'] else r['command']
              for r in json.loads((BASE/'historical_verification.json').read_text('utf8'))]
    commands += ['python -m unittest discover -s research/calibration_2026_11_04 -p test_calibration.py',
                 'python research/calibration_2026_11_04/reproduce.py','git diff --check']
    results=[];env=dict(os.environ,PYTHONIOENCODING='utf-8')
    for cmd in commands:
        start=time.monotonic();p=subprocess.run(cmd.split(),cwd=BASE.parents[1],capture_output=True,env=env)
        tail=(p.stdout+p.stderr).decode('utf8',errors='replace')[-3500:]
        results.append(dict(command=cmd,returncode=p.returncode,elapsed_s=round(time.monotonic()-start,2),tail=tail))
        print(p.returncode,cmd,flush=True)
    save(BASE/'verification.json',results)
    return int(any(r['returncode'] for r in results))

if __name__=='__main__':sys.exit(main())
