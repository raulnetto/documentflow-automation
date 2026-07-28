# DocumentFlow Automation

Pipeline de automação de documentos desenvolvido com Python e FastAPI.

O projeto foi criado como estudo prático de automação de processos, APIs REST, integração entre sistemas, processamento de documentos, OCR e workflows com N8N.

## Estado atual

### v0.5.0 — Processamento automático de documentos

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
- tratar arquivos inexistentes sem interromper a API;
- escolher automaticamente entre extração digital e OCR;
- usar PyMuPDF para PDFs com texto digital;
- encaminhar PDFs sem texto digital para o Tesseract;
- encaminhar imagens diretamente para o Tesseract;
- informar qual mecanismo foi utilizado no processamento.

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
→ processador automático identifica o tipo de arquivo
→ PDF tenta extração digital com PyMuPDF
→ PDF sem texto digital é encaminhado ao Tesseract
→ imagem é encaminhada diretamente ao Tesseract
→ TXT é salvo em output/
→ API devolve metadados e o mecanismo utilizado
```

## Endpoint automático

`POST /documentos/{nome_arquivo}/processar-automaticamente`

O endpoint escolhe o mecanismo adequado sem exigir que o usuário decida entre extração digital e OCR.

## Testes da v0.5.0

- PDF digital processado com PyMuPDF e resposta HTTP `200 OK`.
- PDF escaneado encaminhado automaticamente ao Tesseract.
- Imagem JPG encaminhada automaticamente ao Tesseract.
- Arquivo inexistente tratado com resposta HTTP `404 Not Found`.
- Retorno do mecanismo utilizado em cada processamento.

## Limitações atuais

- A precisão do OCR depende da resolução, contraste, rotação e nitidez do documento.
- O caminho do executável Tesseract está configurado para o ambiente Windows local.
- Arquivos com o mesmo nome podem sobrescrever resultados anteriores.
- Os testes ainda são manuais pelo Swagger.
- Ainda não há integração com N8N, banco de dados ou deploy.

## Próximo marco

### v0.6.0 — Registro estruturado de processamentos

O próximo estágio deverá registrar os resultados de cada execução em formato estruturado, preservando status, mecanismo, arquivos gerados, quantidade de páginas, quantidade de caracteres e eventuais erros.
