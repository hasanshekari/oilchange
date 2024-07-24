import sys
import sqlite3
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox


class customer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.create_database()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('تعویض روغن معین')
        layout = QtWidgets.QVBoxLayout()

        # Inputs
        self.name_input = QtWidgets.QLineEdit(self)
        self.phone_input = QtWidgets.QLineEdit(self)
        self.car_type_input = QtWidgets.QLineEdit(self)

        layout.addWidget(QtWidgets.QLabel('  نام و نام خانوادگی:'))
        layout.addWidget(self.name_input)
        layout.addWidget(QtWidgets.QLabel('شماره موبایل:'))
        layout.addWidget(self.phone_input)
        layout.addWidget(QtWidgets.QLabel('نوع خودرو:'))
        layout.addWidget(self.car_type_input)

        # Buttons
        self.save_button = QtWidgets.QPushButton('ثبت', self)
        self.edit_button = QtWidgets.QPushButton('ویرایش', self)
        self.delete_button = QtWidgets.QPushButton('حذف', self)
        self.search_button = QtWidgets.QPushButton('جستجو', self)
        self.refresh_button = QtWidgets.QPushButton("بروز رسانی", self)

        self.save_button.clicked.connect(self.save_customer)
        self.edit_button.clicked.connect(self.edit_customer)
        self.delete_button.clicked.connect(self.delete_customer)
        self.search_button.clicked.connect(self.search_customer)
        self.refresh_button.clicked.connect(self.load_customers)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.refresh_button)

        layout.addLayout(button_layout)

        # Table
        self.customer_table = QtWidgets.QTableWidget(self)
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(['ID', 'نام', 'شماره موبایل', 'نوع خودرو'])
        self.customer_table.cellClicked.connect(self.populate_form)

        layout.addWidget(self.customer_table)

        self.setLayout(layout)

        self.load_customers()

    def create_database(self):
        self.connection = sqlite3.connect('customers.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS customers (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                name TEXT,  
                phone TEXT,  
                car_type TEXT  
            )  
        ''')
        self.connection.commit()

    def save_customer(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        car_type = self.car_type_input.text()

        try:
            self.cursor.execute("INSERT INTO customers (name, phone, car_type) VALUES (?, ?, ?)", (name, phone, car_type))
            self.connection.commit()
            self.load_customers()
            self.clear_inputs()
        except Exception as e:
            print("Error occurred during saving customer:", e)

    def edit_customer(self):
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            customer_id = self.customer_table.item(selected_row, 0).text()
            name = self.name_input.text()
            phone = self.phone_input.text()
            car_type = self.car_type_input.text()

            self.cursor.execute("UPDATE customers SET name=?, phone=?, car_type=? WHERE id=?",
                                (name, phone, car_type, customer_id))
            self.connection.commit()
            self.load_customers()
            self.clear_inputs()

    def delete_customer(self):
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            customer_id = self.customer_table.item(selected_row, 0).text()
            reply = QMessageBox.question(self, 'تأیید حذف', 'آیا مطمئن هستید که می‌خواهید حذف کنید؟',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
                self.connection.commit()
                self.load_customers()
                self.clear_inputs()

    def search_customer(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        car_type = self.car_type_input.text()

        # شرط جستجوی نام، شماره تلفن و نوع خودرو
        query = "SELECT * FROM customers WHERE 1=1"
        parameters = []

        if name:  # اگر نام وارد شده باشد
            query += " AND name LIKE ?"
            parameters.append('%' + name + '%')

        if phone:  # اگر شماره تلفن وارد شده باشد
            query += " AND phone LIKE ?"
            parameters.append('%' + phone + '%')

        if car_type:  # اگر نوع خودرو وارد شده باشد
            query += " AND car_type LIKE ?"
            parameters.append('%' + car_type + '%')

        self.cursor.execute(query, parameters)
        self.populate_table(self.cursor.fetchall())

    def load_customers(self):
        self.clear_inputs()
        self.cursor.execute("SELECT * FROM customers")
        result = self.cursor.fetchall()
        self.populate_table(result)
    def populate_table(self, data):
        self.customer_table.setRowCount(0)
        for row in data:
            self.customer_table.insertRow(self.customer_table.rowCount())
            for column, item in enumerate(row):
                self.customer_table.setItem(self.customer_table.rowCount() - 1, column, QtWidgets.QTableWidgetItem(str(item)))

    def populate_form(self, row, column):
        self.name_input.setText(self.customer_table.item(row, 1).text())
        self.phone_input.setText(self.customer_table.item(row, 2).text())
        self.car_type_input.setText(self.customer_table.item(row, 3).text())

    def clear_inputs(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.car_type_input.clear()

app = QtWidgets.QApplication(sys.argv)
window = customer()
window.show()
sys.exit(app.exec_())
