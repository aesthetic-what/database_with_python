import sys
from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

class Object_data(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("database.ui", self)
        self.setWindowTitle("DataBase")
        # Кнопки
        self.openDB.clicked.connect(self.open_data)
        self.nextDB.clicked.connect(self.next_data)
        self.lastDB.clicked.connect(self.last_data)

        self.model = None
        self.current_table_index = 0
        self.table_list = []

    def open_data(self):
        # Открытие базы данных
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('pythondb.sqlite')

        # Условие: если база данных не откроется, вывести ошибку
        if not self.db.open():
            QMessageBox.critical(self, "Ошибка подключения!", "Не удалось подключиться к базе данных.")
            sys.exit(1)

        # Создание модели для работы с таблицей базы данных
        self.model = QSqlTableModel(self)
        self.model.setTable("Товары")  # Укажите вашу таблицу
        self.model.select()

        self.table_list = self.db.tables()

        # Проверка наличия таблиц
        if not self.table_list:
            QMessageBox.warning(self, "Нет данных", "Таблица не содержит данных для отображения.")
            return

        # Вывод таблицы в tableView
        self.tableView.setModel(self.model)

        # Обновление текущей строки
        self.current_table_index = 0
        self.load_table(self.table_list[self.current_table_index])

    def load_table(self, table_name):
        if self.model is None:
            self.model = QSqlDatabase(self)
        
        self.model.setTable(table_name)
        self.model.select()
        self.name_table.setText(table_name)

        # Проверка на наличие данных
        if self.model.rowCount() == 0:
            QMessageBox.warning(self, "Нет данных")

        # Установка модели для отображения данных
        self.tableView.setModel(self.model)


    def next_data(self):
        if self.current_table_index < len(self.table_list) - 1:
            self.current_table_index += 1
            self.load_table(self.table_list[self.current_table_index])
            print(f'номер страницы: {self.current_table_index}, всего страниц: {len(self.table_list)}')
        elif self.current_table_index + 1 == len(self.table_list):
            self.current_table_index = 0
            self.load_table(self.table_list[self.current_table_index])

    def last_data(self):
        if self.current_table_index > 0:
            self.current_table_index -= 1
            self.load_table(self.table_list[self.current_table_index])
            print(f'номер страницы: {self.current_table_index}, всего страниц: {len(self.table_list)}')
        elif self.current_table_index == 0:
             self.current_table_index = len(self.table_list) - 1
             self.load_table(self.table_list[self.current_table_index])
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Object_data()
    win.setFixedSize(898, 429)
    win.show()
    sys.exit(app.exec_())