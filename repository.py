import sqlite3
from abc import ABC, abstractmethod


class Repository(ABC):
    def __init__(self, table, database='database.db'):
        self._table = table
        self._database = database
        self._con = None
        self._cur = None
        self._tableCreated = False

    def __enter__(self):
        self._con = sqlite3.connect(f'{self._database}')
        self._cur = self._con.cursor()
        if self._tableCreated is False:
            self.create_table()
            self._tableCreated = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._con.commit()
        self._con.close()

    @abstractmethod
    def create_table(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def read(self, id):
        raise NotImplementedError

    @abstractmethod
    def read_all(self):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, id):
        raise NotImplementedError

    @abstractmethod
    def count(self):
        raise NotImplementedError
