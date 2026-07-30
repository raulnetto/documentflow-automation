# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

## [0.7.0] - 2026-07-30

### Adicionado

- pasta `tests/`;
- arquivo `tests/test_api.py`;
- arquivo `tests/test_processador_automatico.py`;
- arquivo `tests/test_registro_processamento.py`;
- suíte automatizada com 11 testes;
- testes da rota raiz;
- teste da versão anunciada pela API;
- testes da rota automática para respostas `200`, `400`, `404` e `503`;
- testes do processador automático para PDF digital, fallback para OCR e imagens;
- testes para arquivo inexistente e extensão não suportada;
- teste isolado do serviço de registro JSON;
- uso de `tmp_path` para diretórios temporários;
- uso de `monkeypatch` para substituir dependências durante os testes;
- arquivo `requirements-dev.txt`;
- declaração do `pytest==9.1.1` nas dependências de desenvolvimento.

### Alterado

- versão da API atualizada de `0.5.0` para `0.7.0`;
- rota raiz passou a anunciar `0.7.0`;
- resposta do processamento automático voltou a incluir `id_registro` e `caminho_registro`;
- criação do registro de sucesso foi restaurada antes da montagem da resposta;
- erros `400`, `404` e `503` passaram a ser verificados automaticamente;
- registros dos erros `400`, `404` e `503` passaram a ser protegidos por testes;
- fluxo de desenvolvimento passou a utilizar branch específica para a versão.

### Corrigido

- ausência da variável `registro` antes do retorno de sucesso;
- resposta Pydantic sem os campos obrigatórios `id_registro` e `caminho_registro`;
- erro `400` que era devolvido sem persistir o registro correspondente;
- identidade da API que ainda permanecia em `0.5.0`;
- problemas de indentação e escopo nos testes;
- funções auxiliares de teste que estavam fora do teste principal;
- variáveis locais como `caminho_txt` e `registro_criado` inacessíveis por escopo incorreto.

### Validado

- rota raiz retorna `200`;
- versão da rota raiz é `0.7.0`;
- processamento automático retorna `200`;
- arquivo inexistente retorna `404` e registra a falha;
- conteúdo inválido retorna `400` e registra a falha;
- indisponibilidade do Tesseract retorna `503` e registra a falha;
- PDF digital usa PyMuPDF;
- PDF sem texto digital usa fallback para Tesseract;
- imagem usa OCR diretamente;
- arquivo inexistente gera `FileNotFoundError`;
- extensão proibida gera `ValueError`;
- registro JSON é criado em pasta temporária;
- nenhum documento pessoal é usado pela suíte;
- execução completa com `11 passed`.

### Decisões técnicas

- testes de rota usam `TestClient`;
- serviços reais são substituídos por funções controladas com `monkeypatch`;
- arquivos temporários são criados com `tmp_path`;
- testes de unidade não executam OCR real;
- `requirements-dev.txt` inclui `requirements.txt` com `-r requirements.txt`;
- dependências de produção e desenvolvimento foram separadas;
- a versão anunciada passou a ser protegida por teste.

### Conhecimento aplicado

- estrutura visual de indentação;
- escopo de variáveis locais;
- funções internas de teste;
- mocks e substituição de dependências;
- regressão automatizada;
- diagnóstico por mensagens do pytest;
- diferenciação entre falha do código e falha da expectativa do teste.

### Limitações

- existe um aviso de depreciação na integração do TestClient;
- ainda não há cobertura automatizada de todas as rotas legadas;
- ainda não há pipeline de integração contínua;
- ainda não há relatório de cobertura;
- ainda não há integração com N8N ou webhook externo.

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
- ainda não existiam testes automatizados.

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
