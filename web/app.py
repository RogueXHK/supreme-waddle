# -*- coding: utf-8 -*-
"""
Aplicação Web - Conversor Catálogo de Produtos Siscomex (CATP API)
Flask + Interface moderna
"""

import json
import os
import sys
import io
import uuid
import tempfile
import shutil
import zipfile
from datetime import datetime

from flask import (
    Flask, render_template, request, send_file,
    jsonify, redirect, url_for, flash, session
)
from werkzeug.utils import secure_filename

# Importar conversor: tenta local primeiro (deploy), depois diretório pai (dev)
try:
    from conversor_catalogo_siscomex import ConversorCatalogoSiscomex, ATRIBUTOS_LABELS
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from conversor_catalogo_siscomex import ConversorCatalogoSiscomex, ATRIBUTOS_LABELS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ortodente-siscomex-catp-2026-secret')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Diretório temporário para uploads/downloads
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'ortodente_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTENSOES_PERMITIDAS_EXCEL = {'.xlsx', '.xls'}
EXTENSOES_PERMITIDAS_JSON = {'.json'}


def extensao_permitida(filename, permitidas):
    return os.path.splitext(filename)[1].lower() in permitidas


def converter_xls_para_xlsx(caminho_xls: str) -> str:
    """Converte arquivo .xls (formato antigo) para .xlsx usando xlrd + openpyxl."""
    import xlrd
    from openpyxl import Workbook

    # Ler o .xls
    wb_xls = xlrd.open_workbook(caminho_xls)
    ws_xls = wb_xls.sheet_by_index(0)

    # Criar .xlsx
    wb_xlsx = Workbook()
    ws_xlsx = wb_xlsx.active

    for row in range(ws_xls.nrows):
        for col in range(ws_xls.ncols):
            cell = ws_xls.cell(row, col)
            valor = cell.value
            # xlrd retorna floats para números inteiros — corrigir
            if cell.ctype == xlrd.XL_CELL_NUMBER and valor == int(valor):
                valor = int(valor)
            ws_xlsx.cell(row=row + 1, column=col + 1, value=valor)

    caminho_xlsx = caminho_xls.rsplit('.', 1)[0] + '.xlsx'
    wb_xlsx.save(caminho_xlsx)
    wb_xlsx.close()
    wb_xls.release_resources()

    return caminho_xlsx


def limpar_arquivos_antigos():
    """Remove arquivos temporários com mais de 1 hora."""
    agora = datetime.now().timestamp()
    try:
        for f in os.listdir(UPLOAD_FOLDER):
            caminho = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(caminho):
                idade = agora - os.path.getmtime(caminho)
                if idade > 3600:  # 1 hora
                    os.remove(caminho)
    except Exception:
        pass


# ============================================================================
# ROTAS PRINCIPAIS
# ============================================================================

@app.route('/')
def index():
    """Página principal."""
    limpar_arquivos_antigos()
    return render_template('index.html')


