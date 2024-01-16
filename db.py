import sqlite3

from repository import Repository


class Database(Repository):
    """
    A class used to interact with the database containing {self._table}.

    Attributes:
        con (sqlite3.Connection): Connection to the SQLite database.
        cur (sqlite3.Cursor): Cursor object used to execute SQL commands.
    """

    def __init__(self, table) -> None:
        """
        Initializes the Database class by connecting to the SQLite database
        and creating the '{self._table}' table if it does not exist.
        """
        super().__init__(table)
        
    def create_table(self) -> None:
        self._cur.execute(f"""CREATE TABLE IF NOT EXISTS {self._table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact TEXT,
            author TEXT,
            timestamp TEXT
        )""")

    def create(self, fact: str, author: str, timestamp: str) -> None:
        """
        Adds a new fact to the database.

        Parameters:
            fact (str): The fact to be added.
            author (str): The author of the fact.
            timestamp (str): The timestamp when the fact was added.
        """
        fact_exists = self._cur.execute(f"SELECT * FROM {self._table} where fact = ?", (fact,)).fetchone()
        if fact_exists:
            return
        self._cur.execute(f"INSERT INTO {self._table} (fact, author, timestamp) VALUES (?, ?, ?)", (fact, author, timestamp))

    def read_all(self) -> list:
        """
        Retrieves all {self._table} from the database.

        Returns:
            list: A list of tuples containing all {self._table} in the database.
        """
        return self._cur.execute(f"SELECT * FROM {self._table}").fetchall()

    def count(self) -> int:
        """
        Counts the total number of {self._table} in the database.

        Returns:
            int: The total number of {self._table}.
        """
        return self._cur.execute(f"SELECT COUNT(*) FROM {self._table}").fetchone()[0]

    def read(self, id: int) -> tuple:
        """
        Retrieves a specific fact by its ID.

        Parameters:
            id (int): The ID of the fact to retrieve.

        Returns:
            tuple: A tuple containing the fact with the specified ID.
        """
        return self._cur.execute(f"SELECT * FROM {self._table} WHERE id = ?", (id,)).fetchone()

    def update(self, id: int, fact: str) -> None:
        """
        Updates the text of an existing fact.

        Parameters:
            id (int): The ID of the fact to update.
            fact (str): The new text of the fact.
        """
        self._cur.execute(f"""UPDATE {self._table} SET fact = ? WHERE id = ?""", (fact, id))

    def delete(self, id: int) -> None:
        """
        Deletes an existing fact.

        Parameters:
            id (int): The ID of the fact to delete.
        """
        self._cur.execute(f"""DELETE FROM {self._table} WHERE id = ?""", (id,))
