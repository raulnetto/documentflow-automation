# Changelog

Todas as mudanças relevantes do projeto serão registradas neste arquivo.

## v0.2.0 — Upload e armazenamento de documentos

### Adicionado

- Endpoint `POST /documentos/upload`.
- Recebimento de arquivos por `multipart/form-data`.
- Validação de extensões permitidas.
- Armazenamento local na pasta `input/`.
- Sanitização básica do nome do arquivo.
- Cálculo do tamanho do arquivo em bytes.
- Modelo de resposta `UploadResposta`.
- Tratamento de arquivos vazios.
- Resposta HTTP `201 Created` para uploads válidos.

### Validado

- Upload real de um arquivo PDF.
- Persistência do PDF na pasta `input/`.
- Retorno de nome, tipo de conteúdo, tamanho e caminho.
- Rejeição de arquivo TXT.
- Resposta HTTP `400 Bad Request` para extensão inválida.
- Arquivo rejeitado não foi armazenado.

### Limitações conhecidas

- O conteúdo interno do arquivo ainda não é validado.
- Ainda não há extração de texto ou OCR.
- Arquivos com o mesmo nome podem sobrescrever versões anteriores.
- Os testes atuais são manuais pelo Swagger.

## v0.1.0 — Contrato inicial da API

### Adicionado

- Aplicação FastAPI.
- Endpoint `GET /`.
- Endpoint `POST /documentos/processar`.
- Modelos Pydantic de entrada e saída.
- Validação de extensões por regra de negócio.
- Tratamento de `ValueError` como resposta HTTP `400`.
- Documentação automática em `/docs`.

### Validado

- Metadados de PDF aceitos com HTTP `202 Accepted`.
- Metadados de XLSX rejeitados com HTTP `400 Bad Request`.