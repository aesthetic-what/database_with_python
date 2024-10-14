import sqlite3


connect = sqlite3.connect('test.db')
cursor = connect.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS Users(
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    age INTEGER)
    """)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS Orders(
    order_id INTEGER PRIMARY KEY,
    order_date TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE)
    """)
connect.commit()

def add_user():
    username_input = input('Введите свое имя: ')
    password_input = input('Введите пароль: ')
    age_input = int(input('Введите свой возраст: '))

    cursor.execute("""INSERT INTO Users (username, password, age) VALUES (?, ?, ?)""", (username_input, password_input, age_input))
    connect.commit()
    print(f'Пользователь {username_input} c возрастом {age_input}, добавлен')
    return cursor.lastrowid

def add_order(user_id):
    order_date = input('введите дату заказа (YYYY-MM-DD): ')

    cursor.execute("""INSERT INTO Orders(order_date, user_id) VALUES (?, ?)""", (order_date, user_id))
    connect.commit()
    return cursor.lastrowid

def login():
    input('Введите имя пользователя: ')
    password = input('Введите пароль: ')

    cursor.execute("""SELECT password FROM Users WHERE username = ?""", (password, ))

    cursor.execute("""SELECT Users.username, Users.age, Orders.order_date FROM Orders JOIN Users ON Users.user_id = Orders.user_id""")
    rows = cursor.fetchall()
    for i in rows:
        print(i)


func = input('Войти(В) / Регистрация(Р)\n')
if func.lower() == 'р':
    user_id = add_user()
    add_order(user_id)


if func.lower() == 'в':
    login()
    
connect.close()



