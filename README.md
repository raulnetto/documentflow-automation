# DocumentFlow Automation

Pipeline de automação de documentos desenvolvido com Python e FastAPI.

O projeto foi criado como estudo prático de automação de processos, APIs REST, integração entre sistemas, processamento de documentos, OCR e workflows com N8N.

## Estado atual

### v0.3.0 — Extração de texto de PDFs digitais

A API atualmente consegue:

- verificar se o serviço está online;
- receber metadados em JSON;
- validar extensões permitidas;
- receber arquivos reais por upload HTTP;
- armazenar documentos localmente;
- extrair texto de PDFs digitais;
- contar páginas e caracteres extraídos;
- gerar arquivos TXT com o conteúdo do documento;
- identificar PDFs sem camada de texto;
- diferenciar documentos digitais de documentos que exigem OCR;
- retornar respostas HTTP estruturadas para sucesso e falha.

## Tecnologias atuais

- Python
- FastAPI
- Pydantic
- Uvicorn
- PyMuPDF
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
→ PDF é analisado
→ texto digital é extraído
→ TXT é salvo em output/
→ API devolve metadados da extração