"""One immutable JSON file per compatible completed tier call, atomically replaced."""
import hashlib
import json
import os
import tempfile
from pathlib import Path

from .records import Result


def key(prompt, tier, backend, settings_fingerprint):
    value={'prompt_id':prompt.prompt_id,'prompt_sha256':hashlib.sha256(prompt.prompt.encode()).hexdigest(),'dataset_revision':prompt.dataset_revision,'source_revision':prompt.source_revision,'template_fingerprint':prompt.template_fingerprint,'tier':tier,'backend':backend.base_url,'model':backend.model,'settings_fingerprint':settings_fingerprint}
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


class Checkpoints:
    def __init__(self, directory: Path):
        self.directory=directory
        directory.mkdir(parents=True,exist_ok=True)

    def get(self, key_value, configured_model, execution='real'):
        path=self.directory/(key_value+'.json')
        if not path.exists(): return None
        result=Result.model_validate_json(path.read_text())
        if result.model != configured_model or result.execution != execution:
            return None
        if result.outcome in {'backend_error','blocked','evaluator_error'}:
            return None
        return result.model_copy(update={'reuse_of':result.run_id})

    def put(self, key_value, result):
        path=self.directory/(key_value+'.json')
        if path.exists():
            old=Result.model_validate_json(path.read_text())
            if old != result:
                raise FileExistsError('immutable checkpoint already exists')
            return
        with tempfile.NamedTemporaryFile('w',dir=self.directory,prefix='.partial-',delete=False) as stream:
            temp=Path(stream.name)
            stream.write(result.model_dump_json()+'\n')
            stream.flush(); os.fsync(stream.fileno())
        try:
            os.replace(temp,path)
        finally:
            temp.unlink(missing_ok=True)
