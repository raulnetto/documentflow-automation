# DocumentFlow Automation

Pipeline de automação de documentos desenvolvida em Python com FastAPI.

O projeto recebe arquivos, valida o formato, armazena os documentos, escolhe automaticamente entre extração digital e OCR, gera arquivos de texto e mantém registros estruturados dos processamentos.

## Estado atual

Versão atual: **v0.7.0**

A aplicação já consegue:

- receber metadados e uploads reais;
- validar extensões e arquivos vazios;
- armazenar documentos em `input/`;
- extrair texto de PDFs digitais com PyMuPDF;
- executar OCR em imagens e PDFs escaneados com Tesseract;
- escolher automaticamente entre extração digital e OCR;
- gerar arquivos TXT em `output/`;
- registrar sucessos e falhas em JSON;
- identificar cada processamento com UUID;
- registrar data, hora, mecanismo, páginas, caracteres e mensagens de erro;
- responder com códigos HTTP adequados;
- documentar as rotas com OpenAPI e Swagger;
- validar automaticamente os principais comportamentos com pytest.

## Tecnologias

- Python
- FastAPI
- Pydantic
- Uvicorn
- PyMuPDF
- pytesseract
- Pillow
- Tesseract OCR
- pathlib
- UUID
- JSON
- OpenAPI / Swagger
- pytest
- TestClient
- monkeypatch
- tmp_path
- Git e GitHub

## Fluxo atual

```text
arquivo enviado
→ FastAPI recebe
→ extensão é validada
→ arquivo é salvo em input/
→ processador identifica o tipo
→ PDF digital usa PyMuPDF
→ PDF sem texto digital usa Tesseract OCR
→ imagem usa Tesseract OCR
→ TXT é salvo em output/
→ resultado é registrado em JSON
→ API devolve status, mecanismo e referência do registro
```

## Endpoint principal

```text
POST /documentos/{nome_arquivo}/processar-automaticamente
```

A resposta de sucesso informa:

- arquivo de origem;
- arquivo TXT gerado;
- quantidade de páginas;
- quantidade de caracteres;
- caminho do arquivo salvo;
- mecanismo utilizado;
- identificador do registro;
- caminho do registro JSON.

## Registros estruturados

Cada processamento gera um arquivo JSON em `registros/` com:

- `id`;
- `data_hora`;
- `arquivo_origem`;
- `status`;
- `mecanismo`;
- `arquivo_saida`;
- `quantidade_paginas`;
- `quantidade_caracteres`;
- `mensagem_erro`.

Os registros produzidos durante a execução são ignorados pelo Git. Apenas `registros/.gitkeep` é versionado.

## Testes automatizados

A v0.7 adiciona uma suíte com **11 testes automatizados**.

### API

- rota raiz retorna `200`;
- versão anunciada é `0.7.0`;
- processamento automático retorna `200`;
- arquivo inexistente retorna `404`;
- conteúdo inválido retorna `400`;
- indisponibilidade do Tesseract retorna `503`;
- erros geram registros estruturados.

### Processador automático

- PDF digital usa PyMuPDF;
- PDF sem texto digital faz fallback para OCR;
- imagem usa OCR diretamente;
- arquivo inexistente gera `FileNotFoundError`;
- extensão não suportada gera `ValueError`.

### Registro de processamento

- JSON é criado corretamente;
- UUID, status, mecanismo e demais campos são validados;
- testes usam diretório temporário;
- arquivos reais de `input/`, `output/` e `registros/` não são alterados.

## Como instalar

Dependências da aplicação:

```powershell
python -m pip install -r requirements.txt
```

Dependências de desenvolvimento e testes:

```powershell
python -m pip install -r requirements-dev.txt
```

O arquivo `requirements-dev.txt` inclui as dependências da aplicação e o pytest.

## Como executar os testes

```powershell
python -m pytest -v
```

Resultado validado na v0.7:

```text
11 passed
```

Existe atualmente um aviso de depreciação vindo da integração entre FastAPI, Starlette TestClient e httpx. O aviso não invalida os testes e será tratado separadamente.

## Estrutura principal

```text
app/
├── exceptions.py
├── main.py
├── models.py
└── services/
    ├── armazenamento.py
    ├── extrator_ocr.py
    ├── extrator_pdf.py
    ├── processador.py
    ├── processador_automatico.py
    └── registro_processamento.py

tests/
├── test_api.py
├── test_processador_automatico.py
└── test_registro_processamento.py

input/
output/
registros/
README.md
CHANGELOG.md
requirements.txt
requirements-dev.txt
.gitignore
```

## Fluxo de desenvolvimento

```text
main estável
→ branch da versão
→ implementação
→ testes
→ documentação
→ commit
→ merge na main
→ push
```

Branch utilizada na v0.7:

```text
feat/v0.7-testes-automatizados
```

## Limitações atuais

- caminho do Tesseract ainda depende da configuração local;
- arquivos com nomes repetidos podem sobrescrever saídas;
- não há banco de dados;
- não há autenticação;
- não há integração com N8N;
- não há webhooks externos;
- não há deploy;
- não há monitoramento contínuo;
- ainda existe um aviso de depreciação no TestClient.

## Próximo marco sugerido

### v0.8 — Webhook e integração com N8N

Objetivos:

- criar uma entrada por webhook;
- permitir que o N8N envie documentos ou comandos à API;
- tratar fluxos de sucesso e erro no N8N;
- devolver respostas estruturadas;
- preparar uma automação ponta a ponta;
- documentar o fluxo de integração entre sistemas.
