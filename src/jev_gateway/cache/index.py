"""Single-writer, versioned FAISS cosine index and metadata mapping."""
import fcntl
import hashlib
import json
import math
import os
import uuid
from pathlib import Path


class IndexUnavailable(RuntimeError):
    pass


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FaissAnswerIndex:
    metric='cosine_via_normalized_inner_product'

    def __init__(self, root: Path, *, dimension: int, embedding_identity: str,
                 faiss_module=None, array_factory=None):
        if dimension < 1 or not embedding_identity:
            raise ValueError('dimension and embedding identity required')
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)
        self.dimension=dimension
        self.embedding_identity=embedding_identity
        if faiss_module is None:
            try:
                import faiss
                import numpy as np
            except ImportError as exc:
                raise IndexUnavailable('FAISS and NumPy optional dependencies unavailable') from exc
            faiss_module=faiss
            array_factory=lambda values:np.asarray(values,dtype='float32')
        self.faiss=faiss_module
        self.array_factory=array_factory or (lambda values:values)
        self.lock_file=(self.root/'owner.lock').open('a+b')
        try:
            fcntl.flock(self.lock_file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self.lock_file.close()
            raise IndexUnavailable('cache has another writer') from exc
        self.index=self.faiss.IndexFlatIP(dimension)
        self.entries=[]
        try:
            self.load()
        except BaseException:
            self.close()
            raise

    def close(self):
        fcntl.flock(self.lock_file.fileno(),fcntl.LOCK_UN)
        self.lock_file.close()

    def __enter__(self): return self
    def __exit__(self,*args): self.close()

    def _vector(self,vector):
        values=tuple(float(x) for x in vector)
        norm=math.sqrt(sum(x*x for x in values))
        if len(values)!=self.dimension or not all(math.isfinite(x) for x in values) or abs(norm-1)>1e-3:
            raise ValueError('index requires finite unit-length vectors of configured dimension')
        return values

    def load(self):
        pointer=self.root/'current.json'
        if not pointer.exists():
            return
        value=json.loads(pointer.read_text())
        generation=value['generation']
        if '/' in generation or generation.startswith('.'):
            raise IndexUnavailable('invalid index generation')
        folder=self.root/'versions'/generation
        metadata_path=folder/'metadata.json'; index_path=folder/'index.faiss'
        if _sha(metadata_path)!=value['metadata_sha256'] or _sha(index_path)!=value['index_sha256']:
            raise IndexUnavailable('cache index/metadata checksum mismatch')
        metadata=json.loads(metadata_path.read_text())
        if (metadata['dimension']!=self.dimension or metadata['embedding_identity']!=self.embedding_identity or
            metadata['metric']!=self.metric):
            raise IndexUnavailable('cache index embedding configuration mismatch')
        index=self.faiss.read_index(str(index_path))
        if index.d!=self.dimension or index.ntotal!=len(metadata['entries']):
            raise IndexUnavailable('cache index size or dimension mismatch')
        self.index=index
        self.entries=metadata['entries']

    def save(self,entries: list[dict],vectors):
        if len(entries)!=len(vectors) or len({entry['entry_id'] for entry in entries})!=len(entries):
            raise ValueError('one unique metadata entry per vector required')
        checked=[self._vector(v) for v in vectors]
        index=self.faiss.IndexFlatIP(self.dimension)
        if checked:
            index.add(self.array_factory(checked))
        generation=uuid.uuid4().hex
        folder=self.root/'versions'/generation
        folder.mkdir(parents=True,exist_ok=False)
        index_path=folder/'index.faiss'; metadata_path=folder/'metadata.json'
        self.faiss.write_index(index,str(index_path))
        metadata={'dimension':self.dimension,'embedding_identity':self.embedding_identity,
                  'metric':self.metric,'entries':entries}
        metadata_path.write_text(json.dumps(metadata,sort_keys=True))
        for path in (index_path,metadata_path):
            with path.open('rb') as durable: os.fsync(durable.fileno())
        directory_fd=os.open(folder,os.O_RDONLY)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
        pointer={'generation':generation,'index_sha256':_sha(index_path),
                 'metadata_sha256':_sha(metadata_path)}
        temp=self.root/f'.current-{generation}.json'
        temp.write_text(json.dumps(pointer,sort_keys=True))
        with temp.open('rb') as durable: os.fsync(durable.fileno())
        os.replace(temp,self.root/'current.json')
        directory_fd=os.open(self.root,os.O_RDONLY)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
        self.index=index
        self.entries=entries
        return generation

    def search(self,vector,*,k:int=5):
        if k<1: raise ValueError('positive k required')
        if not self.entries: return []
        query=self.array_factory([self._vector(vector)])
        scores,positions=self.index.search(query,min(k,len(self.entries)))
        return [(self.entries[int(pos)],float(score)) for pos,score in zip(positions[0],scores[0]) if pos>=0]
