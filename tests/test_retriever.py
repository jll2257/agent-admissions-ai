from backend.app.rag.retriever import TfidfRetriever

def test_build_and_search(tmp_path):
    docs = [
        TfidfRetriever.load_from_folder("data/docs")[0]
    ]
    r = TfidfRetriever.build(docs)
    hits = r.search("checklist", top_k=3)
    assert isinstance(hits, list)
