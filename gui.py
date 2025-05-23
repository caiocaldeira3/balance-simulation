import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QLineEdit, QLabel, QMessageBox, QComboBox, QTextEdit, QInputDialog,
    QTableWidget, QTableWidgetItem
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from balance_handler import BalanceHandler
from structs.balance import Balance, FrequencyType, SpreadType, BalanceType
from simulate import get_payment_simulation_plot


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Manager")
        self.setGeometry(100, 100, 1150, 600)
        self.setMinimumSize(900, 600)
        self.setSizePolicy(QWidget.sizePolicy(self))
        self.handler = BalanceHandler()

        main_layout = QVBoxLayout()

        # --- Balance Input Form ---
        form_layout = QGridLayout()
        self.id_input = QLineEdit(self)
        self.name_input = QLineEdit(self)
        self.value_input = QLineEdit(self)
        self.frequency_input = QLineEdit(self)

        # Dropdowns for enums
        self.frequency_unit_input = QComboBox(self)
        self.frequency_unit_input.addItems([e.value for e in FrequencyType])
        self.spread_type_input = QComboBox(self)
        self.spread_type_input.addItems([e.value for e in SpreadType])
        self.type_input = QComboBox(self)
        self.type_input.addItems([e.value for e in BalanceType])
        self.expiry_input = QLineEdit(self)
        self.start_month_input = QLineEdit(self)
        form_layout.addWidget(QLabel("ID:"), 0, 0)
        form_layout.addWidget(self.id_input, 0, 1)
        form_layout.addWidget(QLabel("Nome:"), 0, 2)
        form_layout.addWidget(self.name_input, 0, 3)
        form_layout.addWidget(QLabel("Valor:"), 1, 0)
        form_layout.addWidget(self.value_input, 1, 1)
        form_layout.addWidget(QLabel("Frequência:"), 1, 2)
        form_layout.addWidget(self.frequency_input, 1, 3)
        form_layout.addWidget(QLabel("Unidade de frequência:"), 2, 0)
        form_layout.addWidget(self.frequency_unit_input, 2, 1)
        form_layout.addWidget(QLabel("Tipo de spread:"), 2, 2)
        form_layout.addWidget(self.spread_type_input, 2, 3)
        form_layout.addWidget(QLabel("Expiração:"), 3, 0)
        form_layout.addWidget(self.expiry_input, 3, 1)
        form_layout.addWidget(QLabel("Mês de início:"), 3, 2)
        form_layout.addWidget(self.start_month_input, 3, 3)
        form_layout.addWidget(QLabel("Tipo:"), 4, 0)
        form_layout.addWidget(self.type_input, 4, 1)
        main_layout.addLayout(form_layout)

        # Balance Operations
        balance_ops_layout = QHBoxLayout()
        self.add_balance_button = QPushButton("Adicionar Despesa", self)
        self.add_balance_button.clicked.connect(self.add_balance)
        balance_ops_layout.addWidget(self.add_balance_button)

        self.update_balance_button = QPushButton("Atualizar Despesa", self)
        self.update_balance_button.clicked.connect(self.update_balance)
        balance_ops_layout.addWidget(self.update_balance_button)

        self.fetch_balance_button = QPushButton("Buscar Despesa", self)
        self.fetch_balance_button.clicked.connect(self.fetch_balance)
        balance_ops_layout.addWidget(self.fetch_balance_button)

        self.remove_balance_button = QPushButton("Remover Despesa", self)
        self.remove_balance_button.clicked.connect(self.remove_balance)
        balance_ops_layout.addWidget(self.remove_balance_button)

        main_layout.addLayout(balance_ops_layout)

        # Display Balances
        self.balances_table = QTableWidget(self)
        self.balances_table.setColumnCount(10)
        self.balances_table.setHorizontalHeaderLabels([
            "ID", "Nome", "Valor", "Frequência", "Unidade", "Spread", "Expiração", "Mês de início", "Tipo", ""
        ])
        main_layout.addWidget(self.balances_table)

        # Payment Simulation
        sim_layout = QGridLayout()
        # First row: payment_size, investment_size, initial_payment
        sim_layout.addWidget(QLabel("Tamanho do pagamento:"), 0, 0)
        self.payment_size_input = QLineEdit(self)
        sim_layout.addWidget(self.payment_size_input, 0, 1)
        sim_layout.addWidget(QLabel("Tamanho do investimento:"), 0, 2)
        self.investment_size_input = QLineEdit(self)
        sim_layout.addWidget(self.investment_size_input, 0, 3)
        sim_layout.addWidget(QLabel("Pagamento inicial:"), 0, 4)
        self.initial_payment_input = QLineEdit(self)
        sim_layout.addWidget(self.initial_payment_input, 0, 5)
        # Second row: profit_tax, investment_yearly_percentage
        sim_layout.addWidget(QLabel("Taxa de lucro:"), 1, 0)
        self.profit_tax_input = QLineEdit(self)
        sim_layout.addWidget(self.profit_tax_input, 1, 1)
        sim_layout.addWidget(QLabel("% Investimento anual:"), 1, 2)
        self.investment_yearly_input = QLineEdit(self)
        sim_layout.addWidget(self.investment_yearly_input, 1, 3)
        self.simulate_button = QPushButton("Simular Pagamento", self)
        self.simulate_button.clicked.connect(self.simulate_payment)
        sim_layout.addWidget(self.simulate_button, 1, 4, 1, 2)
        main_layout.addLayout(sim_layout)

        # Simulation Results
        self.simulation_display = QTextEdit(self)
        self.simulation_display.setReadOnly(True)
        main_layout.addWidget(self.simulation_display)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.refresh_balances()

    def refresh_balances(self):
        df = self.handler.df
        self.balances_table.setRowCount(0)
        if df.empty:
            self.balances_table.setRowCount(1)
            for col in range(self.balances_table.columnCount()):
                self.balances_table.setItem(0, col, QTableWidgetItem(""))
        else:
            self.balances_table.setRowCount(len(df))
            for row_idx, row in df.iterrows():
                self.balances_table.setItem(row_idx, 0, QTableWidgetItem(str(row.get("id", ""))))
                self.balances_table.setItem(row_idx, 1, QTableWidgetItem(str(row.get("name", ""))))
                self.balances_table.setItem(row_idx, 2, QTableWidgetItem(str(row.get("value", ""))))
                self.balances_table.setItem(row_idx, 3, QTableWidgetItem(str(row.get("frequency", ""))))
                self.balances_table.setItem(row_idx, 4, QTableWidgetItem(str(row.get("frequency_unit", ""))))
                self.balances_table.setItem(row_idx, 5, QTableWidgetItem(str(row.get("spread_type", ""))))
                self.balances_table.setItem(row_idx, 6, QTableWidgetItem(str(row.get("expiry", ""))))
                self.balances_table.setItem(row_idx, 7, QTableWidgetItem(str(row.get("start_month", ""))))
                self.balances_table.setItem(row_idx, 8, QTableWidgetItem(str(row.get("type", ""))))
                # 9th column left blank for future actions

    def get_balance_from_form(self):
        try:
            expiry = self.expiry_input.text().strip()
            expiry = int(expiry) if expiry else None
            start_month = self.start_month_input.text().strip()
            start_month = int(start_month) if start_month else None
            return Balance(
                id=self.id_input.text().strip(),
                name=self.name_input.text().strip(),
                value=float(self.value_input.text()),
                frequency=float(self.frequency_input.text()),
                frequency_unit=self.frequency_unit_input.currentText(),
                spread_type=self.spread_type_input.currentText(),
                expiry=expiry,
                start_month=start_month,
                type=self.type_input.currentText()
            )

        except Exception as e:
            raise ValueError(f"Erro ao ler dados do formulário: {e}")

    def clear_balance_form(self):
        self.id_input.clear()
        self.name_input.clear()
        self.value_input.clear()
        self.frequency_input.clear()
        self.frequency_unit_input.setCurrentIndex(0)
        self.spread_type_input.setCurrentIndex(0)
        self.expiry_input.clear()
        self.start_month_input.clear()
        self.type_input.setCurrentIndex(0)

    def add_balance(self):
        try:
            balance = self.get_balance_from_form()
            self.handler.add_balances([balance])
            self.refresh_balances()
            self.clear_balance_form()
            QMessageBox.information(self, "Sucesso", "Despesa adicionada com sucesso.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao adicionar despesa: {e}")

    def update_balance(self):
        try:
            balance = self.get_balance_from_form()
            self.handler.update_balances_by_id([balance])
            self.refresh_balances()
            self.clear_balance_form()
            QMessageBox.information(self, "Sucesso", "Despesa atualizada com sucesso.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao atualizar despesa: {e}")

    def remove_balance(self):
        try:
            balance_id, ok = QInputDialog.getText(self, "Remover Despesa", "ID da despesa:")
            if ok and balance_id:
                self.handler.remove_balances_by_id([balance_id])
                self.refresh_balances()
                QMessageBox.information(self, "Sucesso", "Despesa removida com sucesso.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao remover despesa: {e}")

    def fetch_balance(self):
        try:
            balance_id, ok = QInputDialog.getText(self, "Buscar Despesa", "ID da despesa:")
            if ok and balance_id:
                balance = self.handler.query_balance_by_id(balance_id)
                if balance:
                    self.id_input.setText(str(balance.id))
                    self.name_input.setText(str(balance.name))
                    self.value_input.setText(str(balance.value))
                    self.frequency_input.setText(str(balance.frequency))
                    self.frequency_unit_input.setCurrentText(str(balance.frequency_unit))
                    self.spread_type_input.setCurrentText(str(balance.spread_type))
                    self.expiry_input.setText(str(balance.expiry))
                    self.start_month_input.setText(str(balance.start_month) if balance.start_month is not None else "")
                    self.type_input.setCurrentText(str(balance.type))
                    QMessageBox.information(self, "Sucesso", "Despesa carregada no formulário.")

                else:
                    QMessageBox.warning(self, "Não encontrado", f"Despesa com ID {balance_id} não encontrada.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao buscar despesa: {e}")

    def simulate_payment(self):
        try:
            payment_size = float(self.payment_size_input.text())
            investment_size = float(self.investment_size_input.text())
            initial_payment = float(self.initial_payment_input.text() or 0)
            profit_tax = float(self.profit_tax_input.text() or 0)
            investment_yearly = float(self.investment_yearly_input.text() or 0)
            fig = get_payment_simulation_plot(
                self.handler, payment_size, investment_size,
                initial_payment=initial_payment,
                profit_tax=profit_tax,
                investment_yearly_percentage=investment_yearly
            )
            # Remove previous canvas if exists
            if hasattr(self, 'plot_canvas') and self.plot_canvas is not None:
                self.simulation_display.layout().removeWidget(self.plot_canvas)
                self.plot_canvas.setParent(None)
                self.plot_canvas = None
            # Clear text display
            self.simulation_display.clear()
            # Embed the matplotlib figure in the QTextEdit area
            self.plot_canvas = FigureCanvas(fig)
            layout = self.simulation_display.parentWidget().layout()
            layout.addWidget(self.plot_canvas)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha na simulação: {e}")

    def closeEvent (self, event) -> None:
        # Save the dataframe to balance.csv before exit
        try:
            self.handler.df.to_csv('balance.csv', index=False)

        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Falha ao salvar balance.csv: {e}")

        event.accept()

def main():
    app = QApplication.instance()
    app_created = False
    if app is None:
        app = QApplication(sys.argv)
        app_created = True
    window = MainWindow()
    window.show()
    if app_created:
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
