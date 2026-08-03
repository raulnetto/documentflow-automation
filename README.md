# DocumentFlow Automation

Pipeline de automação documental desenvolvida em Python com FastAPI.

O projeto recebe documentos, valida formatos, escolhe automaticamente entre extração digital e OCR, gera arquivos de texto, registra sucessos e falhas e pode ser acionado por um workflow real do N8N.

## Demonstração

![Demonstração do DocumentFlow](docs/assets/documentflow-demo.gif)

> O GIF apresenta o fluxo principal da API. A integração com N8N está documentada em [`n8n/README.md`](n8n/README.md) e pode ser reproduzida com o workflow exportado.

## Estado atual

Versão atual: **v0.9.0**

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
- preservar `origem` e `id_fluxo`;
- responder com códigos HTTP adequados;
- disponibilizar documentação OpenAPI e Swagger;
- receber solicitações externas por webhook;
- ser acionada por um workflow real do N8N;
- separar automaticamente os caminhos de sucesso e erro no N8N;
- validar os principais comportamentos com 15 testes automatizados.

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
- N8N
- Node.js e npm
- Git e GitHub

## Arquitetura atual

```text
Usuário ou automação
        │
        ▼
FastAPI / Webhook
        │
        ▼
Processador automático
   ┌────┴────┐
   ▼         ▼
PyMuPDF   Tesseract
   └────┬────┘
        ▼
    arquivo TXT
        │
        ▼
  registro JSON
```

Com N8N:

```text
Manual Trigger
→ Configurar Processamento
→ Chamar DocumentFlow
→ Validar Resposta
   ├── statusCode 200 → Resultado - Sucesso
   └── outro código  → Resultado - Erro
```

## Fluxo principal da API

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

## Endpoints principais

### Processamento automático

```text
POST /documentos/{nome_arquivo}/processar-automaticamente
```

### Webhook para automações externas

```text
POST /webhooks/processar-documento
```

Exemplo de entrada:

```json
{
  "nome_arquivo": "documento_demo.pdf",
  "origem": "n8n",
  "id_fluxo": "workflow-001"
}
```

Exemplo de resposta de sucesso:

```json
{
  "status": "processamento_concluido",
  "origem": "n8n",
  "id_fluxo": "workflow-001",
  "arquivo_origem": "documento_demo.pdf",
  "arquivo_texto": "documento_demo_ocr.txt",
  "quantidade_paginas": 1,
  "quantidade_caracteres": 1555,
  "mecanismo": "tesseract",
  "id_registro": "uuid-gerado",
  "caminho_registro": "registros/uuid-gerado.json"
}
```

O webhook trata:

- `200` — processamento concluído;
- `400` — conteúdo inválido;
- `404` — arquivo inexistente;
- `503` — mecanismo externo indisponível.

## Integração com N8N

A v0.9 adiciona um workflow real e exportável.

Arquivos:

```text
n8n/
├── README.md
└── workflows/
    └── documentflow-processamento.json
```

O workflow:

1. inicia manualmente;
2. define `nome_arquivo`, `origem` e `id_fluxo`;
3. envia uma requisição HTTP para o webhook;
4. recebe corpo, cabeçalhos e código HTTP;
5. mantém respostas de erro no fluxo com `Never Error`;
6. verifica se `statusCode == 200`;
7. produz uma saída padronizada de sucesso ou erro.

Documentação detalhada:

```text
n8n/README.md
```

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

A v0.9 mantém **15 testes automatizados**.

### API

- rota raiz retorna `200`;
- versão anunciada é `0.9.0`;
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

### Registro

- JSON é criado corretamente;
- UUID, status e campos principais são validados;
- o teste usa diretório temporário;
- arquivos reais de execução não são alterados.

Executar:

```powershell
python -m pytest -v
```

Resultado validado:

```text
15 passed
```

Existe atualmente um aviso de depreciação vindo da integração entre FastAPI, Starlette TestClient e httpx. O aviso não invalida a suíte.

## Instalação

### Dependências da aplicação

```powershell
python -m pip install -r requirements.txt
```

### Dependências de desenvolvimento

```powershell
python -m pip install -r requirements-dev.txt
```

### Dependência externa de OCR

O Tesseract OCR precisa estar instalado e configurado na máquina.

### N8N

O workflow foi executado localmente com Node.js, npm e:

```powershell
npx n8n
```

## Como executar

### 1. Ativar o ambiente Python

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Iniciar a API

```powershell
python -m uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 3. Iniciar o N8N em outro terminal

```powershell
npx n8n
```

Editor:

```text
http://localhost:5678
```

### 4. Importar o workflow

```text
Import from File
→ n8n/workflows/documentflow-processamento.json
```

### 5. Preparar um arquivo neutro de demonstração

```text
input/documento_demo.pdf
```

A pasta `input/` não é versionada.

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

n8n/
├── README.md
└── workflows/
    └── documentflow-processamento.json

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

## Privacidade

Não são versionados:

- documentos de entrada;
- arquivos TXT gerados;
- registros JSON produzidos;
- documentos pessoais;
- senhas, tokens ou credenciais.

O endereço `127.0.0.1` representa apenas o próprio computador e não expõe endereço residencial ou IP público.

## Limitações atuais

- o workflow usa gatilho manual;
- o documento precisa existir previamente em `input/`;
- API e N8N precisam estar rodando localmente;
- não há upload binário direto pelo N8N;
- não há banco de dados;
- não há autenticação;
- não há idempotência ou política de repetição;
- não há Docker;
- não há deploy público;
- não há dashboard;
- o caminho do Tesseract ainda depende da configuração local.

## Próximo marco sugerido

### v0.10 — Persistência relacional e consulta de histórico

Objetivos:

- criar uma base SQLite;
- modelar a entidade `processamento`;
- persistir sucessos e falhas no banco;
- manter compatibilidade temporária com os registros JSON;
- criar endpoints de consulta;
- filtrar por status, mecanismo, origem e `id_fluxo`;
- gerar consultas agregadas para apresentação acadêmica;
- preparar a base para relatórios e dashboard.
