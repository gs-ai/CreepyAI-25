"""Dialog for displaying local LLM analysis results inside CreepyAI-25."""

from __future__ import annotations

import json
import html
from typing import Dict, List, Optional, Sequence

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
)

from app.analysis import AnalysisHistoryEntry


class LLMAnalysisDialog(QDialog):
    """Review the latest and historical local LLM insights."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Local LLM Analysis Results")
        self.resize(780, 640)

        layout = QVBoxLayout(self)

        self.intro_label = QLabel(
            "Review the most recent local LLM analysis and switch between prior "
            "runs that were stored with integrity hashes."
        )
        self.intro_label.setWordWrap(True)
        layout.addWidget(self.intro_label)

        selector_row = QHBoxLayout()
        selector_label = QLabel("Select run:")
        self.history_selector = QComboBox()
        self.history_selector.currentIndexChanged.connect(self._on_selection_changed)
        selector_row.addWidget(selector_label)
        selector_row.addWidget(self.history_selector, 1)
        layout.addLayout(selector_row)

        self.integrity_label = QLabel()
        layout.addWidget(self.integrity_label)

        self.tabs = QTabWidget()
        self.summary_view = QTextBrowser()
        self.summary_view.setOpenExternalLinks(True)
        self.summary_view.setObjectName("analysisSummaryView")
        self.tabs.addTab(self.summary_view, "Summary")

        self.raw_view = QPlainTextEdit()
        self.raw_view.setReadOnly(True)
        self.raw_view.setObjectName("analysisRawView")
        self.tabs.addTab(self.raw_view, "Raw JSON")
        layout.addWidget(self.tabs, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self._entries: List[Dict[str, object]] = []

    def set_analysis_results(
        self,
        current_payload: Dict[str, object],
        history_entries: Sequence[AnalysisHistoryEntry],
        saved_entry: Optional[AnalysisHistoryEntry] = None,
    ) -> None:
        """Populate the dialog with the current payload and historical runs."""

        self._entries = []
        seen_paths = set()

        latest_payload = json.loads(json.dumps(current_payload))
        if saved_entry is not None:
            label = f"{saved_entry.label()} (latest)"
            path = str(saved_entry.file_path)
            integrity = saved_entry.integrity
            seen_paths.add(path)
        else:
            generated_at = latest_payload.get("generated_at") or "current"
            subject = latest_payload.get("subject") or "analysis"
            label = f"{generated_at} | {subject} (unsaved)"
            path = str(latest_payload.get("history_path") or "")
            integrity = str(latest_payload.get("integrity") or "unsaved")
            if path:
                seen_paths.add(path)

        self._entries.append(
            {
                "label": label,
                "payload": latest_payload,
                "integrity": integrity,
                "path": path,
            }
        )

        for entry in history_entries:
            entry_path = str(entry.file_path)
            if entry_path in seen_paths:
                continue
            self._entries.append(
                {
                    "label": entry.label(),
                    "payload": entry.payload,
                    "integrity": entry.integrity,
                    "path": entry_path,
                }
            )
            seen_paths.add(entry_path)

        self.history_selector.blockSignals(True)
        self.history_selector.clear()
        for item in self._entries:
            self.history_selector.addItem(item["label"])
        self.history_selector.blockSignals(False)

        if self._entries:
            self.history_selector.setCurrentIndex(0)
            self._update_views(0)
        else:
            self.summary_view.clear()
            self.raw_view.clear()
            self.integrity_label.setText("No analysis runs available.")

    def _on_selection_changed(self, index: int) -> None:
        if 0 <= index < len(self._entries):
            self._update_views(index)

    def _update_views(self, index: int) -> None:
        entry = self._entries[index]
        payload = entry["payload"]
        integrity = entry.get("integrity") or ""
        path = entry.get("path") or ""

        details = f"<strong>Integrity:</strong> {html.escape(str(integrity))}"
        if path:
            details += f" | <strong>Stored at:</strong> {html.escape(path)}"
        self.integrity_label.setText(details)

        self.summary_view.setHtml(self._build_summary_html(payload))
        self.raw_view.setPlainText(json.dumps(payload, indent=2))
        self.tabs.setCurrentIndex(0)

    def _build_summary_html(self, payload: Dict[str, object]) -> str:
        subject = html.escape(str(payload.get("subject") or "Unknown"))
        focus = payload.get("focus")
        generated = html.escape(str(payload.get("generated_at") or ""))
        records_analyzed = payload.get("records_analyzed", 0)

        parts: List[str] = [f"<h3>{subject}</h3>"]
        if focus:
            parts.append(f"<p><strong>Focus:</strong> {html.escape(str(focus))}</p>")
        if generated:
            parts.append(f"<p><strong>Generated:</strong> {generated}</p>")
        parts.append(f"<p><strong>Records analysed:</strong> {records_analyzed}</p>")

        model_outputs = payload.get("model_outputs", [])
        if isinstance(model_outputs, list):
            rows = []
            for item in model_outputs:
                model_name = html.escape(str(item.get("model") or "model"))
                if item.get("error"):
                    status = html.escape(str(item.get("error")))
                elif item.get("parsed") is not None:
                    status = "parsed JSON"
                else:
                    status = "raw text"
                tone = html.escape(str(item.get("tone") or ""))
                depth = html.escape(str(item.get("depth") or ""))
                rows.append(
                    f"<li><strong>{model_name}</strong>: {status}" +
                    (f" | tone={tone}" if tone else "") +
                    (f" | depth={depth}" if depth else "") +
                    "</li>"
                )
            if rows:
                parts.append("<h4>Models</h4><ul>" + "".join(rows) + "</ul>")

        summary = payload.get("record_summary", {})
        if isinstance(summary, dict):
            plugins = summary.get("plugins") or []
            if plugins:
                plugin_rows = []
                for plugin in plugins:
                    name = html.escape(str(plugin.get("plugin") or plugin.get("slug") or ""))
                    count = plugin.get("count", 0)
                    latest = html.escape(str(plugin.get("latest") or ""))
                    plugin_rows.append(f"<li>{name}: {count} records (latest {latest})</li>")
                if plugin_rows:
                    parts.append("<h4>Plugin Coverage</h4><ul>" + "".join(plugin_rows) + "</ul>")

            categories = summary.get("top_categories") or []
            if categories:
                category_rows = []
                for category in categories:
                    name = html.escape(str(category.get("category") or ""))
                    count = category.get("count", 0)
                    category_rows.append(f"<li>{name}: {count}</li>")
                if category_rows:
                    parts.append("<h4>Top Categories</h4><ul>" + "".join(category_rows) + "</ul>")

        graph = payload.get("graph", {})
        if isinstance(graph, dict):
            node_count = graph.get("node_count", 0)
            edge_count = graph.get("edge_count", 0)
            parts.append(f"<h4>Graph Snapshot</h4><p>Nodes: {node_count} | Edges: {edge_count}</p>")
            hotspots = graph.get("hotspots") or []
            if hotspots:
                hotspot_rows = []
                for hotspot in hotspots:
                    label = html.escape(str(hotspot.get("label") or hotspot.get("id") or ""))
                    degree = hotspot.get("degree", 0)
                    slug = html.escape(str(hotspot.get("slug") or ""))
                    hotspot_rows.append(
                        f"<li>{label} (slug={slug}, degree={degree})</li>"
                    )
                if hotspot_rows:
                    parts.append("<ul>" + "".join(hotspot_rows) + "</ul>")

        return "".join(parts)


__all__ = ["LLMAnalysisDialog"]