@app.route('/converter', methods=['POST'])
def converter():
    """Converte Excel para JSON."""
    if 'arquivo' not in request.files:
        return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado.'}), 400

    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo selecionado.'}), 400

    if not extensao_permitida(arquivo.filename, EXTENSOES_PERMITIDAS_EXCEL):
        ext = os.path.splitext(arquivo.filename)[1].lower()
        if ext == '.xls':
            return jsonify({'sucesso': False, 'erro': 'O formato antigo .xls não é suportado. Abra o arquivo no Excel e salve como .xlsx (Pasta de Trabalho do Excel).'}), 400
        return jsonify({'sucesso': False, 'erro': 'Formato inválido. Envie um arquivo .xlsx'}), 400

    modo = request.form.get('modo', 'api_post')
    if modo not in ['post', 'put', 'api_post', 'api_put', 'completo']:
        return jsonify({'sucesso': False, 'erro': 'Modo inválido.'}), 400

    # Valores padrão para colunas que podem não existir na planilha
    cnpj_padrao = request.form.get('cnpj_padrao', '').strip()
    modalidade_padrao = request.form.get('modalidade_padrao', '').strip()

    try:
        # Salvar arquivo temporário
        uid = str(uuid.uuid4())[:8]
        nome_seguro = secure_filename(arquivo.filename)
        caminho_excel = os.path.join(UPLOAD_FOLDER, f"{uid}_{nome_seguro}")
        arquivo.save(caminho_excel)

        # Auto-converter .xls → .xlsx
        ext = os.path.splitext(caminho_excel)[1].lower()
        if ext == '.xls':
            try:
                caminho_xlsx = converter_xls_para_xlsx(caminho_excel)
                os.remove(caminho_excel)
                caminho_excel = caminho_xlsx
            except Exception as e:
                os.remove(caminho_excel)
                return jsonify({
                    'sucesso': False,
                    'erro': f'Erro ao converter .xls para .xlsx: {str(e)}. Tente abrir no Excel e salvar como .xlsx manualmente.'
                }), 400

        # Montar defaults
        defaults = {}
        if cnpj_padrao:
            defaults['cpfCnpjRaiz'] = cnpj_padrao
        if modalidade_padrao:
            defaults['modalidade'] = modalidade_padrao

        # Auto-truncar campos longos?
        auto_truncar = request.form.get('auto_truncar', 'false').lower() == 'true'

        # Converter
        conversor = ConversorCatalogoSiscomex(auto_truncar=auto_truncar)
        produtos = conversor.ler_planilha(caminho_excel, defaults=defaults)

        if conversor.erros:
            # Limpar
            os.remove(caminho_excel)
            return jsonify({
                'sucesso': False,
                'erro': 'Erros encontrados na planilha.',
                'erros': conversor.erros,
                'avisos': conversor.avisos
            }), 400

        if not produtos:
            os.remove(caminho_excel)
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum produto encontrado na planilha. Verifique se os dados começam na linha correta.'
            }), 400

        # Gerar JSON
        if modo == 'post':
            json_data = conversor.gerar_json_post(produtos)
        elif modo == 'put':
            json_data = conversor.gerar_json_put(produtos)
        elif modo == 'api_post':
            json_data = conversor.gerar_json_api_post(produtos)
        elif modo == 'api_put':
            json_data = conversor.gerar_json_api_put(produtos)
        else:
            json_data = conversor.gerar_json_completo(produtos)

        # Salvar JSON temporário para download
        nome_json = f"{uid}_CATALOGO_{modo.upper()}.json"
        caminho_json = os.path.join(UPLOAD_FOLDER, nome_json)
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Limpar Excel
        os.remove(caminho_excel)

        # Resposta
        json_preview = json.dumps(json_data[:3], ensure_ascii=False, indent=2)
        if len(json_data) > 3:
            json_preview += f"\n\n... e mais {len(json_data) - 3} produto(s)"

        return jsonify({
            'sucesso': True,
            'mensagem': f'{len(json_data)} produto(s) convertido(s) com sucesso!',
            'total_produtos': len(json_data),
            'modo': modo.upper(),
            'arquivo_download': nome_json,
            'preview': json_preview,
            'json_completo': json.dumps(json_data, ensure_ascii=False, indent=2),
            'avisos': conversor.avisos
        })

    except zipfile.BadZipFile:
        return jsonify({
            'sucesso': False,
            'erro': 'O arquivo não é um .xlsx válido. Provavelmente está no formato antigo .xls renomeado para .xlsx. Abra o arquivo no Excel, clique em Salvar Como e escolha "Pasta de Trabalho do Excel (.xlsx)".'
        }), 400
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro inesperado: {str(e)}'
        }), 500


