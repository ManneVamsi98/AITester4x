"""Langflow custom component: count the flaky test cases across two Playwright runs.

Paste this into a Langflow Custom Component node (or import the generated
`Flaky Analyzer.json` flow), point the two file inputs at `result1.json` and
`result2.json`, and run. The report lists the flaky tests and the per-run counts.

The counting logic is not duplicated here: it lives in `flaky_analyze.py` in this same
folder, and this component only adapts it to Langflow's input and output types. That
keeps the flow and the command line tool from ever disagreeing.

A test is flaky when its pass/fail status differs between the two runs. Tests that fail
in both runs are consistently failing, not flaky, and are reported separately.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from lfx.custom import Component
from lfx.io import FileInput, Output
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message

ANALYZER_DIR = Path(r"E:\AI Tester 4x\AI Tester 4x\Chapter_09_Langflow")


def _analyzer():
    """Import flaky_analyze.py from the chapter folder so there is one implementation."""
    if str(ANALYZER_DIR) not in sys.path:
        sys.path.insert(0, str(ANALYZER_DIR))
    try:
        import flaky_analyze
    except ImportError as exc:
        msg = f"Cannot import flaky_analyze.py from {ANALYZER_DIR}: {exc}"
        raise ValueError(msg) from exc
    return flaky_analyze


class FlakyAnalyzer(Component):
    display_name = "Flaky Test Analyzer"
    description = "Compare two Playwright JSON reports and count the flaky test cases."
    icon = "bug"

    inputs = [
        FileInput(
            name="result1",
            display_name="Run 1 report",
            file_types=["json"],
            required=True,
            info="result1.json from the first Playwright run (upload the file, or paste its path).",
        ),
        FileInput(
            name="result2",
            display_name="Run 2 report",
            file_types=["json"],
            required=True,
            info="result2.json from the second Playwright run (upload the file, or paste its path).",
        ),
    ]

    outputs = [
        Output(name="report", display_name="Report", method="analyze_report"),
        Output(name="flaky_tests", display_name="Flaky tests", method="analyze_table"),
    ]

    def _resolve(self, value: object, label: str) -> Path:
        """Accept a path, a list holding one, a Data/Message, or pasted JSON text."""
        if isinstance(value, (list, tuple)):
            if not value:
                raise ValueError(f"{label} is empty - point it at a Playwright JSON report.")
            return self._resolve(value[0], label)

        if not isinstance(value, str):
            if value is None:
                raise ValueError(f"{label}: no file provided - upload a Playwright JSON report.")
            for attribute in ("file_path", "path"):
                candidate = getattr(value, attribute, None)
                if isinstance(candidate, str) and candidate.strip():
                    return self._resolve(candidate, label)
            payload = getattr(value, "data", None)
            if isinstance(payload, dict):
                for key in ("file_path", "path", "text", "value"):
                    candidate = payload.get(key)
                    if isinstance(candidate, str) and candidate.strip():
                        return self._resolve(candidate, label)
            raise ValueError(f"{label} must be a file path or JSON text, got {type(value).__name__}.")

        text = value.strip()
        if not text:
            raise ValueError(f"{label} is empty - point it at a Playwright JSON report.")

        if text.startswith("{"):
            handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
            with handle:
                handle.write(text)
            return Path(handle.name)

        path = Path(text)
        if not path.is_file():
            raise ValueError(f"{label}: file not found: {path}")
        return path

    def _analysis(self) -> dict:
        """Run the shared analyzer over the two configured reports."""
        analyzer = _analyzer()
        try:
            return analyzer.analyze_paths(
                self._resolve(self.result1, "Run 1 report"),
                self._resolve(self.result2, "Run 2 report"),
            )
        except analyzer.InputError as exc:
            msg = f"Flaky analysis failed: {exc}"
            self.status = msg
            raise ValueError(msg) from exc

    def analyze_report(self) -> Message:
        """The summary, the flaky count, and the full markdown report."""
        analyzer = _analyzer()
        analysis = self._analysis()
        comparison = analysis["comparison"]
        summary = "\n".join(analyzer.summary_lines(analysis))
        report = analyzer.render_markdown(comparison, analysis["meta1"], analysis["meta2"])

        self.status = f"Flaky: {comparison['flaky_count']}"
        return Message(text=f"{summary}\n\n---\n\n{report}")

    def analyze_table(self) -> DataFrame:
        """The flaky tests as a table."""
        analysis = self._analysis()
        rows = [
            {
                "Test": entry["title_path"],
                "File": entry["file"],
                "Project": entry["project"],
                "Run 1": entry["run1"],
                "Run 2": entry["run2"],
                "Direction": entry["direction"],
            }
            for entry in analysis["comparison"]["flaky"]
        ]
        return DataFrame(data=rows)
