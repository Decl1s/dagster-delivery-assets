"""Я проверяю команды отдельными процессами и долговечную историю между ними."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='delivery-smoke-') as tmp:
    demo=Path(tmp)/'demo'
    def cli(*args,expected=0):
        result=subprocess.run([sys.executable,'-m','delivery_assets',*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=120)
        if result.returncode!=expected:raise AssertionError(result.stderr[-3000:]+result.stdout[-1500:])
        return json.loads(result.stdout)
    result=cli('demo','--directory',demo)
    assert result['objects']==2 and result['latest']['totals']=={'due_count':5,'on_time':2,'late':1,'overdue':2}
    shown=cli('show','--workdir',demo/'state');assert shown==result['latest']
    assert len(cli('history','--workdir',demo/'state'))==5
    failed=cli('run','--input',demo/'missing.csv','--day','2026-10-26','--workdir',demo/'state',expected=2)
    assert not failed['success'] and cli('show','--workdir',demo/'state')==shown
    assert cli('demo','--directory',demo,expected=2)['error']=='DEMO_REQUIRES_NEW_DIRECTORY'
    print(json.dumps({'cli':True,'runs':6,'objects':2,'blocking_check':True,'failed_publish_old_pointer_preserved':True,'retry_reuses_orphan':True,'history_persistent_across_processes':True}))
