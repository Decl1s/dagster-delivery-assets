"""Я публикую immutable JSON объект и отдельный атомарный указатель latest."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from .domain import canonical,ContractError

MARKER='dagster-delivery-assets/v1\n'

def prepare(root):
    root=Path(root)
    if root.is_symlink():raise ContractError('WORKSPACE_SYMLINK')
    root.mkdir(parents=True,exist_ok=True,mode=0o700)
    marker=root/'.delivery-assets'
    if marker.is_symlink():raise ContractError('WORKSPACE_MARKER')
    if not marker.exists():
        if any(root.iterdir()):raise ContractError('UNOWNED_WORKSPACE')
        marker.write_text(MARKER,encoding='utf-8')
    if marker.read_text(encoding='utf-8')!=MARKER:raise ContractError('WORKSPACE_MARKER')
    for name in ('dagster','published','published/objects'):
        path=root/name
        if path.is_symlink():raise ContractError('WORKSPACE_SYMLINK')
        path.mkdir(exist_ok=True,mode=0o700)
    return root.resolve()

@contextmanager
def locked(root):
    # Я не пытаюсь угадать, что stale lock безопасно снять: после crash это ручной шаг.
    lock=root/'.run-lock'
    try:lock.mkdir()
    except FileExistsError:raise ContractError('WORKSPACE_BUSY') from None
    try:yield
    finally:lock.rmdir()

def write_temp(folder,raw):
    fd,name=tempfile.mkstemp(prefix='.new-',dir=folder)
    try:
        with os.fdopen(fd,'wb') as file:file.write(raw);file.flush();os.fsync(file.fileno())
        return Path(name)
    except BaseException:
        Path(name).unlink(missing_ok=True);raise

def publish(folder,report,fail_before_pointer=False):
    folder=Path(folder);raw=canonical(report);key=report['request_id'];digest=hashlib.sha256(raw).hexdigest()
    target=folder/'objects'/(key+'.json');temp=write_temp(target.parent,raw);reused=False
    try:
        try:os.link(temp,target)
        except FileExistsError:
            if target.is_symlink() or target.read_bytes()!=raw:raise ContractError('OBJECT_CONFLICT')
            reused=True
    finally:temp.unlink(missing_ok=True)
    if fail_before_pointer:raise ContractError('SIMULATED_POINTER_FAILURE')
    pointer=canonical({'request_id':key,'sha256':digest});latest=folder/'latest.json'
    if latest.is_symlink():raise ContractError('POINTER_SYMLINK')
    if not latest.exists() or latest.read_bytes()!=pointer:
        temp=write_temp(folder,pointer)
        try:os.replace(temp,latest)
        finally:temp.unlink(missing_ok=True)
    return {'request_id':key,'report_sha256':digest,'reused_object':reused,'totals':report['totals']}

def latest(root):
    folder=Path(root)/'published';pointer=folder/'latest.json'
    if pointer.is_symlink() or pointer.stat().st_size>1024:raise ContractError('POINTER_INVALID')
    try:ref=json.loads(pointer.read_text(encoding='utf-8'))
    except (ValueError,UnicodeError):raise ContractError('POINTER_INVALID') from None
    if not isinstance(ref,dict) or set(ref)!={'request_id','sha256'} or any(not isinstance(v,str) or not re.fullmatch('[a-f0-9]{64}',v) for v in ref.values()):raise ContractError('POINTER_INVALID')
    target=folder/'objects'/(ref['request_id']+'.json')
    if target.is_symlink() or target.stat().st_size>1_000_000:raise ContractError('OBJECT_INVALID')
    raw=target.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise ContractError('OBJECT_HASH_MISMATCH')
    try:report=json.loads(raw)
    except (ValueError,UnicodeError):raise ContractError('OBJECT_INVALID') from None
    if not isinstance(report,dict) or report.get('request_id')!=ref['request_id']:raise ContractError('OBJECT_IDENTITY')
    return report
