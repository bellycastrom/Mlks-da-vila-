# Mlks da Vila — Auto-revisão técnica do MVP

## Escopo
Revisão da implementação existente nas modalidades Python/SQLite (execução local)
e HTML/CSS/JavaScript (demonstração estática no GitHub Pages).
O PR propõe melhorias de rastreabilidade e segurança; **não realiza deploy do backend**.

## Arquitetura e refatoração
- O `app.py` contém servidor HTTP, rotas, HTML renderizado e acesso ao banco em um arquivo.
  Essa decisão reduz dependências e simplifica a demonstração acadêmica, mas aumenta o
  acoplamento. Separar `handlers`, `views` e `database` é uma evolução recomendada,
  ainda **não implementada** neste PR.
- `connect()` usa `contextmanager` para habilitar chaves estrangeiras, dar
  `commit` em caso de sucesso, `rollback` em caso de exceção e fechar a conexão.
- Adicionados testes de regressão para integridade referencial, escaping HTML
  e rollback transacional, além de GitHub Actions para executá-los no PR.

## Segurança
- O backend apresenta sanitização de saída via `e()`/`html.escape`,
  operações SQL parametrizadas e token CSRF nos formulários.
- O banco `dados/mlks_da_vila.db` estava versionado no repositório público.
  Este PR propõe retirar o arquivo da versão atual e impede novos commits
  acidentais de bases locais via `.gitignore`. **A remoção não apaga cópias
  existentes no histórico Git**; é necessária revisão do histórico e, se
  houver dados pessoais reais, análise e tratamento de incidente.
- O aplicativo local não possui autenticação, autorização por perfil ou
  configuração de produção endurecida. **Não expor o backend na internet**
  antes de implementar autenticação, revisão de segurança e persistência segura.
- A versão GitHub Pages é estática e usa armazenamento no navegador, sem
  sincronização entre dispositivos; não equivale ao backend Python em nuvem.

## Validação
```bash
python -m unittest discover -s tests -v
```

Verificar a execução do workflow no GitHub Actions antes do merge.
Nenhuma alteração foi mesclada na branch `main` por este PR.
