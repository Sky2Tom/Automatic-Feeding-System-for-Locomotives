import pyodbc
from PyQt5.QtWidgets import QMessageBox

class TrainDatabaseManager:
    def __init__(self, server, database, username, password,
                 driver="{ODBC Driver 17 for SQL Server}", timeout=5):
        self.server   = server
        self.database = database
        self.username = username
        self.password = password
        self.driver   = driver
        self.timeout  = timeout

    def _connect(self):
        conn_str = (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            "TrustServerCertificate=Yes;"
        )
        return pyodbc.connect(conn_str, autocommit=False, timeout=self.timeout)

    @staticmethod
    def _q(identifier: str) -> str:
        """
        安全转义 SQL Server 标识符：把 ] 转成 ]]
        然后用 [ ... ] 包起来，适用于架构、表名、列名（不要用于值）
        """
        return f"[{identifier.replace(']', ']]')}]"

    def query_all(self, schema: str, table: str):
        """
        SELECT * FROM [schema].[table]
        """
        sql = f"SELECT * FROM {self._q(schema)}.{self._q(table)}"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description]
        return columns, rows

    def query_by_id(self, schema: str, table: str, id_column: str, value: str):
        """
        SELECT * FROM [schema].[table] WHERE [id_column] = ?
        """
        sql = (
            f"SELECT * FROM {self._q(schema)}.{self._q(table)} "
            f"WHERE {self._q(id_column)} = ?"
        )
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, (value,))
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description]
        return columns, rows
    
    def insert_row(self, schema: str, table: str, data: dict):
        """
        INSERT INTO [schema].[table] ([c1],[c2],...) VALUES (?,?,...)
        data: {column: value}
        """
        if not data:
            raise ValueError("data 为空，无法插入。")
        cols = ", ".join(self._q(k) for k in data.keys())
        placeholders = ", ".join("?" for _ in data)
        sql = (
            f"INSERT INTO {self._q(schema)}.{self._q(table)} "
            f"({cols}) VALUES ({placeholders})"
        )
        with self._connect() as conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, tuple(data.values()))
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def update_row_by_id(self, schema: str, table: str, id_column: str, id_value, data: dict):
        """
        UPDATE [schema].[table] SET [c2]=?,[c3]=? ... WHERE [id_column]=?
        data: 不包含主键列；只更新提供的列
        """
        if not data:
            raise ValueError("data 为空，未提供需要更新的列。")
        set_clause = ", ".join(f"{self._q(k)}=?" for k in data.keys())
        sql = (
            f"UPDATE {self._q(schema)}.{self._q(table)} "
            f"SET {set_clause} "
            f"WHERE {self._q(id_column)} = ?"
        )
        params = list(data.values()) + [id_value]
        with self._connect() as conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, params)
                if cur.rowcount == 0:
                    raise ValueError("未找到需要更新的 TrainTypeID。")
                conn.commit()
            except Exception:
                conn.rollback()
                raise
