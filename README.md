# DocumentFlow Automation

Pipeline de automação de documentos desenvolvida em Python com FastAPI.

O projeto recebe arquivos, valida formatos, armazena documentos, escolhe automaticamente entre extração digital e OCR, gera arquivos de texto, mantém registros estruturados e aceita chamadas externas por webhook com rastreabilidade de origem e fluxo.

## Demonstração

![Demonstração do DocumentFlow](docs/assets/documentflow-demo.gif)

## Estado atual

Versão atual: **v0.8.0**

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
- validar automaticamente os principais comportamentos com pytest;
- receber solicitações externas por webhook;
- preservar `origem` e `id_fluxo`;
- devolver respostas estruturadas para automações como N8N.

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

## Fluxo principal

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

## Processamento automático

Endpoint:

```text
POST /documentos/{nome_arquivo}/processar-automaticamente
```

## Webhook para automações externas

Endpoint:

```text
POST /webhooks/processar-documento
```

Exemplo de entrada:

```json
{
  "nome_arquivo": "sistemas_crm.pdf",
  "origem": "n8n",
  "id_fluxo": "workflow-001"
}
```

Fluxo:

```text
N8N ou outro sistema envia JSON
→ Pydantic valida o contrato
→ API localiza o arquivo em input/
→ processamento automático é executado
→ sucesso ou falha é registrado
→ origem e id_fluxo são preservados
→ resposta estruturada volta para a automação
```

O webhook trata:

- `200` para processamento concluído;
- `400` para conteúdo inválido;
- `404` para arquivo inexistente;
- `503` para indisponibilidade do mecanismo externo.

## Registros estruturados

Cada processamento gera um arquivo JSON em `registros/` com:

- `id`;
- `data_hora`;
- `arquivo_origem`;
- `origem`;
- `id_fluxo`;
- `status`;
- `mecanismo`;
- `arquivo_saida`;
- `quantidade_paginas`;
- `quantidade_caracteres`;
- `mensagem_erro`.

Os registros produzidos durante a execução são ignorados pelo Git. Apenas `registros/.gitkeep` é versionado.

## Testes automatizados

A v0.8 possui **15 testes automatizados**.

### API

- rota raiz retorna `200`;
- versão anunciada é `0.8.0`;
- processamento automático retorna `200`, `400`, `404` e `503`;
- webhook retorna `200`, `400`, `404` e `503`;
- webhook preserva `origem` e `id_fluxo`;
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
- arquivos reais não são alterados.

## Como instalar

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Como executar os testes

```powershell
python -m pytest -v
```

Resultado validado na v0.8:

```text
15 passed
```

## Como executar a API

```powershell
python -m uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

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

docs/
└── assets/
    └── documentflow-demo.gif

input/
output/
registros/
README.md
CHANGELOG.md
requirements.txt
requirements-dev.txt
.gitignore
```

## Limitações atuais

- o webhook recebe o nome de um arquivo já armazenado em `input/`;
- o envio binário direto pelo N8N ainda não foi implementado;
- a integração visual dentro do N8N ainda não foi montada;
- o caminho do Tesseract depende da configuração local;
- arquivos com nomes repetidos podem sobrescrever saídas;
- não há banco de dados;
- não há autenticação;
- não há deploy;
- não há monitoramento contínuo;
- permanece um aviso de depreciação no TestClient.

## Próximo marco sugerido

### v0.9 — Fluxo real no N8N

Objetivos:

- criar um workflow no N8N;
- disparar o webhook do DocumentFlow;
- tratar respostas de sucesso e falha;
- preservar `id_fluxo` entre os nós;
- gerar uma saída útil para outra etapa;
- documentar o fluxo ponta a ponta.
