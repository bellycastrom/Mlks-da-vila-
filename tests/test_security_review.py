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


    def test_homonyms_have_distinct_records_and_visible_group(self):
        with tempfile.TemporaryDirectory() as folder:
            previous = app.DB_FILE
            try:
                app.DB_FILE = Path(folder) / "review.db"
                app.init_db()
                with app.connect() as con:
                    one = con.execute(
                        "INSERT INTO participantes(nome,turma) VALUES (?,?)",
                        ("Maria Silva", "Turma A"),
                    ).lastrowid
                    two = con.execute(
                        "INSERT INTO participantes(nome,turma) VALUES (?,?)",
                        ("Maria Silva", "Turma B"),
                    ).lastrowid
                    self.assertNotEqual(one, two)
                    html = app.activity_form(con, "0" * 64)
                    self.assertIn("Turma: Turma A", html)
                    self.assertIn("Turma: Turma B", html)
                    self.assertIn(f"Cadastro #{one}", html)
                    self.assertIn(f"Cadastro #{two}", html)
                    self.assertIn(f'value="{one}"', html)
                    self.assertIn(f'value="{two}"', html)
            finally:
                app.DB_FILE = previous

    def test_legacy_migration_preserves_ids_and_foreign_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            previous = app.DB_FILE
            try:
                app.DB_FILE = Path(folder) / "legacy.db"
                with sqlite3.connect(app.DB_FILE) as con:
                    con.executescript("""
                        PRAGMA foreign_keys=ON;
                        CREATE TABLE participantes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL COLLATE NOCASE UNIQUE,
                            turma TEXT NOT NULL DEFAULT '',
                            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE TABLE atividades (
                            id INTEGER PRIMARY KEY,
                            data TEXT NOT NULL
                        );
                        CREATE TABLE inscricoes (
                            atividade_id INTEGER NOT NULL,
                            participante_id INTEGER NOT NULL,
                            presente INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY (atividade_id, participante_id),
                            FOREIGN KEY (atividade_id) REFERENCES atividades(id),
                            FOREIGN KEY (participante_id) REFERENCES participantes(id)
                        );
                        INSERT INTO participantes(id,nome,turma)
                            VALUES (27,'João Santos','Turma A');
                        INSERT INTO atividades(id,data) VALUES (9,'2026-10-31');
                        INSERT INTO inscricoes(atividade_id,participante_id,presente)
                            VALUES (9,27,1);
                    """)
                app.init_db()
                with app.connect() as con:
                    original = con.execute(
                        "SELECT id,nome,turma FROM participantes WHERE id=27"
                    ).fetchone()
                    self.assertEqual(original["nome"], "João Santos")
                    self.assertEqual(original["turma"], "Turma A")
                    linked = con.execute(
                        "SELECT participante_id,presente FROM inscricoes WHERE atividade_id=9"
                    ).fetchone()
                    self.assertEqual((linked["participante_id"], linked["presente"]), (27, 1))
                    self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
                    con.execute(
                        "INSERT INTO participantes(nome,turma) VALUES (?,?)",
                        ("João Santos", "Turma B"),
                    )
            finally:
                app.DB_FILE = previous


if __name__ == "__main__":
    unittest.main()
