# 🦷 Ortodente — Conversor Catálogo Siscomex (CATP API)

Aplicação web para converter planilhas Excel em JSON compatível com a API do Catálogo de Produtos (CATP) do Portal Único Siscomex.

## 🚀 Funcionalidades

- **Excel → JSON**: Converte planilha para JSON nos modos POST, PUT e Completo
- **JSON → Excel**: Converte JSON exportado do portal para planilha editável
- **Planilha Modelo**: Download de modelo pronto com todas as colunas
- **Validação**: Verifica campos obrigatórios, NCM, CNPJ, tamanhos máximos
- **Preview**: Visualização do JSON gerado com cópia para clipboard

## 📁 Estrutura do Projeto

```
Ortodente/
├── conversor_catalogo_siscomex.py   # Motor de conversão (CLI)
├── teste_conversor.py               # Testes automatizados
├── render.yaml                      # Config deploy Render.com
├── CATALOGO_PRODUTOS_*.json         # JSON exemplo do portal
└── web/
    ├── app.py                       # Servidor Flask
    ├── conversor_catalogo_siscomex.py  # Cópia do conversor (para deploy)
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

---

## 🌐 Deploy Gratuito (Passo a Passo)

### Opção 1: Render.com (Recomendado — gratuito)

1. **Crie uma conta** em [render.com](https://render.com) (pode usar GitHub)

2. **Suba o código para o GitHub**:
   ```bash
   cd c:\Users\ASUS\Documents\Ortodente
   git init
   git add .
   git commit -m "Ortodente - Conversor Siscomex CATP"
   git remote add origin https://github.com/SEU_USUARIO/ortodente-siscomex.git
   git push -u origin main
   ```

3. **No Render.com**:
   - Clique em **"New +"** → **"Web Service"**
   - Conecte seu repositório GitHub
   - Configure:
     - **Name**: `ortodente-siscomex`
     - **Root Directory**: `web`
     - **Runtime**: Python
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
     - **Plan**: Free
   - Clique em **"Create Web Service"**

4. **Pronto!** Seu site estará em: `https://ortodente-siscomex.onrender.com`

> ⚠️ No plano gratuito do Render, o serviço "hiberna" após 15 min sem uso. A primeira requisição após inatividade pode demorar ~30s.

---

### Opção 2: Railway.app

1. Crie conta em [railway.app](https://railway.app)
2. Clique **"New Project"** → **"Deploy from GitHub Repo"**
3. Selecione o repositório
4. Em **Settings**, configure:
   - **Root Directory**: `web`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Railway gera um domínio `.up.railway.app` automaticamente

---

### Opção 3: PythonAnywhere (sem GitHub)

1. Crie conta gratuita em [pythonanywhere.com](https://www.pythonanywhere.com)
2. Vá em **"Web"** → **"Add a new web app"** → Flask → Python 3.11
3. Em **"Files"**, faça upload dos arquivos da pasta `web/`
4. Configure o WSGI para apontar para `app:app`
5. Seu site ficará em: `https://SEU_USUARIO.pythonanywhere.com`

---

### Opção 4: Vercel (via Flask adapter)

1. Instale Vercel CLI: `npm install -g vercel`
2. Crie `vercel.json` na pasta web:
   ```json
   {
     "builds": [{"src": "app.py", "use": "@vercel/python"}],
     "routes": [{"src": "/(.*)", "dest": "app.py"}]
   }
   ```
3. Execute `vercel` na pasta web
4. Domínio gratuito: `https://seu-projeto.vercel.app`

---

## 🔧 API da Aplicação

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Página principal |
| `/converter` | POST | Excel → JSON (form: arquivo, modo) |
| `/json-para-excel` | POST | JSON → Excel (form: arquivo) |
| `/modelo` | GET | Download planilha modelo |
| `/download/<nome>` | GET | Download arquivo gerado |
| `/validar` | POST | Validar planilha (form: arquivo) |
| `/atributos` | GET | Lista de atributos conhecidos |

## 📋 Campos Obrigatórios da API CATP

| Campo | Descrição | Regra |
|-------|-----------|-------|
| `denominacao` | Nome do produto | Max 200 caracteres |
| `descricao` | Descrição detalhada | Max 2000 caracteres |
| `cpfCnpjRaiz` | CNPJ raiz | 8 dígitos numéricos |
| `modalidade` | Tipo operação | IMPORTACAO ou EXPORTACAO |
| `ncm` | Classificação fiscal | 8 dígitos numéricos |

## 📜 Licença

Projeto interno Ortodente. Uso exclusivo para operações de comércio exterior.
