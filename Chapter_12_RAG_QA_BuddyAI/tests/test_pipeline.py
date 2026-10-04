"""Dependency-free tests for the pure pipeline logic.

Run:  python -m unittest discover -s tests -v
(No torch / qdrant / streamlit required.)
"""

from __future__ import annotations

import dataclasses
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qabuddy import chunking, qdrant_store, rag  # noqa: E402
from qabuddy.config import Settings  # noqa: E402
from qabuddy.embeddings import HashEmbedder  # noqa: E402
from qabuddy.ingest import ALL_KEYS, PHASE_2, SOURCES, testcases  # noqa: E402
from qabuddy.ingest.jira import adf_to_text  # noqa: E402
from qabuddy.retrieval import Retrieved  # noqa: E402
from qabuddy.sparse import LexicalSparseEncoder, hash_token  # noqa: E402


class ChunkingTests(unittest.TestCase):
    def test_long_text_splits(self):
        text = "\n\n".join(f"Paragraph {i} " + ("word " * 80) for i in range(20))
        chunks = chunking.chunk_text(text, max_tokens=100, overlap=0.15)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 100 * 4 + 200)

    def test_empty_text(self):
        self.assertEqual(chunking.chunk_text("   \n  "), [])

    def test_log_strips_ansi(self):
        chunks = chunking.chunk_log("\x1b[31mERROR\x1b[0m boom")
        self.assertTrue(chunks)
        self.assertNotIn("\x1b", chunks[0])


class SparseTests(unittest.TestCase):
    def test_deterministic_and_ids_kept(self):
        encoder = LexicalSparseEncoder()
        first = encoder.encode("WING-LOGIN-TC-089 authentication server error")
        second = encoder.encode("WING-LOGIN-TC-089 authentication server error")
        self.assertEqual(first.indices, second.indices)
        self.assertIn(hash_token("WING-LOGIN-TC-089"), first.indices)

    def test_different_text_differs(self):
        encoder = LexicalSparseEncoder()
        self.assertNotEqual(encoder.encode("alpha beta").indices, encoder.encode("gamma delta").indices)


class EmbedderTests(unittest.TestCase):
    def test_hash_embedder(self):
        embedder = HashEmbedder(dim=128)
        dense, sparse = embedder.embed_query("login test")
        self.assertEqual(embedder.dim, 128)
        self.assertEqual(len(dense), 128)
        self.assertTrue(sparse.indices)
        self.assertEqual(embedder.embed_query("login test")[0], dense)


class TestCaseIngestTests(unittest.TestCase):
    def test_rows_become_unique_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data" / "03_test_cases"
            data.mkdir(parents=True)
            (data / "t.csv").write_text(
                "Test Case ID,Summary,Priority,Test Steps\n"
                'WING-LOGIN-TC-001,Login works,High,"1. open\n2. submit"\n'
                "WING-LOGIN-TC-002,Enter submits,Medium,press enter\n",
                encoding="utf-8",
            )
            settings = dataclasses.replace(
                Settings.load(), root=root, data_dir=root / "data", output_dir=root / "output"
            )
            docs = testcases.load(settings, "03_test_cases")
            self.assertEqual(len(docs), 2)
            self.assertEqual(
                {d["metadata"]["tc_id"] for d in docs},
                {"WING-LOGIN-TC-001", "WING-LOGIN-TC-002"},
            )
            keys = [d["point_key"] for d in docs]
            self.assertEqual(len(keys), len(set(keys)))
            self.assertIn("WING-LOGIN-TC-002", docs[1]["text"])


    def test_alternate_headers_are_aliased(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data" / "03_test_cases"
            data.mkdir(parents=True)
            (data / "vwo.csv").write_text(
                "Scenario TID,TestCase Description,Priority,Status,Is Automated\n"
                "LOGIN-001,Verify Login - page load,Critical,Not Executed,Yes\n",
                encoding="utf-8",
            )
            settings = dataclasses.replace(
                Settings.load(), root=root, data_dir=root / "data", output_dir=root / "output"
            )
            docs = testcases.load(settings, "03_test_cases")
            self.assertEqual(len(docs), 1)
            meta = docs[0]["metadata"]
            self.assertEqual(meta["tc_id"], "LOGIN-001")
            self.assertEqual(meta["summary"], "Verify Login - page load")
            self.assertEqual(meta["priority"], "Critical")
            self.assertEqual(meta["is_automated"], "Yes")


class JiraTests(unittest.TestCase):
    def test_adf_flatten(self):
        adf = {
            "type": "doc",
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Login fails"}]}],
        }
        self.assertIn("Login fails", adf_to_text(adf))
        self.assertEqual(adf_to_text("plain"), "plain")


class RagTests(unittest.TestCase):
    def test_context_labels_include_citation_id(self):
        contexts = [Retrieved("body text", {"source_file": "t.csv", "tc_id": "WING-LOGIN-TC-002"}, 0.5)]
        built = rag.build_context(contexts)
        self.assertIn("[1]", built)
        self.assertIn("WING-LOGIN-TC-002", built)

    def test_no_evidence(self):
        self.assertEqual(rag.NO_EVIDENCE, "Insufficient evidence in the knowledge base.")


class StoreTests(unittest.TestCase):
    def test_point_ids_are_deterministic(self):
        self.assertEqual(qdrant_store.make_point_id("a:b"), qdrant_store.make_point_id("a:b"))
        self.assertNotEqual(qdrant_store.make_point_id("a:b"), qdrant_store.make_point_id("a:c"))


class RegistryTests(unittest.TestCase):
    def test_every_source_folder_exists(self):
        base = Settings.load().data_dir
        for key in ALL_KEYS:
            folder = SOURCES[key][0]
            self.assertTrue((base / folder).is_dir(), f"missing {folder} for {key}")

    def test_phase2_is_not_ingested(self):
        for key in PHASE_2:
            self.assertNotIn(key, ALL_KEYS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
