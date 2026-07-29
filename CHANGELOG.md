# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

## [0.6.0] - 2026-07-29

### Adicionado

- serviço `app/services/registro_processamento.py`;
- geração de UUID por processamento;
- data e hora com fuso local;
- persistência de resultados em JSON;
- campos de status, mecanismo, arquivos, páginas, caracteres e mensagem de erro;
- retorno de `id_registro` e `caminho_registro`;
- pasta `registros/`;
- arquivo `registros/.gitkeep`;
- regras no `.gitignore` para não versionar registros gerados.

### Alterado

- a rota automática passou a registrar processamentos concluídos;
- erros `404`, `400` e `503` passaram a gerar registros persistentes;
- o modelo de resposta passou a devolver a referência do registro.

### Validado

- PDF digital gerou registro de sucesso;
- arquivo inexistente retornou `404` e gerou JSON;
- imagem sem texto retornou `400` e gerou JSON;
- indisponibilidade simulada do Tesseract retornou `503` e gerou JSON;
- caminho correto do Tesseract foi restaurado;
- sintaxe validada com `py_compile`;
- aplicação importada com sucesso;
- registros de teste permaneceram ignorados pelo Git.

### Decisões técnicas

- um JSON independente é criado por execução;
- UUID evita colisão entre registros;
- horário é armazenado em ISO 8601 com fuso;
- registros de execução não são enviados ao repositório;
- o serviço de registro foi separado da rota.

### Limitações

- não existe endpoint para consultar o histórico;
- registros ainda não são consolidados;
- não há rotação ou limpeza automática;
- ainda não existem testes automatizados.

## [0.5.0] - 2026-07-29

### Adicionado

- exceção `DocumentoSemTextoDigitalError`;
- arquivo `app/exceptions.py`;
- serviço `app/services/processador_automatico.py`;
- modelo `ProcessamentoAutomaticoResposta`;
- endpoint de processamento automático;
- fallback de PyMuPDF para Tesseract;
- OCR direto para imagens;
- campo com o mecanismo utilizado.

### Validado

- PDF digital com PyMuPDF;
- PDF escaneado com Tesseract;
- imagem com Tesseract;
- arquivo inexistente com `404`.

## [0.4.0]

### Adicionado

- OCR com Tesseract;
- suporte a PNG, JPG e JPEG;
- OCR de PDFs escaneados;
- reconhecimento em português e inglês;
- geração de TXT;
- tratamento de imagem inválida;
- resposta `503` para indisponibilidade do mecanismo.

## [0.3.0]

### Adicionado

- extração de PDFs digitais com PyMuPDF;
- contagem de páginas e caracteres;
- geração de TXT;
- tratamento de arquivo inexistente;
- identificação de PDF sem texto digital.

### Corrigido

- cabeçalhos do TXT deixaram de contar como texto real;
- PDFs escaneados deixaram de gerar falso positivo.

## [0.2.0]

### Adicionado

- upload real;
- armazenamento em `input/`;
- sanitização do nome;
- cálculo do tamanho;
- rejeição de arquivo vazio;
- resposta `201`.

## [0.1.0]

### Adicionado

- aplicação FastAPI;
- rota de verificação;
- recebimento de metadados;
- modelos Pydantic;
- validação de extensões;
- documentação Swagger;
- tratamento inicial de erros.
