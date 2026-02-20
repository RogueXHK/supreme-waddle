# Catálogo de Produtos (CATP) - API Reference
## Portal Único Siscomex - Guia Completo

---

## 1. Ambientes (Base URLs)

| Ambiente | Base URL |
|----------|----------|
| **Produção** | `https://portalunico.siscomex.gov.br/catp/api/ext` |
| **Validação (Homologação)** | `https://val.portalunico.siscomex.gov.br/catp/api/ext` |
| **Treinamento** | `https://trn.portalunico.siscomex.gov.br/catp/api/ext` |

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
x-csrf-token: {csrf_token}
```

---

## 3. Endpoints da API

### 3.1 Incluir Produto (Criar)
```
POST /catp/api/ext/produto
```

### 3.2 Alterar Produto (Atualizar)
```
PUT /catp/api/ext/produto
```

### 3.3 Consultar Produto por Código
```
GET /catp/api/ext/produto?cpfCnpjRaiz={cpfCnpjRaiz}&codigo={codigo}
```

### 3.4 Listar Produtos (Paginado)
```
GET /catp/api/ext/produto/lista?cpfCnpjRaiz={cpfCnpjRaiz}&pagina={pagina}&tamanhoPagina={tamanhoPagina}
```

### 3.5 Desativar Produto
```
PUT /catp/api/ext/produto/desativar
Body: { "cpfCnpjRaiz": "...", "codigo": ... }
```

### 3.6 Ativar Produto
```
PUT /catp/api/ext/produto/ativar
Body: { "cpfCnpjRaiz": "...", "codigo": ... }
```

### 3.7 Exportar Catálogo Completo
```
GET /catp/api/ext/produto/exportar-catalogo?cpfCnpjRaiz={cpfCnpjRaiz}
```
> Retorna o JSON array completo como o seu arquivo `CATALOGO_PRODUTOS_25940099_*.json`

---

## 4. JSON Schema - POST (Incluir Produto)

### Request Body para criação:

```json
{
  "denominacao": "string",           // OBRIGATÓRIO - Nome comercial do produto
  "descricao": "string",             // OBRIGATÓRIO - Descrição detalhada do produto
  "ncm": "string",                   // OBRIGATÓRIO - Código NCM (8 dígitos)
  "cpfCnpjRaiz": "string",           // OBRIGATÓRIO - CNPJ raiz (8 dígitos) ou CPF
  "modalidade": "string",            // OBRIGATÓRIO - "IMPORTACAO" ou "EXPORTACAO"
  "situacao": "string",              // OPCIONAL    - "Ativado" (padrão) ou "Desativado"
  "codigosInterno": ["string"],       // OPCIONAL    - Lista de códigos internos da empresa
  "atributos": [                      // CONDICIONAL - Atributos simples (depende do NCM)
    {
      "atributo": "string",          // Código do atributo (ex: "ATT_14545")
      "valor": "string"             // Valor do atributo
    }
  ],
  "atributosMultivalorados": [        // CONDICIONAL - Atributos com múltiplos valores
    {
      "atributo": "string",
      "valores": ["string"]
    }
  ],
  "atributosCompostos": [             // CONDICIONAL - Atributos compostos (grupos)
    {
      "atributo": "string",
      "elementos": [
        {
          "atributo": "string",
          "valor": "string"
        }
      ]
    }
  ],
  "atributosCompostosMultivalorados": [ // CONDICIONAL - Compostos multivalorados
    {
      "atributo": "string",
      "elementos": [
        [
          {
            "atributo": "string",
            "valor": "string"
          }
        ]
      ]
    }
  ]
}
```

### Response (Sucesso - 201 Created):

```json
{
  "codigo": 123,                    // Código gerado pelo servidor
  "versao": "1"                     // Versão inicial do produto
}
```

---

## 5. JSON Schema - PUT (Alterar Produto)

### Request Body para alteração:

```json
{
  "codigo": 1,                       // OBRIGATÓRIO - Código do produto (retornado na criação)
  "denominacao": "string",           // OBRIGATÓRIO
  "descricao": "string",             // OBRIGATÓRIO
  "ncm": "string",                   // OBRIGATÓRIO
  "cpfCnpjRaiz": "string",           // OBRIGATÓRIO
  "modalidade": "string",            // OBRIGATÓRIO
  "codigosInterno": ["string"],       // OPCIONAL
  "atributos": [...],                // CONDICIONAL
  "atributosMultivalorados": [...],  // CONDICIONAL
  "atributosCompostos": [...],       // CONDICIONAL
  "atributosCompostosMultivalorados": [...] // CONDICIONAL
}
```

> **IMPORTANTE**: Na alteração, enviar todos os campos (inclusive os que não mudaram). Os atributos omitidos serão removidos do produto.

### Response (Sucesso - 200 OK):

```json
{
  "codigo": 1,
  "versao": "3"                     // Versão incrementada
}
```

---

## 6. Classificação dos Campos: POST vs READ-ONLY

### Campos que VOCÊ ENVIA (POST/PUT):

| Campo | Tipo | Obrigatório | Tamanho/Validação |
|-------|------|-------------|-------------------|
| `denominacao` | string | ✅ Sim | Máx. 200 caracteres |
| `descricao` | string | ✅ Sim | Máx. 2000 caracteres |
| `ncm` | string | ✅ Sim | Exatamente 8 dígitos numéricos |
| `cpfCnpjRaiz` | string | ✅ Sim | 8 dígitos (CNPJ raiz) ou 11 (CPF) |
| `modalidade` | string | ✅ Sim | Enum: `"IMPORTACAO"`, `"EXPORTACAO"` |
| `situacao` | string | ❌ Não | Enum: `"Ativado"`, `"Desativado"` (padrão: "Ativado") |
| `codigo` | integer | ✅ Somente PUT | Código retornado no POST |
| `codigosInterno` | string[] | ❌ Não | Array de strings, cada uma até 60 caracteres |
| `atributos` | array | ⚠️ Condicional | Obrigatórios conforme NCM/modalidade |
| `atributosMultivalorados` | array | ⚠️ Condicional | Obrigatórios conforme NCM/modalidade |
| `atributosCompostos` | array | ⚠️ Condicional | Obrigatórios conforme NCM/modalidade |
| `atributosCompostosMultivalorados` | array | ⚠️ Condicional | Obrigatórios conforme NCM/modalidade |

### Campos SOMENTE LEITURA (retornados pelo servidor, NÃO enviar no POST):

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `codigo` | integer | Código sequencial do produto gerado pelo servidor (usado no PUT) |
| `versao` | string | Número da versão, incrementado a cada alteração |
| `seq` | integer | Número sequencial na listagem/exportação |

---

## 7. Regras de Validação Detalhadas

### 7.1 Campo `ncm`
- Exatamente **8 dígitos numéricos** (sem pontos, traços ou espaços)
- Deve ser um NCM válido na tabela TIPI vigente
- Exemplo: `"90211010"`, `"30064012"`
- Os atributos obrigatórios dependem do NCM escolhido

### 7.2 Campo `modalidade`
- Valores aceitos: `"IMPORTACAO"` ou `"EXPORTACAO"`
- Sempre em MAIÚSCULAS, sem acento
- Define quais atributos são obrigatórios

### 7.3 Campo `denominacao`
- Máximo **200 caracteres**
- Nome comercial/fantasia do produto
- Não pode ser vazio

### 7.4 Campo `descricao`
- Máximo **2000 caracteres**
- Descrição detalhada e completa do produto
- Deve ser suficientemente descritiva para fins de despacho aduaneiro

### 7.5 Campo `cpfCnpjRaiz`
- Para CNPJ: **8 primeiros dígitos** (raiz), sem formatação
- Para CPF: **11 dígitos**, sem formatação
- Deve corresponder ao importador/exportador autenticado

### 7.6 Campo `codigosInterno`
- Array de strings
- Cada código interno pode ter até **60 caracteres**
- Usado para vincular códigos internos da empresa (SKU, part number, etc.)
- Limite de até **50 códigos internos** por produto

### 7.7 Campo `situacao`
- `"Ativado"` (padrão ao criar)
- `"Desativado"` (produto inativo, não pode ser usado em novas declarações)

### 7.8 Atributos (Regras Gerais)
- Os atributos obrigatórios são determinados pela combinação **NCM + modalidade**
- Consultar atributos obrigatórios via API de Cadastro de Atributos (CADA):
  ```
  GET /cada/api/ext/atributo-ncm?ncm={ncm}&modalidade={modalidade}
  ```
- Cada atributo tem seu domínio de valores aceitos
- Atributos com valor booleano usam strings: `"true"` ou `"false"`

---

## 8. Atributos Comuns para NCM 90211010 (Seu caso - Instrumentos Odontológicos)

Com base no seu arquivo exportado, os atributos para o NCM `90211010` na modalidade `IMPORTACAO` são:

| Código Atributo | Descrição Provável | Exemplo do seu catálogo | Obrigatório |
|-----------------|--------------------|-----------------------|-------------|
| `ATT_14540` | Condição da mercadoria | `"01"` (Nova) | ✅ Sim |
| `ATT_14545` | País de origem (código BACEN) | `"82"` (China) | ✅ Sim |
| `ATT_14546` | Validade/Prazo | `"INDETERMINADO"`, `"2 ANOS"` | ✅ Sim |
| `ATT_14547` | Produto perigoso | `"false"` | ✅ Sim |
| `ATT_14551` | Registro ANVISA | `"80853390005"` | ✅ Sim |
| `ATT_14554` | Produto controlado | `"false"` | ✅ Sim |
| `ATT_14555` | Fabricante/Fornecedor estrangeiro | Nome do fabricante | ✅ Sim |
| `ATT_14556` | Finalidade de uso (multivalorado) | `["11"]` | ✅ Sim |
| `ATT_14860` | Marca/Modelo/Nome comercial | Nome do produto | ✅ Sim |
| `ATT_15120` | Material/Composição | `"AÇO INOX"`, `"NIQUEL TITANIO"` | ✅ Sim |
| `ATT_15121` | Código do fabricante/Part Number | `"IA06-140"` | ✅ Sim |

---

## 9. Exemplos Completos

### 9.1 POST - Criar um novo produto (IMPORTAÇÃO)

```
POST https://portalunico.siscomex.gov.br/catp/api/ext/produto
Content-Type: application/json
Authorization: Bearer {seu_token}
x-csrf-token: {seu_csrf}
```

```json
{
  "denominacao": "ARCO NITI 12 (M) INF/SUP 10UN",
  "descricao": "Indicado Para Tratamentos Ortodônticos. Ele É Projetado Para Oferecer Excelente Memória De Forma E Resistência, Sendo Ideal Para O Alinhamento Inicial Dos Dentes.",
  "ncm": "90211010",
  "cpfCnpjRaiz": "25940099",
  "modalidade": "IMPORTACAO",
  "codigosInterno": ["6128"],
  "atributos": [
    { "atributo": "ATT_14540", "valor": "01" },
    { "atributo": "ATT_14545", "valor": "82" },
    { "atributo": "ATT_14546", "valor": "INDETERMINADA" },
    { "atributo": "ATT_14547", "valor": "false" },
    { "atributo": "ATT_14551", "valor": "80853390002" },
    { "atributo": "ATT_14554", "valor": "false" },
    { "atributo": "ATT_14555", "valor": "HANGZHOU XINGCHEN 3B DENTAL INSTRUMENT E MATERIAL CO.,LTD" },
    { "atributo": "ATT_14860", "valor": "ARCO NITI 12 (M) INF/SUP 10UN" },
    { "atributo": "ATT_15120", "valor": "NIQUEL TITANIO" },
    { "atributo": "ATT_15121", "valor": "AW002-12U" }
  ],
  "atributosMultivalorados": [
    { "atributo": "ATT_14556", "valores": ["11"] }
  ],
  "atributosCompostos": [],
  "atributosCompostosMultivalorados": []
}
```

**Response (201):**
```json
{
  "codigo": 2,
  "versao": "1"
}
```

### 9.2 PUT - Alterar produto existente

```
PUT https://portalunico.siscomex.gov.br/catp/api/ext/produto
```

```json
{
  "codigo": 2,
  "denominacao": "ARCO NITI 12 (M) INF/SUP 10UN - ATUALIZADO",
  "descricao": "Descrição atualizada...",
  "ncm": "90211010",
  "cpfCnpjRaiz": "25940099",
  "modalidade": "IMPORTACAO",
  "codigosInterno": ["6128", "NOVO-SKU-001"],
  "atributos": [
    { "atributo": "ATT_14540", "valor": "01" },
    { "atributo": "ATT_14545", "valor": "82" },
    { "atributo": "ATT_14546", "valor": "INDETERMINADA" },
    { "atributo": "ATT_14547", "valor": "false" },
    { "atributo": "ATT_14551", "valor": "80853390002" },
    { "atributo": "ATT_14554", "valor": "false" },
    { "atributo": "ATT_14555", "valor": "HANGZHOU XINGCHEN 3B DENTAL INSTRUMENT E MATERIAL CO.,LTD" },
    { "atributo": "ATT_14860", "valor": "ARCO NITI 12 (M) INF/SUP 10UN - ATUALIZADO" },
    { "atributo": "ATT_15120", "valor": "NIQUEL TITANIO" },
    { "atributo": "ATT_15121", "valor": "AW002-12U" }
  ],
  "atributosMultivalorados": [
    { "atributo": "ATT_14556", "valores": ["11"] }
  ],
  "atributosCompostos": [],
  "atributosCompostosMultivalorados": []
}
```

**Response (200):**
```json
{
  "codigo": 2,
  "versao": "4"
}
```

---

## 10. Mapeamento: Seu JSON Exportado → API

Analisando seu arquivo `CATALOGO_PRODUTOS_25940099_20260220031001.json`:

```
Exportação (GET)          →    Criação (POST)
──────────────────────────────────────────────
seq: 1                    →    NÃO ENVIAR (sequencial da listagem)
codigo: 1                 →    NÃO ENVIAR no POST (gerado pelo servidor)
                               ENVIAR no PUT (identificador do produto)
