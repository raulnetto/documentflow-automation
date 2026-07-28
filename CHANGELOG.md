# Changelog

Todas as mudanças relevantes do projeto serão registradas neste arquivo.

## v0.4.0 — OCR de imagens e PDFs escaneados

### Adicionado

- Dependências `pytesseract` e `Pillow`.
- Integração com o motor externo Tesseract OCR.
- Serviço `app/services/extrator_ocr.py`.
- Modelo de resposta `OCRResposta`.
- Endpoint `POST /documentos/{nome_arquivo}/ocr`.
- OCR de arquivos PNG, JPG e JPEG.
- OCR de PDFs escaneados.
- Reconhecimento de texto em português e inglês.
- Renderização das páginas de PDFs em imagem com PyMuPDF.
- Geração de arquivos TXT na pasta `output/`.
- Retorno da quantidade de páginas e caracteres reconhecidos.
- Tratamento de arquivos inexistentes.
- Tratamento de imagens inválidas.
- Tratamento de OCR sem texto reconhecido.
- Tratamento da ausência do executável Tesseract.

### Validado

- OCR de PDF escaneado com texto.
- OCR de imagem JPG.
- Reconhecimento de 1.097 caracteres em uma imagem.
- Geração de arquivos TXT legíveis.
- Resposta HTTP `200 OK` para OCR concluído.
- Resposta HTTP `404 Not Found` para arquivo inexistente.
- Resposta HTTP `400 Bad Request` para imagem sem texto.
- Rejeição de arquivo TXT durante o upload.
- Preservação dos fluxos anteriores de upload e extração digital.

### Decisões técnicas

- O executável do Tesseract foi configurado por caminho explícito porque não estava disponível no `PATH` do Windows.
- O OCR utiliza os idiomas `por+eng`.
- PDFs escaneados são renderizados em resolução ampliada antes do reconhecimento.
- A validação considera apenas texto efetivamente reconhecido, evitando falsos positivos em imagens sem conteúdo.

### Limitações conhecidas

- A precisão depende da resolução, contraste, rotação e nitidez do documento.
- O caminho do Tesseract ainda está configurado para o ambiente Windows local.
- Ainda não há escolha automática entre extração digital e OCR.
- Os testes atuais são manuais pelo Swagger.
- Arquivos de saída ainda não possuem identificador único.
- Arquivos com o mesmo nome podem sobrescrever versões anteriores.

## v0.3.0 — Extração de texto de PDFs digitais

### Adicionado

- Dependência `PyMuPDF`.
- Serviço `app/services/extrator_pdf.py`.
- Modelo de resposta `ExtracaoResposta`.
- Endpoint `POST /documentos/{nome_arquivo}/extrair-texto`.
- Leitura de PDFs previamente armazenados na pasta `input/`.
- Contagem da quantidade de páginas.
- Contagem da quantidade de caracteres extraídos.
- Geração de arquivo TXT na pasta `output/`.
- Tratamento de arquivos inexistentes.
- Identificação de PDFs sem camada de texto digital.
- Tratamento de PDFs inválidos ou corrompidos.

### Validado

- Extração de texto de um PDF digital com 11 páginas.
- Extração de 14.943 caracteres.
- Geração de arquivo TXT legível.
- Resposta HTTP `200 OK` para extração bem-sucedida.
- Resposta HTTP `404 Not Found` para arquivo inexistente.
- Resposta HTTP `400 Bad Request` para PDF composto apenas por imagem.
- Mensagem indicando que o documento exige OCR.

### Bug identificado e corrigido

- A primeira implementação adicionava cabeçalhos de página antes de verificar se havia texto real.
- Cabeçalhos como `--- Página 1 ---` poderiam ser confundidos com conteúdo extraído.
- A validação foi refatorada para separar o texto real do texto formatado.
- PDFs escaneados passaram a ser identificados corretamente, sem falso positivo.

### Limitações conhecidas

- Ainda não há OCR.
- Imagens ainda não são processadas.
- PDFs escaneados são identificados, mas ainda não têm o texto extraído.
- Os testes atuais são manuais pelo Swagger.
- Arquivos de saída ainda não possuem identificador único.
- Arquivos com o mesmo nome podem sobrescrever versões anteriores.

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