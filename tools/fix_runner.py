from pathlib import Path
p=Path('tools/tester.py');s=p.read_text();s=s.replace("out=ROOT/'evidence'/name;out.mkdir(parents=True,exist_ok=True)","check=subprocess.run(['pwsh','-NoProfile','-Command','if(Get-Process terminal64 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True)\n if check.returncode:raise RuntimeError('Close the active terminal before testing')\n out=ROOT/'evidence'/name;out.mkdir(parents=True,exist_ok=False)")
s=s.replace("p=subprocess.Popen([EXE", "common=pathlib.Path(r'C:\\Users\\ian\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files')\n for f in ['ChallengeAudit.csv','ChallengeStats.csv']:(common/f).unlink(missing_ok=True)\n p=subprocess.Popen([EXE")
s=s.replace("if not report.exists():raise RuntimeError", "if p.poll() is None:\n  p.terminate();raise TimeoutError('Tester exceeded 30 minutes')\n if not report.exists():raise RuntimeError")
p.write_text(s)
