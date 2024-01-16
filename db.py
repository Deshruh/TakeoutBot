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
            city TEXT NOT NULL,
            area TEXT NOT NULL,
            street TEXT NOT NULL,
            home INTEGER NOT NULL,
            flat INTEGER NOT NULL,
            orders TEXT DEFAULT NULL,
            prime INTEGER DEFAULT NULL
            )
            """
        )  # Создание таблицы Users

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Orders(
            id INTEGER PRIMARY KEY,
            description TEXT DEFAULT NULL,
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

    def add_user(self, user_id, name, city, area, street, house, flat):
        """Регистрация нового пользователя"""
        self.cursor.execute(
            "INSERT INTO Users(user_id, name, city, area, street, home, flat) VALUES (?,?,?,?,?,?,?)",
            (user_id, name, city, area, street, house, flat),
        )
        self.conn.commit()

    def add_order(self, user_id, description):
        """Сохранение завки"""
        self.cursor.execute(
            "INSERT INTO Orders(user_id, description) VALUES (?,?)",
            (user_id, description),
        )
        return self.conn.commit()

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()
