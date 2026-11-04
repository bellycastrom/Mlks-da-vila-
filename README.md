# Mlks da Vila — sistema comunitário em Python

Implementação fiel às três telas de referência do projeto acadêmico:

1. **Início:** barra lateral azul-marinho e dois cartões centrais (Atividades e Presenças / Biblioteca).
2. **Registrar atividade e presenças:** nome, data e descrição da atividade; tabela de participantes com caixas de seleção e contador atualizado automaticamente.
3. **Resultado do registro:** aviso de sucesso, resumo da atividade, total de presentes e ausentes, tabela individual e ações de navegação.

Além das três telas, o sistema inclui **cadastro de participantes**, **listagem/edição de atividades** e **biblioteca com empréstimos e devoluções**. Não usa serviços externos.

## Abrir no VS Code (Windows)

1. Extraia o ZIP para uma pasta de sua escolha.
2. Abra a pasta no VS Code.
3. No terminal, rode:

   ```powershell
   py app.py
   ```

   Se `py` não funcionar, use `python app.py`.
4. Acesse **http://127.0.0.1:8000**.
5. Encerre o servidor com **Ctrl+C**.

Você também pode executar o arquivo `iniciar_windows.bat`.

**Requisitos:** Python 3.10 ou superior. Não é necessário instalar pacotes.

## Preciso copiar toda a pasta?

Não necessariamente. O `app.py` contém uma **cópia interna do CSS e do JavaScript** e funciona sozinho. Os arquivos `static/style.css` e `static/app.js` estão no ZIP apenas para facilitar a edição visual. Quando a pasta `static` existe, seus arquivos têm prioridade.

## Preservar os dados da versão anterior

Se você já cadastrou pessoas, atividades ou livros na versão antiga, **faça backup antes de trocar arquivos**. Para preservar os registros, mantenha a pasta `dados` e seu arquivo `mlks_da_vila.db` ao lado do novo `app.py`:

```text
mlks_da_vila/
├── app.py
├── dados/
│   └── mlks_da_vila.db  ← preservar
├── static/
│   ├── style.css
│   └── app.js
└── README.md
```

O banco continua em SQLite. O projeto cria automaticamente as tabelas novas, inclusive a de empréstimos, sem apagar os registros antigos.

## Participantes e demonstração

No primeiro uso, entre em **Atividades e Presenças → Gerenciar participantes** para cadastrar pessoas. Depois, abra **Registrar atividade**, marque os presentes e clique em **Salvar atividade e presenças**. Participantes não marcados serão registrados como ausentes.

Para preencher dados **fictícios** iguais aos apresentados nos prints, execute voluntariamente:

```powershell
py popular_exemplo.py
```

Esse comando cria Ana Souza, Pedro Lima e Lucas Ferreira e a atividade fictícia “Aula de inglês”, com dois presentes e um ausente. Os exemplos não são adicionados automaticamente ao sistema.

## Armazenamento e segurança

- Banco de dados: `dados/mlks_da_vila.db` (persistente entre execuções).
- Dados recebidos são validados no servidor; HTML é escapado; formulários têm token CSRF.
- O servidor escuta em **127.0.0.1** por padrão, para uso local e apresentação acadêmica.
- **Não publique esse servidor diretamente na internet** sem adicionar autenticação, controle de permissões, HTTPS e uma infraestrutura adequada.

## Testes automatizados

```powershell
py -m unittest discover -s tests -v
```

Os testes exercitam abertura de páginas e ativos, cadastro de participantes, atividade com presentes/ausentes, prevenção de duplicação, edição de presenças e empréstimo/devolução.

## Identidade visual

O CSS foi construído a partir dos **prints de referência enviados pelo usuário**: menu lateral escuro, fundo claro, cartões brancos, botões azuis/verdes, banner verde de confirmação e indicadores acessíveis com cor **e texto/ícone**.
