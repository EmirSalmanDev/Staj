import sys
import re
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox
)

class TextToTableApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Computer Info Viewer")
        self.resize(900, 600)
        self.file_paths = []

        layout = QVBoxLayout(self)

        self.button_load = QPushButton("Select TXT Files and Load")
        self.button_load.clicked.connect(self.select_files)
        layout.addWidget(self.button_load)

        self.button_save = QPushButton("Save Changes to Files")
        self.button_save.clicked.connect(self.save_files)
        layout.addWidget(self.button_save)

        self.button_export = QPushButton("Export to CSV")
        self.button_export.clicked.connect(self.export_to_csv)
        layout.addWidget(self.button_export)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.data = []
        self.columns = []

    def select_files(self):
        self.file_paths, _ = QFileDialog.getOpenFileNames(self, filter="Text Files (*.txt)")
        self.data = []

        for path in self.file_paths:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
                entry = self.parse_lines(lines)
                self.data.append(entry)

        self.display_table(self.data)

    def parse_lines(self, lines):
        result = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # key : value
            if ":" in line:
                parts = line.split(":", 1)
                key = parts[0].strip()
                value = parts[1].strip()
                if value == "" and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and (":" not in next_line and "=" not in next_line):
                        value = next_line
                        i += 1
                result[key] = value

            # key = value
            elif "=" in line:
                parts = line.split("=", 1)
                key = parts[0].strip()
                value = parts[1].strip()
                result[key] = value

            # terminal-style (MediaType DeviceID Model)
            elif (
                re.match(r'^\w+( +\w+)*$', line)
                and i + 1 < len(lines)
                and re.match(r'^[- ]+$', lines[i + 1].strip())
            ):
                headers = re.split(r'\s+', line.strip())
                j = i + 2
                while j < len(lines):
                    row_line = lines[j].strip()
                    if not row_line:
                        break
                    row = re.split(r'\s{2,}', row_line)
                    if len(row) == len(headers):
                        for h, v in zip(headers, row):
                            result[h.strip()] = v.strip()
                        j += 1
                    else:
                        break
                i = j - 1



            # Alt satırda veri olan başlıklar
            else:
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and (":" not in next_line and "=" not in next_line):
                        result[line] = next_line
                        i += 1

            i += 1
        return result

    def display_table(self, data):
        if not data:
            return
        self.columns = sorted({key for item in data for key in item})
        self.table.setColumnCount(len(self.columns))
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(self.columns)

        for row_index, item in enumerate(data):
            for col_index, key in enumerate(self.columns):
                value = item.get(key, "")
                cell = QTableWidgetItem(value)
                cell.setFlags(cell.flags() | 2)  # editable
                self.table.setItem(row_index, col_index, cell)

    def save_files(self):
        updated_data = []
        for row in range(self.table.rowCount()):
            entry = {}
            for col, key in enumerate(self.columns):
                item = self.table.item(row, col)
                value = item.text() if item else ""
                entry[key] = value
            updated_data.append(entry)

        for i, path in enumerate(self.file_paths):
            entry = updated_data[i]
            with open(path, "w", encoding="utf-8") as f:
                for key, value in entry.items():
                    f.write(f"{key} = {value}\n")

        QMessageBox.information(self, "Saved", "Changes saved to files successfully.")

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", filter="CSV Files (*.csv)")
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.columns)

            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)

        QMessageBox.information(self, "Exported", f"CSV file saved successfully:\n{path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextToTableApp()
    window.show()
    sys.exit(app.exec_())