@app.route('/json-para-excel', methods=['POST'])
def json_para_excel():
    """Converte JSON do portal para Excel."""
    if 'arquivo' not in request.files:
        return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado.'}), 400

    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo selecionado.'}), 400

    if not extensao_permitida(arquivo.filename, EXTENSOES_PERMITIDAS_JSON):
        return jsonify({'sucesso': False, 'erro': 'Formato inválido. Envie um arquivo .json'}), 400

    try:
        uid = str(uuid.uuid4())[:8]
        nome_seguro = secure_filename(arquivo.filename)
        caminho_json = os.path.join(UPLOAD_FOLDER, f"{uid}_{nome_seguro}")
        arquivo.save(caminho_json)

        nome_excel = f"{uid}_CATALOGO_EDITAVEL.xlsx"
        caminho_excel = os.path.join(UPLOAD_FOLDER, nome_excel)

        conversor = ConversorCatalogoSiscomex()
        conversor.json_para_planilha(caminho_json, caminho_excel)

        # Contar produtos
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            total = len(dados) if isinstance(dados, list) else 1

        os.remove(caminho_json)

        return jsonify({
            'sucesso': True,
            'mensagem': f'{total} produto(s) convertido(s) para Excel!',
            'total_produtos': total,
            'arquivo_download': nome_excel
        })

    except json.JSONDecodeError:
        return jsonify({'sucesso': False, 'erro': 'JSON inválido. Verifique o formato do arquivo.'}), 400
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': f'Erro: {str(e)}'}), 500


@app.route('/modelo')
def baixar_modelo():
    """Gera e baixa a planilha modelo."""
    try:
        uid = str(uuid.uuid4())[:8]
        nome = f"MODELO_catalogo_siscomex.xlsx"
        caminho = os.path.join(UPLOAD_FOLDER, f"{uid}_{nome}")

        conversor = ConversorCatalogoSiscomex()
        conversor.gerar_planilha_modelo(caminho)

        return send_file(
            caminho,
            as_attachment=True,
            download_name=nome,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@app.route('/download/<nome_arquivo>')
def download(nome_arquivo):
    """Download de arquivos gerados."""
    nome_seguro = secure_filename(nome_arquivo)
    caminho = os.path.join(UPLOAD_FOLDER, nome_seguro)

    if not os.path.exists(caminho):
        return jsonify({'sucesso': False, 'erro': 'Arquivo não encontrado ou expirado.'}), 404

    # Determinar nome de download amigável
    partes = nome_seguro.split('_', 1)
    nome_download = partes[1] if len(partes) > 1 else nome_seguro

    mimetype = 'application/json'
    if nome_seguro.endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return send_file(
        caminho,
        as_attachment=True,
        download_name=nome_download,
        mimetype=mimetype
    )


@app.route('/validar', methods=['POST'])
def validar():
    """Valida planilha sem gerar JSON."""
    if 'arquivo' not in request.files:
        return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado.'}), 400

    arquivo = request.files['arquivo']
    if not extensao_permitida(arquivo.filename, EXTENSOES_PERMITIDAS_EXCEL):
        ext = os.path.splitext(arquivo.filename)[1].lower()
        if ext == '.xls':
            return jsonify({'sucesso': False, 'erro': 'O formato antigo .xls não é suportado. Abra o arquivo no Excel e salve como .xlsx.'}), 400
        return jsonify({'sucesso': False, 'erro': 'Formato inválido. Envie .xlsx'}), 400

    try:
        uid = str(uuid.uuid4())[:8]
        caminho = os.path.join(UPLOAD_FOLDER, f"{uid}_{secure_filename(arquivo.filename)}")
        arquivo.save(caminho)

        conversor = ConversorCatalogoSiscomex()
        produtos = conversor.ler_planilha(caminho)

        os.remove(caminho)

        if conversor.erros:
            return jsonify({
                'sucesso': False,
                'valido': False,
                'total_produtos': 0,
                'erros': conversor.erros,
                'avisos': conversor.avisos
            })

        return jsonify({
            'sucesso': True,
            'valido': True,
            'total_produtos': len(produtos),
            'erros': [],
            'avisos': conversor.avisos
        })

    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@app.route('/atributos')
def listar_atributos():
    """Retorna lista de atributos conhecidos."""
    return jsonify(ATRIBUTOS_LABELS)


# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
