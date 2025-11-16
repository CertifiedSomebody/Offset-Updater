from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from .theme import Theme


class ResultsViewer(QWidget):
    """Displays analysis results in a table format."""

    def __init__(self):
        super().__init__()

        title = QLabel("Analysis Results")
        title.setFont(Theme.FONT_BOLD)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Method", "Old Offset", "New Offset"]
        )

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_results(self, results: dict):
        """
        Load data into the table.
        Handles new OffsetAnalyzer structure.
        """
        entries = []

        # Outdated entries (have old and new offsets)
        for item in results.get("outdated", []):
            entries.append({
                "method": item["func"],
                "old": item.get("old_offset"),
                "new": item.get("new_offset")
            })

        # Updated entries (no old offset)
        for item in results.get("updated", []):
            if any(e["method"] == item["func"] for e in entries):
                continue
            entries.append({
                "method": item["func"],
                "old": None,
                "new": item.get("offset")
            })

        # Missing in dump (old offset is from source)
        for item in results.get("missing_in_dump", []):
            entries.append({
                "method": item["func"],
                "old": item.get("source_offset"),
                "new": None
            })

        # Clear table and set row count
        self.table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(entry["method"]))

            # Format offsets as hex if numeric, otherwise show N/A
            old_val = entry["old"]
            new_val = entry["new"]

            if isinstance(old_val, int):
                old_val = hex(old_val)
            elif old_val is None:
                old_val = "[N/A]"

            if isinstance(new_val, int):
                new_val = hex(new_val)
            elif new_val is None:
                new_val = "[N/A]"

            self.table.setItem(row, 1, QTableWidgetItem(str(old_val)))
            self.table.setItem(row, 2, QTableWidgetItem(str(new_val)))
