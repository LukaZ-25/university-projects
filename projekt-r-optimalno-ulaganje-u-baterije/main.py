import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel,
                             QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
                             QLineEdit, QFileDialog, QComboBox, QSizePolicy)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import calculations_highs as calculations

human_datum = ["Koji mjesec:", "Koji dan:"]  # za koji dan neka bude dvije brojke, mjesec i dan
human_outputs = ["Godišnja cijena s baterijom", "Godišnja originalna cijena", "Ušteda"]
human_inputs = ["Veličina baterije:", "Dnevna tarifa:", "Noćna tarifa:", "Cijena Peak Monthly Load:"]
human_inputs_stand_vals = [0, 0.16, 0.09, 3.57]


class CalculationWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, values):
        super().__init__()
        self.values = values

    def run(self):
        try:
            result = calculations.gigaracun(self.values)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projekt - Optimizator")  # ovdje ide naslov
        self.setGeometry(0, 0, 500, 800)  # gdje i koliki se stvori

        # sad slijede sve stvorene stvari
        self.label01 = QLabel("IZRAČUN ULAGANJA U BATERIJE", self)
        self.label02 = QLabel("Pišite decimalne brojeve točkom, ne zarezom")
        self.button_excel = QPushButton("Odaberi Excel")
        self.excel_path_label = QLabel("Nije odabrano")
        self.labels_inputs = []
        self.button_calculate = QPushButton("IZRAČUNAJ", self)
        self.labels_outputs = []
        self.labels_oznake = []
        self.datum = []
        self.rezultati = "0"

        # Dva grafa: punjenje, praznjenje, taj redoslijed; sad stanu cijeli grafovi
        self.fig_charge = Figure(figsize=(4, 2))
        self.fig_charge.set_tight_layout(True)
        self.fig_charge.subplots_adjust(bottom=0.15)
        self.canvas_charge = FigureCanvas(self.fig_charge)

        self.fig_discharge = Figure(figsize=(4, 2))
        self.fig_discharge.set_tight_layout(True)
        self.fig_discharge.subplots_adjust(bottom=0.15)
        self.canvas_discharge = FigureCanvas(self.fig_discharge)

        self.excel_file_path = None

        # sad slijedi initUI i adjoining funkcije: postavlja sve
        self.initUI()
        self.ukrasi()  # ukrasava sve da izgleda lijepo, osim grafa

    def ukrasi(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #eef7ee;
                font-family: Segoe UI, Arial;
                font-size: 14px;
            }

            /* General labels */
            QLabel {
                color: #2e4d2e;
                font-weight: 500;
            }

            /* Result labels */
            QLabel[resultLabel="true"] {
                font-weight: 500;
                color: #1f3b1f;
            }

            /* Resultati */
            QLabel[resultValue="true"] {
                font-weight: 500;
                font-size: 16px;
                color: #0f5f0f;
                qproperty-alignment: 'AlignRight | AlignVCenter';
            }

            /* Buttons */
            QPushButton {
                background-color: #3fa34d;
                color: white;
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: bold;
                border: 2px solid #2e7a3a;
            }

            /* Button hover */
            QPushButton:hover {
                background-color: #4fbd5e;
            }

            /* Button pritisnut */
            QPushButton:pressed {
                background-color: #2e7a3a;
                border: 2px solid #1f5a2a;
                padding-top: 10px;   /* visual press effect */
                padding-bottom: 6px;
            }

            /* Disabled button */
            QPushButton:disabled {
                background-color: #8acb8f;
                border: 2px solid #6bbf72;
            }

            /* Dropdown menus */
            QComboBox {
                background-color: #ffffff;
                padding: 4px 6px;
                padding-right: 22px;
                border: 1px solid #6bbf72;
                border-radius: 4px;
                font-weight: 500;
                color: #0f5f0f;
            }
            
            QComboBox::editable {
                padding-right: 22px;
            }

            QComboBox:hover {
                border: 1px solid #3fa34d;
            }
        """)

        # Title styling
        self.label01.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #1f7a1f;
            padding: 10px;
            border-bottom: 2px solid #3fa34d;
            /*qproperty-alignment: 'AlignCenter';*/
        """)

        # Uredi labels za results
        for label in self.labels_oznake:
            label.setProperty("resultLabel", "true")
            label.style().unpolish(label)
            label.style().polish(label)

        for label in self.labels_outputs:
            label.setProperty("resultValue", "true")
            label.style().unpolish(label)
            label.style().polish(label)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        grid_main = QGridLayout()

        # Naslov - label01
        current_line = 0
        grid_main.addWidget(self.label02, current_line, 1, 1, 1)
        current_line += 1

        # unošenje parametara - Human inputs
        for i in range(0, len(human_inputs)):
            label = QLabel(human_inputs[i])
            self.labels_oznake.append(label)
            grid_main.addWidget(label, current_line + i, 0)
            input_box = QLineEdit()
            input_box.setPlaceholderText(str(human_inputs_stand_vals[i]))
            self.labels_inputs.append(input_box)
            grid_main.addWidget(input_box, current_line + i, 1)
        current_line += len(human_inputs)

        # unošenje excel tablice
        hbox_excel = QHBoxLayout()
        self.button_excel.clicked.connect(self.choose_excel)
        hbox_excel.addWidget(self.button_excel)
        hbox_excel.addWidget(self.excel_path_label)
        grid_main.addLayout(hbox_excel, current_line, 0, 1, 2)
        current_line += 1

        # ovdje botun za izračune
        self.button_calculate.clicked.connect(self.click_calculate)
        grid_main.addWidget(self.button_calculate, current_line, 0, 1, 2)
        current_line += 1

        # prikazivanje rezultata izracuna (brojke)
        for i in range(0, len(human_outputs)):
            label = QLabel(human_outputs[i])
            self.labels_oznake.append(label)
            grid_main.addWidget(label, current_line + i, 0)
            label = QLabel("-")
            self.labels_outputs.append(label)
            grid_main.addWidget(label, current_line + i, 1)
        current_line += len(human_outputs)

        # dropdown menus (biranje mjeseca i dana)
        for i in range(0, len(human_datum)):
            label = QLabel(human_datum[i])
            self.labels_oznake.append(label)
            grid_main.addWidget(label, current_line, 0)

            dropdown_widget = QWidget()
            vbox = QVBoxLayout(dropdown_widget)
            vbox.setContentsMargins(0, 0, 0, 0)

            self.dropdown = QComboBox()  # nemoj ga pomicati u __init__, treba ovdje biti
            if i == 0:
                self.dropdown.addItems([
                    "Siječanj", "Veljača", "Ožujak", "Travanj",
                    "Svibanj", "Lipanj", "Srpanj", "Kolovoz",
                    "Rujan", "Listopad", "Studeni", "Prosinac"
                ])
            else:
                self.dropdown.addItems([
                    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16",
                    "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"
                ])

            self.dropdown.setCurrentIndex(0)
            self.dropdown.currentTextChanged.connect(self.koji_datum)
            self.dropdown.setMaxVisibleItems(12)
            self.datum.append(self.dropdown)
            vbox.addWidget(self.dropdown)

            grid_main.addWidget(dropdown_widget, current_line, 1)
            current_line += 1

        # odvajanje podataka lijevo
        grid_2 = QGridLayout()
        grid_2.addLayout(grid_main, 0, 0, 2, 1)

        # grafovi
        grid_2.addWidget(self.canvas_charge, 0, 1)
        grid_2.addWidget(self.canvas_discharge, 1, 1)

        # udio sirine grafova i podataka
        grid_2.setColumnStretch(0, 1)
        grid_2.setColumnStretch(1, 2)

        # naslov na vrh cijelom sirinom
        vbox = QVBoxLayout()
        vbox.addWidget(self.label01)
        vbox.addLayout(grid_2)
        vbox.setStretch(0, 0)
        vbox.setStretch(1, 1)

        # kraj
        central_widget.setLayout(vbox)

    def koji_datum(self):  # ovdje napravi dva grafa: punjenje i praznjenje
        koji_mjesec = self.datum[0].currentIndex()
        koji_dan = self.datum[1].currentIndex()
        if self.rezultati != "0":
            sati_charge = self.rezultati[len(human_outputs)][koji_mjesec][koji_dan*24:(koji_dan+1)*24]
            sati_discharge = self.rezultati[len(human_outputs)+1][koji_mjesec][koji_dan*24:(koji_dan+1)*24]
            self.update_charge_graph(sati_charge)
            self.update_discharge_graph(sati_discharge)

    def choose_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Odaberi Excel datoteku",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.excel_file_path = file_path
            self.excel_path_label.setText(file_path)

    def update_charge_graph(self, charge):
        self.fig_charge.clear()
        ax = self.fig_charge.add_subplot(111)

        hours = list(range(24))
        ax.plot(hours, charge, marker="o", color="green")
        ax.set_title("Punjenje (Charge)")
        ax.set_xlabel("Sat")
        ax.set_ylabel("kWh")
        ax.grid(True)

        self.canvas_charge.draw()

    def update_discharge_graph(self, discharge):
        self.fig_discharge.clear()
        ax = self.fig_discharge.add_subplot(111)

        hours = list(range(24))
        ax.plot(hours, discharge, marker="o", color="red")
        ax.set_title("Pražnjenje (Discharge)")
        ax.set_xlabel("Sat")
        ax.set_ylabel("kWh")
        ax.grid(True)

        self.canvas_discharge.draw()

    def click_calculate(self):
        # tokom izračuna blokiraj botun i unose
        # blokiras botun
        self.button_calculate.setText("IZRAČUNAVA SE")
        self.button_calculate.setDisabled(True)
        QApplication.processEvents()
        # sad se izracunaju stvari i vrate vrijednosti
        try:
            if not self.excel_file_path:
                raise Exception("File nije chosen")
            df = pd.read_excel(self.excel_file_path)
            list_values = []
            for element in df.values.tolist()[1:]:
                list_values.append(element[1])
            # values = [800, 0.16, 0.09, 3.57, 40, 0.013239, 50]  # P_distr > D__tm svaki element: nebitan komentar
            human_unosi = []
            for i, element in enumerate(self.labels_inputs):
                value = element.text()
                if value == "":
                    human_unosi.append(human_inputs_stand_vals[i])
                else:
                    human_unosi.append(float(element.text()))
            values = [list_values, human_unosi]

            # Stvori thread, worker: normalan rad programa
            self.thread = QThread()
            self.worker = CalculationWorker(values)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.handle_results)
            self.worker.error.connect(self.handle_error)

            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

        except Exception as e:
            self.handle_error(str(e))

    def handle_results(self, results):
        self.rezultati = results
        for i in range(len(human_outputs)):
            self.labels_outputs[i].setText(str(results[i]))
        self.button_calculate.setText("IZRAČUNAJ")
        self.button_calculate.setDisabled(False)
        self.koji_datum()  # update graphs
        # ne bude selectan text
        self.button_calculate.setFocus()

    def handle_error(self, message):
        self.labels_outputs[0].setText("Greška")
        self.labels_outputs[1].setText(message)

        self.button_calculate.setText("IZRAČUNAJ")
        self.button_calculate.setDisabled(False)


def main():
    # print("Pozdrav svijete")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
