from backend.app.rag.retriever import TfidfRetriever
from backend.app.config import settings

DOC_FOLDER = "data/columbia_docs"  # Columbia-only demo

def main():
    docs = TfidfRetriever.load_from_folder(DOC_FOLDER)
    if not docs:
        # Try to fetch the Columbia pages automatically (requires internet).
        try:
            from scripts.fetch_columbia_docs import fetch_all

            print(f"No docs found in {DOC_FOLDER}. Fetching Columbia sources...")
            fetch_all()
            docs = TfidfRetriever.load_from_folder(DOC_FOLDER)
        except Exception as e:
            raise SystemExit(
                f"No docs found in {DOC_FOLDER} and auto-fetch failed ({e}).\n"
                f"Run: python -m scripts.fetch_columbia_docs\n"
                f"Then: python -m scripts.build_index"
            )
    if not docs:
        raise SystemExit(f"No docs found in {DOC_FOLDER}")
    retriever = TfidfRetriever.build(docs)
    retriever.save(settings.rag_index_path, settings.rag_vectorizer_path)
    print(f"Built index over {len(docs)} docs -> {settings.rag_index_path}")

if __name__ == "__main__":
    main()
