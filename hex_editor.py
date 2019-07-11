from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QPushButton, QGridLayout, QWidget
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt
import sys
from hex_data import HexData


class HexEditorWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.data = None
        self.initUI()

    def initUI(self):
        self.setFixedSize(1050, 900)
        self.setWindowTitle("Hex editor")

        self.table = QTableWidget(100, 10, self)
        self.table.cellChanged.connect(self.cell_changed)
        self.table.setColumnCount(17)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        self.table.setHorizontalHeaderLabels(["0" + hex(x)[2:] for x in range(0, 16)] + [""])
        self.table.setVerticalHeaderLabels([hex(y * 16)[2:].zfill(8) for y in range(0, 100)])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.setDisabled(True)

        self.file_name = QLabel(self)
        self.file_name.setText("File name: ")


        self.load = QPushButton("Open", self)
        self.load.clicked.connect(self.load_file)

        self.add = QPushButton("Add row", self)
        self.add.clicked.connect(self.add_row)
        self.add.setDisabled(True)

        self.delete = QPushButton("Delete row", self)
        self.delete.clicked.connect(self.delete_row)
        self.delete.setDisabled(True)

        self.save = QPushButton("Save", self)
        self.save.clicked.connect(self.save_file)
        self.save.setDisabled(True)

        layout = QGridLayout()
        layout.addWidget(self.table, 1, 0, 10, 10)
        layout.addWidget(self.load, 0, 0)
        layout.addWidget(self.add, 0, 1)
        layout.addWidget(self.save, 0, 3)
        layout.addWidget(self.delete, 0, 2)
        layout.addWidget(self.file_name, 0, 4)
        window = QWidget()
        window.setLayout(layout)
        self.setCentralWidget(window)

    def load_file(self):
        path = QFileDialog.getOpenFileName(self, "Open File")[0]
        if path != "":
            self.data = HexData(path)
            self.fill_data()
            self.file_name.setText("File name: " + path.split("/")[-1])
            self.table.setDisabled(False)
            self.add.setDisabled(False)
            self.save.setDisabled(False)
            self.delete.setDisabled(False)

    def fill_data(self):
        self.table.setRowCount(len(self.data.data))
        for y in range(len(self.data.data)):
            for x in range(len(self.data.data[y])):
                self.table.setItem(y, x, QTableWidgetItem(self.data.data[y][x]))
        for i in range(len(self.data.encoding)):
            self.table.setItem(i, 16, QTableWidgetItem(self.data.encoding[i]))
        self.table.resizeColumnsToContents()
        self.table.setVerticalHeaderLabels([hex(y * 16)[2:].zfill(8) for y in range(len(self.data.data))])

    def cell_changed(self, row, col):
        if self.data is None:
            self.table.item(row, col).setText("")
            return
        if not self.table.item(row, col).isSelected():
            return
        if col == 16:
            if self.data.check_change_encoded_text(row, self.table.item(row, col).text()):
                self.update_row(row)
            else:
                self.table.setItem(row, 16, QTableWidgetItem(self.data.encoding[row]))
            return
        elif not self.data.check_change(row, col, self.table.item(row, col).text().lower()):
            if not len(self.data.data[row]) - 1 < col:
                self.table.item(row, col).setText(self.data.data[row][col])
            else:
                self.table.item(row, col).setText("")
        else:
            self.table.item(row, 16).setText(self.data.encoding[row])
            self.table.item(row, col).setForeground(QBrush(Qt.red))
            self.data.changed_cells.add((row, col))
        self.update_row(row)

    def update_row(self, row):
        for x in range(len(self.data.data[row])):
            if self.table.item(row, x) is None:
                self.table.setItem(row, x, QTableWidgetItem(""))
            if self.table.item(row, x).text() != self.data.data[row][x]:
                self.table.item(row, x).setText(self.data.data[row][x])
                self.table.item(row, x).setForeground(QBrush(Qt.red))
                self.data.changed_cells.add((row, x))
        if self.table.item(row, 16) is None:
            self.table.setItem(row, 16, QTableWidgetItem(""))
        if self.table.item(row, 16).text() != self.data.encoding[row]:
            self.table.setItem(row, 16, QTableWidgetItem(self.data.encoding[row]))

    def save_file(self):
        if self.data is not None:
            self.data.save()
            self.recolor_changes()

    def add_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        for x in range(17):
            self.table.setItem(row_count, x, QTableWidgetItem(""))
        self.table.setVerticalHeaderItem(row_count, QTableWidgetItem(hex(row_count * 16)[2:].zfill(8)))
        self.data.add_row()
        self.update_row(row_count - 1)

    def delete_row(self):
        self.table.removeRow(self.table.rowCount() - 1)
        self.data.delete_row()

    def recolor_changes(self):
        for cell in self.data.changed_cells:
            self.table.item(cell[0], cell[1]).setForeground(QBrush(Qt.black))
        self.data.changed_cells.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HexEditorWindow()
    ex.show()
    sys.exit(app.exec_())
