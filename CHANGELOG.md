# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

## [0.8.0] - 2026-07-31

### Adicionado

- modelos `WebhookProcessamentoEntrada` e `WebhookProcessamentoResposta`;
- endpoint `POST /webhooks/processar-documento`;
- contrato JSON para chamadas externas;
- suporte aos campos `origem` e `id_fluxo`;
- rastreabilidade de chamadas vindas de automações externas;
- persistência de `origem` e `id_fluxo` nos registros JSON;
- resposta estruturada para integrações como N8N;
- quatro testes automatizados do webhook;
- cobertura dos cenários `200`, `400`, `404` e `503`;
- validação de rastreabilidade em sucesso e falha;
- suíte ampliada de 11 para 15 testes.

### Alterado

- versão da API atualizada de `0.7.0` para `0.8.0`;
- rota raiz passou a anunciar `0.8.0`;
- serviço de registro passou a aceitar `origem` e `id_fluxo`;
- registros de sucesso e erro do webhook passaram a preservar o contexto externo;
- README passou a documentar o fluxo de webhook.

### Validado

- webhook processou arquivo existente com `200`;
- webhook retornou `404` para arquivo inexistente;
- webhook retornou `400` para conteúdo inválido;
- webhook retornou `503` para indisponibilidade do Tesseract;
- `origem` e `id_fluxo` foram devolvidos na resposta;
- `origem` e `id_fluxo` foram persistidos no JSON;
- processamento real de `sistemas_crm.pdf` foi concluído;
- Swagger exibiu o novo contrato;
- `python -m py_compile` passou nos arquivos alterados;
- suíte completa executada com `15 passed`.

### Decisões técnicas

- o primeiro webhook recebe o nome de um arquivo já existente em `input/`;
- upload binário direto foi adiado;
- entrada e saída foram modeladas com Pydantic;
- a rota reaproveita `processar_automaticamente`;
- a rota reaproveita `criar_registro_processamento`;
- sucesso e falha mantêm o mesmo padrão de auditoria;
- `origem` e `id_fluxo` são opcionais para preservar compatibilidade;
- testes usam mocks para evitar OCR e arquivos reais.

### Conhecimento aplicado

- contratos de entrada e saída;
- webhook;
- rastreabilidade entre sistemas;
- correlação por `id_fluxo`;
- extensão de dicionários de registro;
- parâmetros opcionais;
- reutilização de serviços;
- testes de integração com `TestClient`.

### Limitações

- ainda não existe workflow real montado no N8N;
- o webhook depende de arquivo previamente salvo em `input/`;
- não há autenticação do webhook;
- não há assinatura ou segredo compartilhado;
- não há política de repetição;
- não há idempotência;
- não há deploy público;
- permanece o warning de depreciação do TestClient.

## [0.7.0] - 2026-07-30

### Adicionado

- suíte automatizada com 11 testes;
- testes da API, processador automático e registro JSON;
- uso de `tmp_path` e `monkeypatch`;
- arquivo `requirements-dev.txt`.

### Alterado

- versão da API atualizada para `0.7.0`;
- resposta automática voltou a incluir `id_registro` e `caminho_registro`;
- registros de erro passaram a ser protegidos por testes.

### Corrigido

- ausência da variável `registro`;
- resposta Pydantic incompleta;
- erro `400` sem registro;
- problemas de indentação e escopo nos testes.

### Validado

- execução completa com `11 passed`.

## [0.6.0] - 2026-07-29

### Adicionado

- serviço de registro estruturado;
- UUID, data e hora;
- persistência em JSON;
- retorno de `id_registro` e `caminho_registro`;
- pasta `registros/` e regras no `.gitignore`.

## [0.5.0] - 2026-07-29

### Adicionado

- processamento automático;
- fallback de PyMuPDF para Tesseract;
- OCR direto para imagens;
- exceção `DocumentoSemTextoDigitalError`.

## [0.4.0]

### Adicionado

- OCR com Tesseract;
- suporte a PNG, JPG e JPEG;
- OCR de PDFs escaneados.

## [0.3.0]

### Adicionado

- extração de PDFs digitais com PyMuPDF;
- contagem de páginas e caracteres;
- geração de TXT.

## [0.2.0]

### Adicionado

- upload real;
- armazenamento em `input/`;
- sanitização do nome;
- rejeição de arquivo vazio.

## [0.1.0]

### Adicionado

- aplicação FastAPI;
- modelos Pydantic;
- validação de extensões;
- documentação Swagger.
