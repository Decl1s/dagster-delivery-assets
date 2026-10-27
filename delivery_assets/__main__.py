"""Я предоставляю короткие команды demo/generate/run/show/history."""
import argparse
import json
from pathlib import Path
from .domain import ContractError,fixture
from .storage import latest,prepare

def generate(folder,scenario):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    (folder/'deliveries.csv').write_bytes(fixture(scenario))
    return {'scenario':scenario,'rows':8 if scenario=='duplicate' else 7,'file':'deliveries.csv'}

def demo(root):
    from .pipeline import run,history
    root=Path(root)
    if root.exists():raise ContractError('DEMO_REQUIRES_NEW_DIRECTORY')
    root.mkdir(parents=True);work=root/'state';events=[]
    for scenario in ('valid','duplicate','revised'):generate(root/scenario,scenario)
    source=root/'valid/deliveries.csv'
    events.append(run(source,'2026-10-26',work));old=latest(work)
    events.append(run(source,'2026-10-26',work))
    events.append(run(root/'duplicate/deliveries.csv','2026-10-26',work))
    assert latest(work)==old
    events.append(run(root/'revised/deliveries.csv','2026-10-26',work,fail_before_pointer=True))
    assert latest(work)==old
    events.append(run(root/'revised/deliveries.csv','2026-10-26',work))
    assert [e['success'] for e in events]==[True,True,False,False,True]
    assert events[1]['publication']['reused_object'] and events[-1]['publication']['reused_object']
    return {'scenario':'quality-and-recovery','runs':events,'latest':latest(work),'history':history(work),'objects':len(list((work/'published/objects').glob('*.json')))}

def main():
    p=argparse.ArgumentParser(description='Я строю суточную витрину доставок через Dagster assets/checks')
    sub=p.add_subparsers(dest='command',required=True)
    generate_parser=sub.add_parser('generate');generate_parser.add_argument('--output',required=True,type=Path);generate_parser.add_argument('--scenario',choices=('valid','duplicate','chronology','revised'),default='valid')
    demo_parser=sub.add_parser('demo');demo_parser.add_argument('--directory',type=Path,default=Path('workspace/demo'))
    run_parser=sub.add_parser('run');run_parser.add_argument('--input',required=True,type=Path);run_parser.add_argument('--day',required=True);run_parser.add_argument('--simulate-publish-failure',action='store_true')
    for parser in (run_parser,sub.add_parser('show'),sub.add_parser('history')):parser.add_argument('--workdir',type=Path,default=Path('workspace/state'))
    a=p.parse_args()
    try:
        if a.command=='generate':value=generate(a.output,a.scenario)
        elif a.command=='demo':value=demo(a.directory)
        elif a.command=='run':
            from .pipeline import run
            value=run(a.input,a.day,a.workdir,fail_before_pointer=a.simulate_publish_failure)
        elif a.command=='show':value=latest(prepare(a.workdir))
        else:
            from .pipeline import history
            value=history(a.workdir)
        print(json.dumps(value,ensure_ascii=False,indent=2))
        return 2 if isinstance(value,dict) and value.get('success') is False else 0
    except (OSError,ValueError,AssertionError) as error:
        print(json.dumps({'success':False,'error':str(error) if isinstance(error,ContractError) else type(error).__name__},ensure_ascii=False));return 2

if __name__=='__main__':raise SystemExit(main())
