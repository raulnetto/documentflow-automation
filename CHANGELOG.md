# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

## [0.9.0] - 2026-08-03

### Adicionado

- integração real entre N8N e DocumentFlow;
- workflow `DocumentFlow - Processamento`;
- pasta `n8n/`;
- documentação específica em `n8n/README.md`;
- pasta `n8n/workflows/`;
- workflow exportado em `n8n/workflows/documentflow-processamento.json`;
- nó manual de início;
- nó `Configurar Processamento`;
- nó `Chamar DocumentFlow`;
- nó `Validar Resposta`;
- saída `Resultado - Sucesso`;
- saída `Resultado - Erro`;
- tratamento visual dos caminhos de sucesso e falha;
- uso de `statusCode` na decisão do workflow;
- uso de `Never Error` no nó HTTP;
- inclusão de corpo, cabeçalhos e status na resposta;
- arquivo neutro de demonstração para testes locais.

### Alterado

- versão da API atualizada de `0.8.0` para `0.9.0`;
- rota raiz passou a anunciar `0.9.0`;
- teste da rota raiz passou a exigir `0.9.0`;
- arquivo padrão do workflow alterado para `documento_demo.pdf`;
- nomes dos nós foram refinados para expressar suas responsabilidades;
- README principal passou a documentar a integração real com N8N.

### Validado

- N8N iniciou localmente em `localhost:5678`;
- FastAPI iniciou localmente em `127.0.0.1:8000`;
- workflow enviou requisição real para o webhook;
- payload preservou `nome_arquivo`, `origem` e `id_fluxo`;
- arquivo existente retornou `200`;
- fluxo `true` produziu saída de sucesso;
- arquivo inexistente retornou `404`;
- fluxo `false` produziu saída de erro;
- OCR real processou `documento_demo.pdf` com Tesseract;
- resposta preservou mecanismo, UUID e identificador do fluxo;
- workflow exportado foi validado com `ConvertFrom-Json`;
- nome do workflow exportado foi confirmado;
- nenhum documento de entrada apareceu no Git;
- suíte Python permaneceu estável com `15 passed`.

### Corrigido

- valor `=sistemas_crm.pdf` enviado incorretamente pelo N8N;
- expressões JSON ajustadas para não incluir o caractere `=`;
- condição do IF que comparava `statusCode` com texto incorreto;
- segundo operando vazio no nó IF;
- referências de saída atualizadas após habilitar resposta HTTP completa;
- campos do resultado de sucesso ajustados para `body`;
- tratamento de respostas HTTP não concluídas passou a seguir pelo workflow.

### Decisões técnicas

- o primeiro workflow usa `Manual Trigger`;
- o documento precisa existir previamente em `input/`;
- o N8N não executa OCR diretamente;
- a lógica documental continua pertencendo à API;
- o N8N atua como orquestrador;
- a decisão do fluxo usa o código HTTP;
- `Never Error` impede que `400`, `404` e `503` interrompam o workflow;
- o workflow exportado mantém apenas configurações e expressões;
- documentos reais e pessoais não são versionados;
- `127.0.0.1` foi mantido para execução local reproduzível;
- o arquivo de demonstração permanece ignorado pelo Git.

### Conhecimento aplicado

- instalação e execução local do N8N;
- Node.js, npm e `npx`;
- workflows e nós;
- mapeamento de dados;
- expressões `$json`;
- referência a dados de outro nó;
- requisição HTTP `POST`;
- corpo JSON;
- resposta HTTP completa;
- códigos de status;
- bifurcação com IF;
- transformação de saídas;
- exportação e validação de workflow;
- privacidade de artefatos de demonstração;
- separação entre processamento e orquestração.

### Limitações

- workflow ainda usa gatilho manual;
- não há upload binário direto;
- documento precisa estar em `input/`;
- N8N e FastAPI precisam rodar localmente;
- não há autenticação;
- não há política de repetição ou idempotência;
- não há banco de dados;
- não há Docker;
- não há deploy público;
- não há monitoramento contínuo.

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
