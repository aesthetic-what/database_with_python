import sys
import bcrypt
from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox


class Login_window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r"design\login.ui", self)
        self.setWindowTitle("DataBase")

        # кнопка авторизации
        self.loginbutton.clicked.connect(self.login)

        # кнопка регистрации
        self.register_2.clicked.connect(self.reg)

    def login(self):

        login = self.lineEdit.text()
        password = self.lineEdit_2.text()

        role_client = 'Клиент'
        role_admin = 'Админ'

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('form.db')
        self.db.open()

        if not login or not password:
            QMessageBox.warning(self, 'заполните все поля', 'не все поля заполнены, заполните их для регистрации')
            return
        
        query = QSqlQuery()
        query.prepare("SELECT hash_pass, Role FROM users WHERE login = ?;")
        query.addBindValue(login)
        query.exec_()
        
        if query.next():
            self.db_pass = query.value(0).encode('utf-8')
            self.db_role = query.value(1)
            if bcrypt.checkpw(password.encode('utf-8'), self.db_pass):
                if self.db_role == role_admin:

                    print(f'хеш: {self.db_pass}'
                        f'пароль: {password}')
                    
                    QMessageBox.information(self, 'Успех!', 'Вы успешно авторизировались')
                    Login_window.close(self)
                    self.DB_win = Admin_window()
                    self.DB_win.show()
                    return
                else:
                    Login_window.close(self)
                    self.DB_win = Object_data()
                    self.DB_win.show()
            else:
                print(self.db_pass)
                QMessageBox.warning(self, 'Ошибка!', 'Неправильно введен пароль')
        else:
            QMessageBox.warning(self, 'Ошибка!', 'Пользователь с таким логином не найден')

    def reg(self):
        self.register = Register_window()
        Login_window.close(self)
        self.register.show()

class Register_window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r"design\register.ui", self)
        self.setWindowTitle("DataBase")

        # кнопка регистрации
        self.register_button.clicked.connect(self.register)

        # кнопка авторизации
        self.login_button.clicked.connect(self.login_in_reg)

        
    def register(self):

        # строки состояния
        login = self.first_line.text()
        password = self.sec_line.text()
        conf_password = self.sec_line_confirm.text()

        role = 'Клиент'

        hashed_password = bcrypt.hashpw(conf_password.encode('utf-8'), bcrypt.gensalt())  # Хэширование с добавлением соли


        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('form.db')
        self.db.open()

        if not login or not password or not conf_password:
            QMessageBox.warning(self, 'заполните все поля', 'не все поля заполнены, заполните их для регистрации')
            return
        elif not password == conf_password:
            QMessageBox.warning(self, 'пароли не совпадают', 'пароли не совпадают, проверьте написание пароля')
            return
        
        query = QSqlQuery()
        query.prepare("SELECT COUNT(*) FROM users WHERE login = ?;")
        query.addBindValue(login)
        query.exec_()

        if query.next() and query.value(0) > 0:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем или email уже существует.")
            return
        
        # Вставка нового пользователя в таблицу
        query.prepare("INSERT INTO users (login, pass, hash_pass, Role) VALUES (?, ?, ?, ?);")
        query.addBindValue(login)
        query.addBindValue(password) # В реальной системе нужно использовать хэширование пароля!
        query.addBindValue(hashed_password.decode('utf-8'))
        query.addBindValue(role)

        if query.exec_():
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            Register_window.hide(self)
            self.login_win = Login_window()
            self.login_win.show()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось зарегистрировать пользователя.")

    def login_in_reg(self):
        self.login_win = Login_window()
        Register_window.close(self)
        self.login_win.show()


class Object_data(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r"design\form.ui", self)
        self.setWindowTitle("DataBase")

        # Кнопки взаимодействия с БД
        self.openDB.clicked.connect(self.open_data)
        self.closeDB.clicked.connect(self.close_data)
        self.nextDB.clicked.connect(self.next_data)
        self.lastDB.clicked.connect(self.last_data)

        # Кнопки авторизации
        self.registerDB.clicked.connect(self.reg_data)
        self.loginDB.clicked.connect(self.login_data)

        self.model = None
        self.index = 0
        self.table_list = []

    def open_data(self):
        # Открытие базы данных
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('form.db')
            # Условие: если база данных не откроется, вывести ошибку
        if not self.db.open():
            QMessageBox.critical(self, "Ошибка подключения!", "Неудалось подключиться к базе данных.")
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
        self.index = 0
        self.load_table(self.table_list[self.index])

    # закрытие базы данных
    def close_data(self):
        try:
                self.db.close()
                QMessageBox.warning(self, "Подключение разорвано", "Подключение к базе данных было успешно закрыто.")
                QSqlDatabase.removeDatabase('QSQLITE')
                self.db = None
                self.model = None
                self.tableView.setModel(None)
        except AttributeError:
            QMessageBox.critical(self, "соединение не найдено", "Подключение к базе данных уже закрыто или не установлено")

    # загрузка таблицы
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

    # следующая таблица
    def next_data(self):
        try:
            if self.index < len(self.table_list) - 1:
                self.index += 1
                self.load_table(self.table_list[self.index])
                print(f'номер страницы: {self.index}, всего страниц: {len(self.table_list)}')
            # эффект карусели    
            elif self.index + 1 == len(self.table_list):
                self.index = 0
                self.load_table(self.table_list[self.index])
        except (IndexError, TypeError):
            QMessageBox.critical(self, "Ошибка", "Соединение не установлено")
    # предыдущая таблица
    def last_data(self):
        try:
            if self.index > 0:
                self.index -= 1
                self.load_table(self.table_list[self.index])
                print(f'номер страницы: {self.index}, всего страниц: {len(self.table_list)}')
            # эффект карусели
            elif self.index == 0:
                 self.index = len(self.table_list) - 1
                 self.load_table(self.table_list[self.index])
        except (IndexError, TypeError):
            QMessageBox.critical(self, "Ошибка", "Соединение не установлено")

    def reg_data(self):
        self.reg_window = Register_window()
        self.reg_window.show()

    def login_data(self):
        self.log_window = Login_window()
        self.log_window.show()
        
        
class Admin_window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r"design\admin.ui", self)
        self.setWindowTitle("Admin_menu")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Login_window()
    win.show()
    sys.exit(app.exec_())