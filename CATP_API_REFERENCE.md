# Catálogo de Produtos (CATP) - API Reference v1.0.0
## Portal Único Siscomex - Guia Completo (Atualizado)

---

## 1. Ambientes (Base URLs)

| Ambiente | Base URL |
|----------|----------|
| **Produção** | `https://portalunico.siscomex.gov.br/catp/api` |
| **Validação** | `https://val.portalunico.siscomex.gov.br/catp/api` |
| **Homologação** | `https://hom.pucomex.serpro.gov.br/catp/api` |

---

## 2. Autenticação

Todas as chamadas requerem autenticação via **certificado digital (e-CPF/e-CNPJ)** ou **token JWT** obtido no endpoint de autenticação do Portal Único:

```
POST https://portalunico.siscomex.gov.br/portal/api/autenticar
```

Headers obrigatórios em todas as chamadas:
```
Authorization: Bearer {token_jwt}
Content-Type: application/json
X-CSRF-Token: {csrf_token}
```

---

## 3. Endpoints da API

### ⚠️ ENDPOINTS DEPRECIADOS (removidos após 01/01/2026)

> Estes endpoints usam o schema `ProdutoIntegracaoDTO` (com `seq`, `cpfCnpjRaiz`, `situacao` no body).
> Utilize os novos endpoints abaixo.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/ext/produto` | Incluir produto(s) em lote |
| `POST` | `/ext/operador-estrangeiro` | Incluir operador estrangeiro (lote) |

### ✅ ENDPOINTS ATUAIS (Novos)

#### 3.1 Incluir Produto
```
POST /catp/api/ext/produto/{cpfCnpjRaiz}
```
- **Body**: `ProdutoIntegracaoRequestDTO`
- **Response 201**: `{ "codigo": int, "versao": "string" }`

#### 3.2 Nova Versão de Produto
```
PUT /catp/api/ext/produto/{cpfCnpjRaiz}/{codigo}
```
- **Body**: `ProdutoIntegracaoRequestDTO`
- **Response 200**: `{ "codigo": int, "versao": "string" }`

#### 3.3 Retificar Versão Existente
```
PUT /catp/api/ext/produto/{cpfCnpjRaiz}/{codigo}/{versao}
```
- **Body**: `ProdutoIntegracaoRequestDTO`
- **Response 200**: `{ "codigo": int, "versao": "string" }`

#### 3.4 Consultar Produto (Detalhe)
```
GET /catp/api/ext/produto/{cpfCnpjRaiz}/{codigo}/{versao}
```
- **Response 200**: Produto completo com todos os campos

#### 3.5 Listar Produtos (Paginado)
```
GET /catp/api/ext/produto/lista?cpfCnpjRaiz={cpfCnpjRaiz}&pagina={n}&tamanhoPagina={n}
```

#### 3.6 Desativar Produto
```
PUT /catp/api/ext/produto/desativar
Body: { "cpfCnpjRaiz": "...", "codigo": ... }
```

#### 3.7 Ativar Produto
```
PUT /catp/api/ext/produto/ativar
Body: { "cpfCnpjRaiz": "...", "codigo": ... }
```

#### 3.8 Exportar Catálogo Completo
```
GET /catp/api/ext/produto/exportar-catalogo?cpfCnpjRaiz={cpfCnpjRaiz}
```

#### 3.9 Incluir Operador Estrangeiro
```
POST /catp/api/ext/operador-estrangeiro/{cpfCnpjRaiz}
```
- **Body**: `OperadorEstrangeiroIntegracaoRequestDTO`

---

## 4. Schemas (Modelos de Dados)

### 4.1 ProdutoIntegracaoRequestDTO (Novos Endpoints)

Usado nos endpoints `POST /ext/produto/{cpfCnpjRaiz}`, `PUT /ext/produto/{cpfCnpjRaiz}/{codigo}` e `PUT /ext/produto/{cpfCnpjRaiz}/{codigo}/{versao}`.

> **NOTA**: `cpfCnpjRaiz` vai na URL, NÃO no body. `situacao`, `seq`, `codigo` e `versao` NÃO fazem parte deste schema.

```json
{
  "descricao": "string",
  "denominacao": "string",
  "modalidade": "string",
  "ncm": "string",
  "atributos": [
    { "atributo": "string", "valor": "string" }
  ],
  "atributosMultivalorados": [
    { "atributo": "string", "valores": ["string"] }
  ],
  "atributosCompostos": [
    {
      "atributo": "string",
      "elementos": [
        { "atributo": "string", "valor": "string" }
      ]
    }
  ],
  "atributosCompostosMultivalorados": [
    {
      "atributo": "string",
      "elementos": [
        [{ "atributo": "string", "valor": "string" }]
      ]
    }
  ],
  "codigosInterno": ["string"]
}
```

### 4.2 ProdutoIntegracaoDTO (Endpoint Depreciado - Upload em Lote)

Usado no endpoint depreciado `POST /ext/produto` (upload de JSON em lote). Inclui campos extras.

```json
{
  "seq": 1,
  "codigo": 123,
  "versao": "1",
  "cpfCnpjRaiz": "25940099",
  "situacao": "ATIVADO",
  "dataReferencia": "dd/MM/yyyy HH:mm:ss",
  "descricao": "string",
  "denominacao": "string",
  "modalidade": "string",
  "ncm": "string",
  "atributos": [...],
  "atributosMultivalorados": [...],
  "atributosCompostos": [...],
  "atributosCompostosMultivalorados": [...],
  "codigosInterno": ["string"]
}
```

### 4.3 Response: ProdutoIntegracaoResponseDTO

```json
{
  "codigo": 123,
  "versao": "1"
}
```

---

## 5. Classificação dos Campos

### Campos do ProdutoIntegracaoRequestDTO (Novos Endpoints)

| Campo | Tipo | Obrigatório | Tamanho/Validação |
|-------|------|-------------|-------------------|
| `descricao` | string | ✅ Sim | Máx. 2000 caracteres |
| `denominacao` | string | ✅ Sim | Máx. **120** caracteres |
| `modalidade` | string | ✅ Sim | Enum: `"IMPORTACAO"`, `"EXPORTACAO"` |
| `ncm` | string | ✅ Sim | Exatamente 8 dígitos numéricos |
| `codigosInterno` | string[] | ❌ Não | Cada código até 60 caracteres |
| `atributos` | array | ⚠️ Condicional | Depende do NCM/modalidade |
| `atributosMultivalorados` | array | ⚠️ Condicional | Depende do NCM/modalidade |
| `atributosCompostos` | array | ⚠️ Condicional | Depende do NCM/modalidade |
| `atributosCompostosMultivalorados` | array | ⚠️ Condicional | Depende do NCM/modalidade |

### Campos Extras no ProdutoIntegracaoDTO (Endpoint Depreciado)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `seq` | integer | ✅ Sim | Sequencial no lote |
| `cpfCnpjRaiz` | string | ✅ Sim | CNPJ raiz (8 dígitos) ou CPF |
| `situacao` | string | ❌ Não | `"ATIVADO"`, `"DESATIVADO"`, `"RASCUNHO"` |
| `codigo` | integer | ❌ Não | Código do produto (para atualização) |
| `versao` | string | ❌ Não | Versão (para retificação) |
| `dataReferencia` | string | ❌ Não | Formato dd/MM/yyyy HH:mm:ss |

---

## 6. Regras de Validação

### 6.1 Campo `denominacao`
- Máximo **120 caracteres** (conforme Swagger oficial)
- Nome comercial/fantasia do produto

### 6.2 Campo `descricao`
- Máximo **2000 caracteres**
- Descrição detalhada e completa do produto

### 6.3 Campo `ncm`
- Exatamente **8 dígitos numéricos**
- Deve ser um NCM válido na tabela TIPI vigente

### 6.4 Campo `modalidade`
- Valores: `"IMPORTACAO"` ou `"EXPORTACAO"` (MAIÚSCULAS, sem acento)

### 6.5 Campo `situacao` (apenas endpoint depreciado)
- `"ATIVADO"` (padrão), `"DESATIVADO"`, `"RASCUNHO"`
- **MAIÚSCULAS** conforme Swagger oficial

### 6.6 Campo `cpfCnpjRaiz`
- CNPJ raiz: **8 dígitos** / CPF: **11 dígitos**
- Nos novos endpoints: vai na **URL**, NÃO no body

---

## 7. Mapeamento: Exportação → Criação

```
Exportação (GET)           →    POST (Novo API)          →    POST (Lote Depreciado)
────────────────────────────────────────────────────────────────────────────────────
seq: 1                     →    NÃO ENVIAR               →    ENVIAR (sequencial)
codigo: 1                  →    NÃO ENVIAR               →    Opcional (atualização)
versao: "2"                →    NÃO ENVIAR               →    Opcional (retificação)
cpfCnpjRaiz: "25940099"   →    NA URL (não no body)     →    ENVIAR no body
situacao: "ATIVADO"        →    NÃO ENVIAR               →    ENVIAR (opcional)
descricao: "..."           →    ENVIAR ✅                 →    ENVIAR ✅
denominacao: "..."         →    ENVIAR ✅                 →    ENVIAR ✅
modalidade: "IMPORTACAO"   →    ENVIAR ✅                 →    ENVIAR ✅
ncm: "90211010"            →    ENVIAR ✅                 →    ENVIAR ✅
atributos: [...]           →    ENVIAR ✅                 →    ENVIAR ✅
atributosMultivalorados    →    ENVIAR ✅                 →    ENVIAR ✅
atributosCompostos         →    ENVIAR ✅ (pode ser [])   →    ENVIAR ✅
atributosCompostosMulti..  →    ENVIAR ✅ (pode ser [])   →    ENVIAR ✅
codigosInterno: [...]      →    ENVIAR ✅ (opcional)      →    ENVIAR ✅
```

---

## 8. Códigos de Resposta HTTP

| Código | Significado |
|--------|-------------|
| `200` | OK - Produto alterado com sucesso |
| `201` | Created - Produto criado com sucesso |
| `400` | Bad Request - Erro de validação |
| `401` | Unauthorized - Token inválido ou expirado |
| `403` | Forbidden - Sem permissão para o CNPJ |
| `404` | Not Found - Produto não encontrado |
| `409` | Conflict - Conflito de versão |
| `422` | Unprocessable Entity - Dados inválidos |
| `500` | Internal Server Error |

---

## 9. Limites da API

| Limite | Valor |
|--------|-------|
| Tamanho máximo da denominação | **120** caracteres |
| Tamanho máximo da descrição | 2000 caracteres |
| Tamanho máximo código interno | 60 caracteres |
| Tamanho máximo valor atributo | 3000 caracteres |
| cpfCnpjRaiz máximo | 14 caracteres |

---

## 10. Notas Importantes

1. **Endpoints depreciados**: `POST /ext/produto` (lote) e `POST /ext/operador-estrangeiro` (lote) foram marcados para remoção em 01/01/2026. Use os novos endpoints com `{cpfCnpjRaiz}` na URL.

2. **cpfCnpjRaiz na URL**: Nos novos endpoints, o CNPJ raiz vai na URL (`/ext/produto/{cpfCnpjRaiz}`), NÃO no body do JSON.

3. **Situação**: Nos novos endpoints, `situacao` NÃO faz parte do body. Use os endpoints `/ativar` e `/desativar` para mudar o status.

4. **Versionamento**: `PUT /ext/produto/{cnpj}/{codigo}` cria nova versão. `PUT /ext/produto/{cnpj}/{codigo}/{versao}` retifica versão existente.

5. **Alteração completa**: O PUT substitui TODOS os dados. Se omitir um atributo, ele será removido.

6. **Upload via Portal**: O portal web pode aceitar JSON no formato do endpoint depreciado (com `seq`) para upload em lote.
