"""Regressões de segurança e persistência do MVP.

Execute com: python -m unittest discover -s tests -v
Os testes não usam dados da ONG: criam uma base SQLite temporária.
"""

import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
spec = importlib.util.spec_from_file_location("mlks_security_under_test", APP_PATH)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class SecurityReviewTests(unittest.TestCase):
    def test_html_output_is_escaped(self):
        malicious = '<script>alert("x")</script>'
        escaped = app.e(malicious)
        self.assertNotIn("<script>", escaped)
        self.assertEqual(escaped, "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;")

    def test_sqlite_foreign_keys_enabled(self):
        with tempfile.TemporaryDirectory() as folder:
            previous = app.DB_FILE
            try:
                app.DB_FILE = Path(folder) / "review.db"
                app.init_db()
                with app.connect() as con:
                    enabled = con.execute("PRAGMA foreign_keys").fetchone()[0]
                self.assertEqual(enabled, 1)
            finally:
                app.DB_FILE = previous

    def test_transaction_rolls_back_on_error(self):
        with tempfile.TemporaryDirectory() as folder:
            previous = app.DB_FILE
            try:
                app.DB_FILE = Path(folder) / "review.db"
                app.init_db()
                with self.assertRaisesRegex(RuntimeError, "erro intencional"):
                    with app.connect() as con:
                        con.execute(
                            "INSERT INTO participantes(nome,turma) VALUES (?,?)",
                            ("Registro temporário", "Teste"),
                        )
                        raise RuntimeError("erro intencional")
                with app.connect() as con:
                    count = con.execute(
                        "SELECT COUNT(*) FROM participantes WHERE nome=?",
                        ("Registro temporário",),
                    ).fetchone()[0]
                self.assertEqual(count, 0)
            finally:
                app.DB_FILE = previous


if __name__ == "__main__":
    unittest.main()
