# DocumentFlow Automation

Pipeline de automação de documentos desenvolvido com Python e FastAPI.

O projeto foi criado como estudo prático de automação de processos, APIs REST, integração entre sistemas, OCR e workflows com N8N.

## Estado atual

### v0.2.0 — Upload e armazenamento de documentos

A API atualmente consegue:

- verificar se o serviço está online;
- receber metadados em JSON;
- validar extensões permitidas;
- receber arquivos reais por upload HTTP;
- armazenar documentos localmente;
- retornar nome, tamanho, tipo e caminho do arquivo;
- rejeitar formatos não permitidos;
- responder com códigos HTTP estruturados.

## Tecnologias atuais

- Python
- FastAPI
- Pydantic
- Uvicorn
- pathlib
- UploadFile
- JSON
- OpenAPI / Swagger

## Fluxo atual

```text
arquivo enviado
→ FastAPI recebe
→ extensão é validada
→ arquivo é salvo em input/
→ API devolve metadados