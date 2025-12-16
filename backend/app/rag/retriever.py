from __future__ import annotations
import os
import glob
import pickle
from dataclasses import dataclass
from typing import List, Tuple, Dict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class Doc:
    doc_id: str
    title: str
    text: str

class TfidfRetriever:
    def __init__(self, vectorizer: TfidfVectorizer, docs: List[Doc], matrix):
        self.vectorizer = vectorizer
        self.docs = docs
        self.matrix = matrix

    @staticmethod
    def load_from_folder(folder: str) -> List[Doc]:
        docs: List[Doc] = []
        for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
            doc_id = os.path.basename(path)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            # first markdown header as title
            title = "Untitled"
            for line in text.splitlines():
                if line.strip().startswith("#"):
                    title = line.strip().lstrip("#").strip()
                    break
            docs.append(Doc(doc_id=doc_id, title=title, text=text))
        return docs

    @classmethod
    def build(cls, docs: List[Doc]) -> "TfidfRetriever":
        corpus = [d.text for d in docs]
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2), max_features=25000)
        matrix = vectorizer.fit_transform(corpus)
        return cls(vectorizer=vectorizer, docs=docs, matrix=matrix)

    def save(self, index_path: str, vectorizer_path: str) -> None:
        with open(index_path, "wb") as f:
            pickle.dump({"docs": self.docs, "matrix": self.matrix}, f)
        with open(vectorizer_path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    @classmethod
    def load(cls, index_path: str, vectorizer_path: str) -> "TfidfRetriever":
        with open(index_path, "rb") as f:
            blob = pickle.load(f)
        with open(vectorizer_path, "rb") as f:
            vectorizer = pickle.load(f)
        return cls(vectorizer=vectorizer, docs=blob["docs"], matrix=blob["matrix"])

    def search(self, query: str, top_k: int = 4) -> List[Tuple[Doc, float]]:
        if not query.strip():
            return []
        q = self.vectorizer.transform([query])
        sims = cosine_similarity(q, self.matrix).ravel()
        idxs = np.argsort(-sims)[:top_k]
        return [(self.docs[i], float(sims[i])) for i in idxs if sims[i] > 0]

    @staticmethod
    def make_snippet(text: str, max_len: int = 260) -> str:
        clean = " ".join(text.split())
        return clean[:max_len] + ("…" if len(clean) > max_len else "")
