# DocumentFlow Automation

Pipeline de automação de documentos desenvolvida em Python com FastAPI.

## Estado atual

Versão atual: **v0.6**

A aplicação já consegue:

- receber metadados e uploads reais;
- validar extensões e arquivos vazios;
- armazenar documentos em `input/`;
- extrair texto de PDFs digitais com PyMuPDF;
- executar OCR em imagens e PDFs escaneados com Tesseract;
- escolher automaticamente entre extração digital e OCR;
- gerar TXT em `output/`;
- registrar sucessos e falhas em JSON;
- identificar cada processamento com UUID;
- registrar data, hora, mecanismo, páginas, caracteres e mensagens de erro;
- responder com códigos HTTP adequados;
- documentar as rotas com OpenAPI e Swagger.

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

## Validações da v0.6

Foram testados:

- PDF digital com registro de sucesso;
- erro `404` para arquivo inexistente;
- erro `400` para imagem sem texto;
- erro `503` com indisponibilidade simulada do Tesseract;
- criação de JSON para sucesso e falhas;
- restauração do caminho correto do Tesseract;
- validação com `py_compile`;
- importação completa da aplicação;
- proteção dos registros pelo `.gitignore`.

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

input/
output/
registros/
README.md
CHANGELOG.md
requirements.txt
.gitignore
```

## Limitações atuais

- testes ainda são majoritariamente manuais;
- caminho do Tesseract ainda depende da configuração local;
- arquivos com nomes repetidos podem sobrescrever saídas;
- não há banco de dados;
- não há autenticação;
- não há integração com N8N;
- não há webhooks;
- não há deploy;
- não há monitoramento contínuo.

## Próximo marco sugerido

### v0.7 — Testes automatizados

Objetivos:

- configurar `pytest`;
- testar serviços isoladamente;
- testar endpoints FastAPI;
- validar fluxos de sucesso e falha;
- usar arquivos temporários;
- eliminar dependência de documentos pessoais nos testes;
- criar uma base segura para futuras refatorações.
