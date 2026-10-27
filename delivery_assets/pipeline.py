"""Я исполняю три assets и две blocking checks в одном процессе, без daemon/Cloud."""
from pathlib import Path
import dagster as dg
from .domain import MAX_BYTES,parse_csv,parse_day,quality,summarize
from .storage import prepare,locked,publish

class Settings(dg.ConfigurableResource):
    source:str
    day:str
    published:str
    fail_before_pointer:bool=False

@dg.asset
def raw_deliveries(context:dg.AssetExecutionContext,settings:Settings):
    """Я замораживаю bytes одного выбранного CSV до любых вычислений."""
    with Path(settings.source).open('rb') as file:batch=parse_csv(file.read(MAX_BYTES+1))
    context.add_output_metadata({'rows':len(batch.rows),'source_sha256':batch.sha256})
    return batch

@dg.asset_check(asset=raw_deliveries,blocking=True)
def unique_delivery_ids(raw_deliveries):
    count=quality(raw_deliveries)['unique_delivery_ids']
    return dg.AssetCheckResult(passed=count==0,severity=dg.AssetCheckSeverity.ERROR,metadata={'duplicate_rows':count})

@dg.asset_check(asset=raw_deliveries,blocking=True)
def consistent_chronology(raw_deliveries):
    count=quality(raw_deliveries)['consistent_chronology']
    return dg.AssetCheckResult(passed=count==0,severity=dg.AssetCheckSeverity.ERROR,metadata={'invalid_rows':count})

@dg.asset
def delivery_summary(context:dg.AssetExecutionContext,raw_deliveries,settings:Settings):
    """Dagster не запускает эту функцию, пока обе blocking checks не пройдут."""
    report=summarize(raw_deliveries,settings.day)
    context.add_output_metadata({'due_count':report['totals']['due_count'],'request_id':report['request_id']})
    return report

@dg.asset
def published_report(context:dg.AssetExecutionContext,delivery_summary,settings:Settings):
    result=publish(settings.published,delivery_summary,settings.fail_before_pointer)
    context.add_output_metadata({'request_id':result['request_id'],'reused_object':result['reused_object']})
    return result

def instance(home):
    # Я не читаю глобальный DAGSTER_HOME; telemetry выключена в собственном instance.
    return dg.DagsterInstance.local_temp(str(home),overrides={'telemetry':{'enabled':False}})

def run(source,day,workdir,*,fail_before_pointer=False):
    parse_day(day);root=prepare(workdir)
    with locked(root),instance(root/'dagster') as state:
        result=dg.materialize([raw_deliveries,delivery_summary,published_report,unique_delivery_ids,consistent_chronology],resources={'settings':Settings(source=str(Path(source).resolve()),day=day,published=str(root/'published'),fail_before_pointer=fail_before_pointer),'io_manager':dg.mem_io_manager},instance=state,raise_on_error=False,tags={'delivery/day':day},run_config={'loggers':{'console':{'config':{'log_level':'ERROR'}}}})
        checks=[{'name':check.check_name,'passed':check.passed} for check in result.get_asset_check_evaluations()]
        summary={'run_id':result.run_id,'success':result.success,'checks':sorted(checks,key=lambda c:c['name']),'materialized':[event.asset_key.to_user_string() for event in result.get_asset_materialization_events()]}
        if result.success:summary['publication']=result.output_for_node('published_report')
        return summary

def history(workdir,limit=10):
    if not 1<=limit<=100:raise ValueError('HISTORY_LIMIT')
    root=prepare(workdir)
    with locked(root),instance(root/'dagster') as state:
        return [{'run_id':run.run_id,'status':run.status.value,'day':run.tags.get('delivery/day')} for run in state.get_runs(limit=limit)]
