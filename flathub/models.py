import datetime
import sqlite3


class Application:
    scheme = """
                CREATE TABLE IF NOT EXISTS `applications` (
                    `id` INTEGER PRIMARY KEY,
                    `app_id` TEXT NOT NULL UNIQUE
                );
            """
    app_id: str
    _id: int
    _history: ['ApplicationHistory']

    def __init__(self, app_id: str, **kwargs):
        self.app_id = app_id
        self._history = kwargs.get('history', [])
        self._id = kwargs.get('id', -1)

    @staticmethod
    def all(connection: sqlite3.Connection) -> ['Application']:
        query = 'SELECT * FROM applications'

        cursor = connection.cursor()
        cursor.execute(query, ())
        rows = cursor.fetchall()
        return [Application._from_row(row, connection) for row in rows]

    @staticmethod
    def from_app_id(app_id: str, connection: sqlite3.Connection) -> 'Application':
        cursor = connection.cursor()
        query = 'SELECT * FROM applications WHERE app_id=?'
        cursor.execute(query, (app_id, ))
        row = cursor.fetchone()

        return Application._from_row(row, connection)

    @staticmethod
    def _from_row(row, connection: sqlite3.Connection):
        app = None
        if row:
            _id, app_id = row
            history = ApplicationHistory.from_app_id(_id, app_id, connection)
            app = Application(app_id, id=_id, history=history)
        return app

    def to_json(self) -> dict:
        downloads, updates = self.get_total_downloads()
        return {
            "app_id": self.app_id,
            "downloads": downloads,
            "updates": updates,
        }

    def get_total_downloads(self) -> (int, int):
        total_downloads, total_updates = 0, 0
        history = self.get_history()
        for app_history in history:
            total_downloads += app_history.downloads
            total_updates += app_history.updates
        return (total_downloads, total_updates)

    def get_history(self):
        return self._history

    def add_history(self, history: 'ApplicationHistory'):
        assert history.app_id == self.app_id
        self._history.append(history)

    def save(self, cursor: sqlite3.Cursor):
        # Insert the application data to a sqlite database
        app_query = "REPLACE INTO applications (app_id) VALUES (?)"
        cursor.execute(app_query, (self.app_id,))

        application_id = cursor.lastrowid
        records = [
            (application_id, app_history.downloads, app_history.updates, app_history.date) for app_history in self.get_history()
        ]
        history_query = "REPLACE INTO applications_history (application_id, downloads, updates, date) VALUES (?, ?, ?, ?)"
        cursor.executemany(history_query, records)


class ApplicationHistory:
    scheme = """
                CREATE TABLE IF NOT EXISTS `applications_history` (
                    `application_id` INTEGER NOT NULL,
                    `date` DATE,
                    `downloads` INTEGER DEFAULT 0,
                    `updates` INTEGER DEFAULT 0
                );
            """
    app_id: str
    _application_id: int
    date: datetime.date
    downloads: int
    updates: int

    def __init__(self, app_id: str, date: datetime.date, downloads: int, updates: int, **kwargs):
        self.app_id = app_id
        self.date = date
        self.downloads = int(downloads)
        self.updates = updates
        self._application_id = kwargs.get('id')

    @staticmethod
    def from_app_id(application_id: int, app_id: str, connection: sqlite3.Connection):
        cursor = connection.cursor()
        query = 'SELECT * FROM applications_history WHERE application_id=?'
        cursor.execute(query, (application_id, ))
        history = []

        rows = cursor.fetchall()
        for row in rows:
            history.append(
                ApplicationHistory(
                    app_id, row[1], int(row[2]), int(row[3]), id=application_id)
            )
        return history

    def __str__(self):
        return f"Application {self.app_id}'s history at {self.date}"

    def __repr__(self):
        return f"<{self.app_id}//{self.date}>"
