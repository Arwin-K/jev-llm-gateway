import json
import math
from pathlib import Path
from jev_gateway.cache.index import FaissAnswerIndex


class FakeIndex:
    def __init__(self,d): self.d=d; self.vectors=[]
    @property
    def ntotal(self): return len(self.vectors)
    def add(self,vectors): self.vectors.extend(vectors)
    def reconstruct(self,i): return self.vectors[i]
    def search(self,queries,k):
        scores=[sum(a*b for a,b in zip(queries[0],v)) for v in self.vectors]
        order=sorted(range(len(scores)),key=lambda i:-scores[i])[:k]
        return [[scores[i] for i in order]],[order]


class FakeFaiss:
    IndexFlatIP=FakeIndex
    def write_index(self,index,path): Path(path).write_text(json.dumps({'d':index.d,'vectors':index.vectors}))
    def read_index(self,path):
        data=json.loads(Path(path).read_text()); index=FakeIndex(data['d']); index.add(data['vectors']); return index


def test_versioned_save_reload_and_search(tmp_path):
    with FaissAnswerIndex(tmp_path,dimension=2,embedding_identity='model@rev',faiss_module=FakeFaiss()) as store:
        assert store.search([1,0])==[]
        store.save([{'entry_id':'one','answer':'a'}],[[1.,0.]])
        assert store.search([1.,0.])[0][0]['entry_id']=='one'
    with FaissAnswerIndex(tmp_path,dimension=2,embedding_identity='model@rev',faiss_module=FakeFaiss()) as restored:
        assert restored.search([1.,0.])[0][1]==1.
