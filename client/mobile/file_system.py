import os
import sqlite3


class FileDB:
    def __init__(self):
        db_path = os.path.join(
            os.getenv("FLET_APP_STORAGE_DATA", "."),
            "files.db",
        )

        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                display_order INTEGER NOT NULL
            )
        """)

        self.db.commit()

    # ========================================================
    # GET
    # ========================================================

    def get_all(self):
        return self.db.execute("""
            SELECT *
            FROM files
            ORDER BY display_order
        """).fetchall()

    # ========================================================
    # ADD
    # ========================================================

    def add(self, name: str, path: str):

        if self.db.execute(
            "SELECT id FROM files WHERE path = ?",
            (path,),
        ).fetchone():
            return False

        order = self.db.execute(
            """
            SELECT COALESCE(MAX(display_order), -1) + 1
            FROM files
            """
        ).fetchone()[0]

        self.db.execute(
            """
            INSERT INTO files (
                name,
                path,
                display_order
            )
            VALUES (?, ?, ?)
            """,
            (name, path, order),
        )

        self.db.commit()

        return True

    # ========================================================
    # RENAME
    # ========================================================

    def rename(self, file_id: int, new_name: str):

        self.db.execute(
            """
            UPDATE files
            SET name = ?
            WHERE id = ?
            """,
            (new_name, file_id),
        )

        self.db.commit()

    # ========================================================
    # DELETE
    # ========================================================

    def delete(self, file_id: int):

        self.db.execute(
            """
            DELETE FROM files
            WHERE id = ?
            """,
            (file_id,),
        )

        self.db.commit()

        self.save_order([
            file["id"]
            for file in self.get_all()
        ])

    # ========================================================
    # SAVE ORDER
    # ========================================================

    def save_order(self, ids):

        with self.db:

            for order, file_id in enumerate(ids):

                self.db.execute(
                    """
                    UPDATE files
                    SET display_order = ?
                    WHERE id = ?
                    """,
                    (order, file_id),
                )