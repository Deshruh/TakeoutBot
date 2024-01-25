import sqlite3


class BotDB:
    def __init__(self, db_file):
        """Создание БД и инициализация соединения с ней"""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            "PRAGMA foreign_keys=on"
        )  # необходимо включить для поддержки ON DELETE CASCADE и т.п. команд

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users(
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            adress TEXT NOT NULL,
            prime INTEGER DEFAULT 1
            )
            """
        )  # Создание таблицы Users

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Orders(
            id INTEGER PRIMARY KEY,
            status TEXT DEFAULT 'active',
            description TEXT DEFAULT NULL,
            date TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
            )
            """
        )  # Создание таблицы Orders

        self.conn.commit()

    def user_exist(self, user_id):
        """Проверка на наличие пользователя в БД"""
        check = self.cursor.execute(
            'SELECT "user_id" FROM "Users" WHERE "user_id" = ?', (user_id,)
        )
        return bool(len(check.fetchall()))

    def add_user(self, user_id, name, adress):
        """Регистрация нового пользователя"""
        self.cursor.execute(
            "INSERT INTO Users(user_id, name, adress) VALUES (?,?,?)",
            (user_id, name, adress),
        )
        self.conn.commit()

    def edit_user(self, user_id, name, adress):
        """Изменить данные пользователя"""
        self.cursor.execute(
            "UPDATE Users set name=?, adress=? where user_id=?",
            (name, adress, user_id),
        )
        self.conn.commit()

    def prime(self, user_id, prime):
        """Изменение Prime-статуса"""
        self.cursor.execute(
            "UPDATE Users set prime = ? where user_id=?",
            (prime, user_id),
        )
        self.conn.commit()

    def data_user(self, user_id):
        """Извлечения данных клиента"""
        data = self.cursor.execute(
            'SELECT * FROM "Users" WHERE "user_id" = ?', (user_id,)
        )
        return data.fetchall()

    def order_exist(self, user_id):
        """Проверка на наличие активного заказа у клиента в БД"""
        data = self.cursor.execute(
            'SELECT "status" FROM "Orders" WHERE "user_id" = ? and "status" = "active"',
            (user_id,),
        )
        return bool(len(data.fetchall()))

    def add_order(self, user_id, description, date):
        """Сохранение завки"""
        self.cursor.execute(
            "INSERT INTO Orders(user_id, description, date) VALUES (?,?,?)",
            (user_id, description, date),
        )
        return self.conn.commit()

    def data_order(self, user_id=None, status=None):
        """Извлечения данных о заказе"""
        if user_id == None and status == None:
            data = self.cursor.execute('SELECT * FROM "Orders"')  # все активные заказы
        elif user_id == None and status == "active":
            data = self.cursor.execute(
                'SELECT * FROM "Orders" WHERE "status" = "active"'
            )  # все активные заказы
        elif user_id == None and status == "finished":
            data = self.cursor.execute(
                'SELECT * FROM "Orders" WHERE "status" = "finished"'
            )  # все активные заказы
        elif status == "finished":
            data = self.cursor.execute(
                'SELECT * FROM "Orders" WHERE "user_id" = ? and "status" = "finished"',
                (user_id,),
            )  # только завершенные заказы конкретного клиента
        elif status == "active":
            data = self.cursor.execute(
                'SELECT * FROM "Orders" WHERE "user_id" = ? and "status" = "active"',
                (user_id,),
            )  # только активные заказы конкретного клиента
        else:
            data = self.cursor.execute(
                'SELECT * FROM "Orders" WHERE "user_id" = ?',
                (user_id,),
            )  # все заказы конкретного клиента

        return data.fetchall()

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()
