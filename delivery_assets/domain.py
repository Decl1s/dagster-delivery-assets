"""Я держу контракт CSV и расчёт отдельно от оркестратора и filesystem."""
import csv
from dataclasses import dataclass
from datetime import date,datetime,timedelta,timezone
import hashlib
import io
import json
import re

ENGINE='delivery-summary-v1'
FIELDS=('delivery_id','warehouse','created_at','promised_at','delivered_at')
MAX_BYTES=1_000_000
MAX_ROWS=10_000

class ContractError(ValueError):pass

@dataclass(frozen=True)
class Delivery:
    delivery_id:str
    warehouse:str
    created_at:datetime
    promised_at:datetime
    delivered_at:datetime|None

@dataclass(frozen=True)
class Batch:
    rows:tuple[Delivery,...]
    sha256:str

def canonical(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')

def parse_day(value):
    try:result=date.fromisoformat(value)
    except (ValueError,TypeError):raise ContractError('DAY_FORMAT') from None
    if result.isoformat()!=value or not 2020<=result.year<=2099:raise ContractError('DAY_RANGE')
    return result

def timestamp(value):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',value):raise ContractError('UTC_TIMESTAMP')
    try:result=datetime.fromisoformat(value[:-1]+'+00:00')
    except ValueError:raise ContractError('UTC_TIMESTAMP') from None
    if not 2020<=result.year<=2099:raise ContractError('UTC_TIMESTAMP_RANGE')
    return result

def parse_csv(raw):
    if len(raw)>MAX_BYTES:raise ContractError('INPUT_TOO_LARGE')
    try:
        reader=csv.DictReader(io.StringIO(raw.decode('utf-8'),newline=''),strict=True)
        if tuple(reader.fieldnames or ())!=FIELDS:raise ContractError('CSV_HEADER')
        rows=[]
        for index,row in enumerate(reader,1):
            if index>MAX_ROWS:raise ContractError('TOO_MANY_ROWS')
            if set(row)!=set(FIELDS) or any(value is None for value in row.values()):raise ContractError('CSV_COLUMNS')
            if not re.fullmatch(r'D[0-9]{3,8}',row['delivery_id']):raise ContractError('DELIVERY_ID')
            if row['warehouse'] not in ('WH-A','WH-B'):raise ContractError('WAREHOUSE')
            rows.append(Delivery(row['delivery_id'],row['warehouse'],timestamp(row['created_at']),timestamp(row['promised_at']),timestamp(row['delivered_at']) if row['delivered_at'] else None))
    except (UnicodeError,csv.Error):raise ContractError('CSV_ENCODING_OR_SYNTAX') from None
    return Batch(tuple(rows),hashlib.sha256(raw).hexdigest())

def quality(batch):
    # Я считаю разные свойства отдельно: Dagster покажет, какое условие нарушено.
    duplicate_count=len(batch.rows)-len({row.delivery_id for row in batch.rows})
    chronology_count=sum(row.created_at>row.promised_at or (row.delivered_at is not None and row.delivered_at<row.created_at) for row in batch.rows)
    return {'unique_delivery_ids':duplicate_count,'consistent_chronology':chronology_count}

def summarize(batch,day):
    selected=parse_day(day);cutoff=datetime.combine(selected+timedelta(days=1),datetime.min.time(),tzinfo=timezone.utc)
    identity=hashlib.sha256(canonical({'engine':ENGINE,'day':day,'source_sha256':batch.sha256})).hexdigest()
    groups={}
    for row in batch.rows:
        if row.promised_at.date()!=selected:continue
        counters=groups.setdefault(row.warehouse,{'warehouse':row.warehouse,'due_count':0,'on_time':0,'late':0,'overdue':0,'max_known_late_seconds':0})
        counters['due_count']+=1
        if row.delivered_at is None or row.delivered_at>=cutoff:counters['overdue']+=1
        elif row.delivered_at<=row.promised_at:counters['on_time']+=1
        else:
            counters['late']+=1
            counters['max_known_late_seconds']=max(counters['max_known_late_seconds'],int((row.delivered_at-row.promised_at).total_seconds()))
    warehouses=[groups[key] for key in sorted(groups)]
    totals={key:sum(g[key] for g in warehouses) for key in ('due_count','on_time','late','overdue')}
    return {'engine':ENGINE,'request_id':identity,'day':day,'as_of_exclusive':cutoff.isoformat().replace('+00:00','Z'),'source_sha256':batch.sha256,'source_rows':len(batch.rows),'warehouses':warehouses,'totals':totals}

def fixture(scenario='valid'):
    rows=[
      ['D001','WH-A','2026-10-26T07:00:00Z','2026-10-26T09:00:00Z','2026-10-26T08:59:00Z'],
      ['D002','WH-A','2026-10-26T07:00:00Z','2026-10-26T10:00:00Z','2026-10-26T10:20:00Z'],
      ['D003','WH-A','2026-10-26T07:00:00Z','2026-10-26T11:00:00Z',''],
      ['D004','WH-B','2026-10-26T07:00:00Z','2026-10-26T12:00:00Z','2026-10-26T12:00:00Z'],
      ['D005','WH-B','2026-10-26T07:00:00Z','2026-10-26T13:00:00Z','2026-10-27T00:10:00Z'],
      ['D006','WH-B','2026-10-26T07:00:00Z','2026-10-27T09:00:00Z',''],
      ['D007','WH-A','2026-10-25T07:00:00Z','2026-10-25T09:00:00Z','2026-10-25T09:15:00Z'],
    ]
    if scenario=='duplicate':rows.append(rows[0].copy())
    elif scenario=='chronology':rows[0][4]='2026-10-26T06:59:00Z'
    elif scenario=='revised':rows[1][4]='2026-10-26T10:05:00Z'
    elif scenario!='valid':raise ContractError('SCENARIO')
    stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\n');writer.writerow(FIELDS);writer.writerows(rows)
    return stream.getvalue().encode('utf-8')
