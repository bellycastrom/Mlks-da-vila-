"""Adiciona dados FICTÍCIOS opcionais usados no protótipo de referência."""
from app import init_db, connect

init_db()
with connect() as db:
    for name in ('Ana Souza', 'Pedro Lima', 'Lucas Ferreira'):
        db.execute('INSERT OR IGNORE INTO participantes(nome,turma) VALUES (?,?)', (name, 'Demonstração'))
    activity = db.execute('SELECT id FROM atividades WHERE titulo=? COLLATE NOCASE AND data=?', ('Aula de inglês', '2026-10-20')).fetchone()
    if activity:
        activity_id = activity['id']
        print('A atividade fictícia já existe; mantive o registro existente.')
    else:
        activity_id = db.execute('''INSERT INTO atividades
            (titulo,data,horario,responsavel,local,categoria,descricao,presenca_registrada)
            VALUES (?,?, '', '', '', 'Educação', ?, 1)''',
            ('Aula de inglês','2026-10-20','Atividade educativa para crianças e adolescentes.')).lastrowid
        for p in db.execute('SELECT id,nome FROM participantes WHERE nome IN (?,?,?)',('Ana Souza','Pedro Lima','Lucas Ferreira')):
            db.execute('INSERT OR IGNORE INTO inscricoes(atividade_id,participante_id,presente) VALUES (?,?,?)',
                       (activity_id,p['id'],1 if p['nome'] != 'Lucas Ferreira' else 0))
        print('Participantes e atividade fictícia de demonstração criados.')
print('Abra http://127.0.0.1:8000 e consulte Atividades e Presenças.')