descricao: "..."          →    ENVIAR ✅
denominacao: "..."        →    ENVIAR ✅
cpfCnpjRaiz: "25940099"  →    ENVIAR ✅
situacao: "Ativado"       →    OPCIONAL (padrão "Ativado")
modalidade: "IMPORTACAO"  →    ENVIAR ✅
ncm: "90211010"           →    ENVIAR ✅
versao: "2"               →    NÃO ENVIAR (controlado pelo servidor)
atributos: [...]          →    ENVIAR ✅
atributosMultivalorados   →    ENVIAR ✅
atributosCompostos        →    ENVIAR ✅ (pode ser [])
atributosCompostosMulti.. →    ENVIAR ✅ (pode ser [])
codigosInterno: [...]     →    ENVIAR ✅ (opcional)
```

---

## 11. Códigos de Resposta HTTP

| Código | Significado |
|--------|-------------|
| `200` | OK - Produto alterado com sucesso |
| `201` | Created - Produto criado com sucesso |
| `400` | Bad Request - Erro de validação (campos inválidos, atributos faltando) |
| `401` | Unauthorized - Token inválido ou expirado |
| `403` | Forbidden - Sem permissão para o CNPJ informado |
| `404` | Not Found - Produto não encontrado |
| `409` | Conflict - Conflito de versão ou produto duplicado |
| `422` | Unprocessable Entity - Dados semanticamente inválidos |
| `429` | Too Many Requests - Limite de requisições excedido |
| `500` | Internal Server Error |

---

## 12. Limites da API

| Limite | Valor |
|--------|-------|
| Requisições por minuto | 60 |
| Tamanho máximo do body | 1 MB |
| Máximo de códigos internos por produto | 50 |
| Tamanho máximo da denominação | 200 caracteres |
| Tamanho máximo da descrição | 2000 caracteres |
| Produtos por página (listagem) | Máx. 50 |

---

## 13. API Auxiliar: Consultar Atributos por NCM

Para saber quais atributos são obrigatórios para um NCM+modalidade:

```
GET https://portalunico.siscomex.gov.br/cada/api/ext/atributo-ncm?ncm=90211010&modalidade=IMPORTACAO
```

Retorna a lista de atributos, seus tipos, se são obrigatórios, e os domínios de valores aceitos.

---

## 14. Notas Importantes

1. **Certificado Digital**: A autenticação requer certificado digital ICP-Brasil (e-CPF ou e-CNPJ) tipo A1 ou A3.

2. **Perfil de Acesso**: O usuário precisa ter o perfil "Catálogo de Produtos" habilitado no Portal Único para a empresa (CNPJ).

3. **Versionamento**: Cada alteração (PUT) incrementa a versão. O campo `versao` no seu JSON exportado mostra quantas vezes o produto foi editado.

4. **Atributos são NCM-dependentes**: Diferentes NCMs exigem diferentes conjuntos de atributos. Sempre consulte a API CADA para o NCM específico.

5. **Alteração completa**: O PUT substitui TODOS os dados. Se omitir um atributo que existia, ele será removido.

6. **Exportação em lote**: O endpoint `exportar-catalogo` gera o JSON como o seu arquivo. É útil para backup/migração.
