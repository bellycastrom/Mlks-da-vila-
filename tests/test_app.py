"""Testes locais: python -m unittest discover -s tests -v"""
import http.cookiejar
import importlib.util
import os
import re
import sqlite3
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'app.py'
spec = importlib.util.spec_from_file_location('mlks_app', SOURCE)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class FlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        app.DB_FILE = Path(cls.temporary.name) / 'mlks.db'
        app.init_db()
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temporary.cleanup()

    def setUp(self):
        self.jar = http.cookiejar.CookieJar()
        self.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def get(self, path):
        with self.client.open(self.base + path) as response:
            return response.read().decode(), response.status

    def post(self,path,payload):
        page,_ = self.get(path if path != '/biblioteca/livros' and path != '/biblioteca/emprestimos' else '/biblioteca')
        token = re.search(r'name="_csrf" value="([0-9a-f]{64})"',page)
        if not token:
            raise AssertionError(f'No token in form for {path}')
        payload['_csrf'] = token.group(1)
        request = urllib.request.Request(self.base + path,data=urllib.parse.urlencode(payload,doseq=True).encode(),method='POST')
        try:
            with self.client.open(request) as response:
                return response.read().decode(),response.geturl()
        except urllib.error.HTTPError as exc:
            return exc.read().decode(),exc.geturl()

    def test_01_pages_and_embedded_assets(self):
        for path, keyword in [('/','Bem-vindo ao Mlks da Vila'),('/atividades/nova','Registrar atividade e presenças'),('/participantes','Novo participante'),('/biblioteca','Cadastrar livro'),('/sobre','Sobre o Mlks da Vila'),('/ajuda','Como registrar uma atividade')]:
            page,status=self.get(path)
            self.assertEqual(status,200)
            self.assertIn(keyword,page)
        with self.client.open(self.base+'/static/style.css') as response:
            self.assertEqual(response.status,200)
            self.assertEqual(response.headers.get_content_type(),'text/css')
            self.assertIn(b'.sidebar',response.read())
        with self.client.open(self.base+'/static/app.js') as response:
            self.assertEqual(response.status,200)
            self.assertIn(b'presence-counter',response.read())

    def test_02_register_activity_and_summary(self):
        for name in ('Ana Souza','Pedro Lima','Lucas Ferreira'):
            self.post('/participantes',{'nome':name,'turma':'Voluntariado'})
        with app.connect() as con:
            people = {row['nome']:row['id'] for row in con.execute('SELECT id,nome FROM participantes')}
        html,url = self.post('/atividades/nova',{'titulo':'Aula de inglês','data':'2026-10-20','descricao':'Atividade educativa para crianças e adolescentes.','presentes':[people['Ana Souza'],people['Pedro Lima']]})
        self.assertIn('Atividade salva com sucesso!',html)
        self.assertIn('2 de 3',html)
        self.assertIn('Lucas Ferreira',html)
        self.assertIn('Ausente',html)
        self.assertIn('Aula de inglês',html)
        self.assertIn('/atividades/1?salvo=1',url)

    def test_03_duplicate_and_update(self):
        with app.connect() as con:
            id_ = con.execute('SELECT id FROM atividades WHERE titulo=?',('Aula de inglês',)).fetchone()['id']
        html,url = self.post('/atividades/nova',{'titulo':'Aula de inglês','data':'2026-10-20','descricao':'', 'presentes':[]})
        self.assertIn('Esta atividade já foi registrada nessa data',html)
        self.assertEqual(url,self.base+'/atividades/nova')
        html,url = self.post(f'/atividades/{id_}/editar',{'titulo':'Aula de inglês','data':'2026-10-20','descricao':'Atualização de chamada','presentes':[]})
        self.assertIn('0 de 3',html)
        with app.connect() as con:
            self.assertEqual(con.execute('SELECT COALESCE(SUM(presente),0) FROM inscricoes WHERE atividade_id=?',(id_,)).fetchone()[0],0)

    def test_04_library_loan_return(self):
        html,url = self.post('/biblioteca/livros',{'titulo':'Livro de leitura','autor':'Professor(a)','categoria':'Educação','quantidade':'1'})
        self.assertIn('Livro de leitura',html)
        with app.connect() as con:
            book = con.execute('SELECT id FROM livros WHERE titulo=?',('Livro de leitura',)).fetchone()[0]
            person = con.execute('SELECT id FROM participantes LIMIT 1').fetchone()[0]
        html,url=self.post('/biblioteca/emprestimos',{'livro_id':book,'participante_id':person})
        self.assertIn('Empréstimos em aberto',html)
        self.assertIn('0</td>',html)
        with app.connect() as con:
            loan = con.execute('SELECT id FROM emprestimos WHERE livro_id=? AND devolvido_em IS NULL',(book,)).fetchone()[0]
        # Token from library form
        page,_=self.get('/biblioteca')
        token=re.search(r'name="_csrf" value="([0-9a-f]{64})"',page).group(1)
        request=urllib.request.Request(self.base+f'/biblioteca/emprestimos/{loan}/devolver',data=urllib.parse.urlencode({'_csrf':token}).encode(),method='POST')
        with self.client.open(request) as response:
            self.assertIn('Operação realizada com sucesso',response.read().decode())
        with app.connect() as con:
            self.assertTrue(con.execute('SELECT devolvido_em FROM emprestimos WHERE id=?',(loan,)).fetchone()[0])

if __name__=='__main__': unittest.main()
