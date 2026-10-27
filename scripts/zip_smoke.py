"""Я распаковываю поставку и запускаю приложение без исходного checkout и Git."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
from package_release import ROOT,NAME,archive

archive()
with tempfile.TemporaryDirectory(prefix='delivery-zip-') as tmp:
    folder=Path(tmp)
    with zipfile.ZipFile(ROOT/'artifacts'/NAME) as bundle:bundle.extractall(folder)
    result=subprocess.run([sys.executable,'-m','delivery_assets','demo','--directory','workspace/demo'],cwd=folder,capture_output=True,text=True,timeout=180)
    if result.returncode:raise AssertionError(result.stderr[-3000:])
    payload=json.loads(result.stdout)
    assert payload['objects']==2 and payload['latest']['totals']['due_count']==5
    print(json.dumps({'zip_round_trip':True,'objects':2,'due_count':5}))
