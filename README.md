# 📦 Conversor Catálogo de Produtos Siscomex (CATP API)

Aplicação web genérica para converter planilhas Excel em JSON compatível com a API do Catálogo de Produtos (CATP) do Portal Único Siscomex. Funciona para qualquer empresa.

## 🚀 Funcionalidades

- **Excel → JSON**: Converte planilha para JSON em 5 modos:
  - **API POST**: ProdutoIntegracaoRequestDTO (novos endpoints)
  - **API PUT**: ProdutoIntegracaoRequestDTO (nova versão/retificação)
  - **Lote POST**: ProdutoIntegracaoDTO com seq (upload portal, depreciado)
  - **Lote PUT**: ProdutoIntegracaoDTO com seq e codigo (atualização lote)
  - **Completo**: Formato idêntico ao exportado pelo portal
- **JSON → Excel**: Converte JSON exportado do portal para planilha editável
- **Planilha Modelo**: Download de modelo pronto com todas as colunas
- **Validação**: Verifica campos obrigatórios, NCM, CNPJ, tamanhos máximos
- **Preview**: Visualização do JSON gerado com cópia para clipboard
- **Genérico**: Funciona para qualquer empresa (CNPJ configurável)

## 📁 Estrutura do Projeto

```
web/
├── app.py                       # Servidor Flask
├── conversor_catalogo_siscomex.py  # Motor de conversão
├── requirements.txt             # Dependências Python
├── Procfile                     # Config Heroku/Railway
└── templates/
    └── index.html               # Interface web completa
```

## 💻 Executar Localmente

```bash
cd web
pip install -r requirements.txt
python app.py
```

Acesse: **http://localhost:5000**

## 🌐 Deploy (Render.com)

O projeto inclui `render.yaml` para deploy automático no Render.com.

1. Suba o código para o GitHub
2. No Render.com, crie um **Web Service** conectando o repositório
3. O `render.yaml` configura tudo automaticamente

> ⚠️ No plano gratuito do Render, o serviço "hiberna" após 15 min sem uso.

## 🔧 Endpoints da Aplicação Web

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Página principal |
| `/converter` | POST | Excel → JSON (form: arquivo, modo) |
| `/json-para-excel` | POST | JSON → Excel (form: arquivo) |
| `/modelo` | GET | Download planilha modelo |
| `/download/<nome>` | GET | Download arquivo gerado |
| `/validar` | POST | Validar planilha (form: arquivo) |

## 📋 Campos Obrigatórios da API CATP

| Campo | Descrição | Regra |
|-------|-----------|-------|
| `denominacao` | Nome do produto | Máx **120** caracteres |
| `descricao` | Descrição detalhada | Máx 2000 caracteres |
| `cpfCnpjRaiz` | CNPJ raiz | 8 dígitos numéricos |
| `modalidade` | Tipo operação | IMPORTACAO ou EXPORTACAO |
| `ncm` | Classificação fiscal | 8 dígitos numéricos |

## 📡 Endpoints da API CATP (Siscomex)

| Ação | Método | Endpoint |
|------|--------|----------|
| Incluir produto | POST | `/catp/api/ext/produto/{cpfCnpjRaiz}` |
| Nova versão | PUT | `/catp/api/ext/produto/{cpfCnpjRaiz}/{codigo}` |
| Retificar versão | PUT | `/catp/api/ext/produto/{cpfCnpjRaiz}/{codigo}/{versao}` |
| Consultar produto | GET | `/catp/api/ext/produto/{cpfCnpjRaiz}/{codigo}/{versao}` |
| Upload lote (depreciado) | POST | `/catp/api/ext/produto` |

## 📜 Licença

Uso livre para operações de comércio exterior via Portal Único Siscomex.
