# Integração N8N — DocumentFlow

Esta pasta contém o workflow do N8N utilizado para acionar o DocumentFlow por meio de uma requisição HTTP local.

## Estrutura

```text
n8n/
├── README.md
└── workflows/
    └── documentflow-processamento.json
```

## Objetivo

O workflow demonstra uma integração real entre o N8N e a API FastAPI do DocumentFlow.

Fluxo:

```text
Manual Trigger
→ Configurar Processamento
→ Chamar DocumentFlow
→ Validar Resposta
   ├── Resultado - Sucesso
   └── Resultado - Erro
```

## Workflow exportado

Arquivo:

```text
n8n/workflows/documentflow-processamento.json
```

Esse JSON pode ser importado em outra instalação do N8N.

## Entrada utilizada

O nó `Configurar Processamento` produz:

```json
{
  "nome_arquivo": "documento_demo.pdf",
  "origem": "n8n",
  "id_fluxo": "workflow-001"
}
```

O arquivo precisa existir previamente na pasta:

```text
input/
```

O arquivo de demonstração não é versionado no GitHub.

## Requisição enviada

O nó `Chamar DocumentFlow` realiza:

```text
POST http://127.0.0.1:8000/webhooks/processar-documento
```

Corpo:

```json
{
  "nome_arquivo": "{{ $json.nome_arquivo }}",
  "origem": "{{ $json.origem }}",
  "id_fluxo": "{{ $json.id_fluxo }}"
}
```

Configurações importantes do nó HTTP:

```text
Send Body: ativado
Body Content Type: JSON
Include Response Headers and Status: ativado
Never Error: ativado
```

A opção `Never Error` permite que respostas como `400`, `404` e `503` continuem pelo workflow, em vez de interromper a execução.

## Decisão do fluxo

O nó `Validar Resposta` verifica:

```text
statusCode == 200
```

Resultado:

```text
true
→ Resultado - Sucesso

false
→ Resultado - Erro
```

## Saída de sucesso

Exemplo:

```json
{
  "resultado": "sucesso",
  "mensagem": "Documento processado com sucesso",
  "arquivo": "documento_demo.pdf",
  "mecanismo": "tesseract",
  "id_fluxo": "workflow-001",
  "id_registro": "uuid-gerado"
}
```

## Saída de erro

Exemplo:

```json
{
  "resultado": "erro",
  "mensagem": "O arquivo 'input\\arquivo_inexistente.pdf' não foi encontrado.",
  "codigo_http": 404,
  "arquivo": "arquivo_inexistente.pdf",
  "origem": "n8n",
  "id_fluxo": "workflow-001"
}
```

## Como executar localmente

### 1. Iniciar o DocumentFlow

Na raiz do projeto:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

### 2. Iniciar o N8N

Em outro terminal:

```powershell
npx n8n
```

O editor ficará disponível em:

```text
http://localhost:5678
```

### 3. Importar o workflow

No N8N:

```text
Import from File
→ selecionar n8n/workflows/documentflow-processamento.json
```

### 4. Preparar o arquivo de demonstração

Coloque um arquivo sem dados pessoais em:

```text
input/documento_demo.pdf
```

### 5. Executar

Clique em:

```text
Execute workflow
```

## Cenários validados

```text
200
→ processamento concluído
→ saída de sucesso

404
→ arquivo inexistente
→ saída de erro
```

A API também possui tratamento automatizado para:

```text
400
→ conteúdo inválido

503
→ mecanismo externo indisponível
```

## Segurança e privacidade

Não versionar:

- documentos pessoais;
- arquivos da pasta `input/`;
- arquivos produzidos em `output/`;
- registros gerados em `registros/`;
- senhas;
- tokens;
- credenciais do N8N.

O endereço:

```text
127.0.0.1
```

é local e representa o próprio computador. Não é um endereço residencial nem um IP público.

## Limitações atuais

- o workflow usa um gatilho manual;
- o documento precisa existir previamente em `input/`;
- a API e o N8N precisam estar rodando localmente;
- ainda não há autenticação;
- ainda não há upload binário direto pelo N8N;
- ainda não há deploy público.

## Evoluções futuras

- gatilho automático;
- upload direto;
- autenticação por chave;
- integração com banco de dados;
- relatórios;
- deploy;
- monitoramento;
- workflows adicionais.
