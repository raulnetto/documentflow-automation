# Changelog

Este arquivo registra mudanças relevantes por versão. Detalhes de instalação e uso ficam no [README](README.md).

## v0.11.0 — publicada

### Adicionado
- Backend PostgreSQL opcional via `DATABASE_URL`, usando SQLAlchemy Core e Psycopg; SQLite continua sendo o padrão.
- Stack local da API e PostgreSQL com Docker Compose, healthcheck e volume persistente para o banco.
- Teste de integração PostgreSQL e runner HOST para regressão, build frio e validação HTTP containerizada.
- Dockerfile instala Tesseract com idioma português e define o caminho do executável Linux.

### Mantido
- Persistência dos registros JSON e contratos HTTP existentes.
- Compatibilidade SQLite e seleção de PostgreSQL sem migração automática de dados históricos.

Status de publicação informado pelo responsável do projeto; não revalidado contra o serviço de hospedagem nesta sessão.

## v0.10.0
- Histórico de processamento persistido em SQLite, mantendo registros JSON.
- API FastAPI com processamento de documentos e histórico consultável.

## v0.9
- Workflow N8N real e exportável para acionar o processamento de documentos.
