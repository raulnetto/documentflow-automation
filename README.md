# DocumentFlow Automation

Pipeline de automação de documentos desenvolvido com Python e FastAPI.

O projeto foi criado como estudo prático de automação de processos, APIs REST, integração entre sistemas, processamento de documentos, OCR e workflows com N8N.

## Estado atual

### v0.4.0 — OCR de imagens e PDFs escaneados

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
- retornar respostas HTTP estruturadas para sucesso e falha;
- executar OCR em imagens JPG, JPEG e PNG;
- executar OCR em PDFs escaneados;
- reconhecer texto em português e inglês;
- gerar arquivos TXT com o texto reconhecido por OCR;
- rejeitar imagens sem texto reconhecível;
- tratar arquivos inexistentes sem interromper a API.

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
- pytesseract
- Pillow
- Tesseract OCR

## Fluxo atual

```text
arquivo enviado
→ FastAPI recebe
→ extensão é validada
→ arquivo é salvo em input/
→ PDF é analisado
→ texto digital é extraído
→ quando necessário, imagem ou PDF escaneado passa por OCR
→ TXT é salvo em output/
→ API devolve metadados da extração
```
