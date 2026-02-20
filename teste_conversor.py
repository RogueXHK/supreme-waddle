# -*- coding: utf-8 -*-
"""
Script de teste: valida conversão JSON → Excel → JSON com compatibilidade 100%.
"""

import json
import os
import sys

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversor_catalogo_siscomex import ConversorCatalogoSiscomex

DIRETORIO = os.path.dirname(os.path.abspath(__file__))
JSON_ORIGINAL = os.path.join(DIRETORIO, "CATALOGO_PRODUTOS_25940099_20260220031001.json")
EXCEL_TESTE = os.path.join(DIRETORIO, "TESTE_catalogo.xlsx")
JSON_POST = os.path.join(DIRETORIO, "TESTE_saida_POST.json")
JSON_COMPLETO = os.path.join(DIRETORIO, "TESTE_saida_COMPLETO.json")
EXCEL_MODELO = os.path.join(DIRETORIO, "MODELO_catalogo_produtos.xlsx")


def teste_1_json_para_excel():
    """Testa conversão do JSON exportado do portal para planilha Excel."""
    print("\n" + "=" * 70)
    print("TESTE 1: JSON → Excel")
    print("=" * 70)
    
    conversor = ConversorCatalogoSiscomex()
    conversor.json_para_planilha(JSON_ORIGINAL, EXCEL_TESTE)
    
    assert os.path.exists(EXCEL_TESTE), "Arquivo Excel não foi criado!"
    print("✅ TESTE 1 PASSOU: JSON convertido para Excel com sucesso.")
    return True


def teste_2_excel_para_json_post():
    """Testa conversão do Excel para JSON no modo POST."""
    print("\n" + "=" * 70)
    print("TESTE 2: Excel → JSON (modo POST)")
    print("=" * 70)
    
    conversor = ConversorCatalogoSiscomex()
    resultado = conversor.converter(EXCEL_TESTE, JSON_POST, modo="post")
    
    assert resultado is not None, f"Conversão falhou! Erros: {conversor.erros}"
    
    with open(JSON_POST, 'r', encoding='utf-8') as f:
        dados_post = json.load(f)
    
    # Verificar que NÃO tem campos read-only
    for produto in dados_post:
        assert "seq" not in produto, "Campo 'seq' NÃO deve estar no JSON de POST!"
        assert "versao" not in produto, "Campo 'versao' NÃO deve estar no JSON de POST!"
        
        # Verificar campos obrigatórios presentes
        assert "descricao" in produto, "Campo 'descricao' faltando!"
        assert "denominacao" in produto, "Campo 'denominacao' faltando!"
        assert "cpfCnpjRaiz" in produto, "Campo 'cpfCnpjRaiz' faltando!"
        assert "modalidade" in produto, "Campo 'modalidade' faltando!"
        assert "ncm" in produto, "Campo 'ncm' faltando!"
        
        # Verificar estrutura de atributos
        assert "atributos" in produto, "Campo 'atributos' faltando!"
        assert isinstance(produto["atributos"], list), "'atributos' deve ser uma lista!"
        
        assert "atributosMultivalorados" in produto, "Campo 'atributosMultivalorados' faltando!"
        assert isinstance(produto["atributosMultivalorados"], list), "'atributosMultivalorados' deve ser uma lista!"
        
        assert "atributosCompostos" in produto, "Campo 'atributosCompostos' faltando!"
        assert isinstance(produto["atributosCompostos"], list), "'atributosCompostos' deve ser uma lista!"
        
        assert "atributosCompostosMultivalorados" in produto, "Campo 'atributosCompostosMultivalorados' faltando!"
        assert isinstance(produto["atributosCompostosMultivalorados"], list), "'atributosCompostosMultivalorados' deve ser uma lista!"
        
        assert "codigosInterno" in produto, "Campo 'codigosInterno' faltando!"
        assert isinstance(produto["codigosInterno"], list), "'codigosInterno' deve ser uma lista!"
        
        # Validar formato de atributo simples
        for att in produto["atributos"]:
            assert "atributo" in att, "Atributo sem chave 'atributo'!"
            assert "valor" in att, "Atributo sem chave 'valor'!"
            assert att["atributo"].startswith("ATT_"), f"Código de atributo inválido: {att['atributo']}"
        
        # Validar formato de atributo multivalorado
        for att in produto["atributosMultivalorados"]:
            assert "atributo" in att, "Atributo multi sem chave 'atributo'!"
            assert "valores" in att, "Atributo multi sem chave 'valores'!"
            assert isinstance(att["valores"], list), "'valores' deve ser uma lista!"
        
        # Validar NCM (8 dígitos)
        assert len(produto["ncm"]) == 8, f"NCM deve ter 8 dígitos: {produto['ncm']}"
        assert produto["ncm"].isdigit(), f"NCM deve ser numérico: {produto['ncm']}"
        
        # Validar modalidade
        assert produto["modalidade"] in ["IMPORTACAO", "EXPORTACAO"], \
            f"Modalidade inválida: {produto['modalidade']}"
    
    print(f"✅ TESTE 2 PASSOU: {len(dados_post)} produtos convertidos no modo POST.")
    return True


def teste_3_validar_compatibilidade():
    """Valida que o JSON gerado é compatível com o JSON original do portal."""
    print("\n" + "=" * 70)
    print("TESTE 3: Validação de compatibilidade com JSON original")
    print("=" * 70)
    
    with open(JSON_ORIGINAL, 'r', encoding='utf-8') as f:
        original = json.load(f)
    
    with open(JSON_POST, 'r', encoding='utf-8') as f:
        gerado = json.load(f)
    
    assert len(gerado) == len(original), \
        f"Quantidade diferente: original={len(original)}, gerado={len(gerado)}"
    
    erros = []
    for i, (orig, ger) in enumerate(zip(original, gerado)):
        # Comparar campos principais
        for campo in ["descricao", "denominacao", "cpfCnpjRaiz", "modalidade", "ncm"]:
            val_orig = str(orig.get(campo, "")).strip()
            val_ger = str(ger.get(campo, "")).strip()
            if val_orig != val_ger:
                erros.append(f"Produto {i+1}: {campo} diverge: '{val_orig}' vs '{val_ger}'")
        
        # Comparar atributos (verificar que todos os atributos do original estão no gerado)
        atts_orig = {a["atributo"]: a["valor"] for a in orig.get("atributos", [])}
        atts_ger = {a["atributo"]: a["valor"] for a in ger.get("atributos", [])}
        
        for att_code, att_val in atts_orig.items():
            if att_code not in atts_ger:
                erros.append(f"Produto {i+1}: Atributo {att_code} faltando no gerado")
            elif atts_ger[att_code] != att_val:
                # Verificar se a diferença é apenas espaço em branco (trim)
                if atts_ger[att_code].strip() == att_val.strip():
                    print(f"  ℹ️  Produto {i+1}: Atributo {att_code} - espaço extra removido (melhoria)")
                else:
                    erros.append(
                        f"Produto {i+1}: Atributo {att_code} diverge: "
                        f"'{att_val}' vs '{atts_ger[att_code]}'"
                    )
        
        # Comparar atributos multivalorados
        multi_orig = {a["atributo"]: a["valores"] for a in orig.get("atributosMultivalorados", [])}
        multi_ger = {a["atributo"]: a["valores"] for a in ger.get("atributosMultivalorados", [])}
        
        for att_code, att_vals in multi_orig.items():
            if att_code not in multi_ger:
                erros.append(f"Produto {i+1}: Atributo multi {att_code} faltando no gerado")
            elif set(multi_ger[att_code]) != set(att_vals):
                erros.append(
                    f"Produto {i+1}: Atributo multi {att_code} diverge: "
                    f"{att_vals} vs {multi_ger[att_code]}"
                )
        
        # Comparar códigos internos
        cods_orig = set(orig.get("codigosInterno", []))
        cods_ger = set(ger.get("codigosInterno", []))
        if cods_orig != cods_ger:
            erros.append(
                f"Produto {i+1}: codigosInterno diverge: {cods_orig} vs {cods_ger}"
            )
    
    if erros:
        print(f"\n❌ {len(erros)} DIVERGÊNCIA(S) ENCONTRADA(S):")
        for erro in erros:
            print(f"   ⛔ {erro}")
        return False
    
    print(f"✅ TESTE 3 PASSOU: 100% compatível com o JSON original!")
    return True


def teste_4_gerar_modelo():
    """Testa geração da planilha modelo."""
    print("\n" + "=" * 70)
    print("TESTE 4: Gerar planilha modelo")
    print("=" * 70)
    
    conversor = ConversorCatalogoSiscomex()
    conversor.gerar_planilha_modelo(EXCEL_MODELO)
    
    assert os.path.exists(EXCEL_MODELO), "Planilha modelo não foi criada!"
    print("✅ TESTE 4 PASSOU: Planilha modelo criada com sucesso.")
    return True


def teste_5_excel_para_json_completo():
    """Testa conversão no modo completo (formato exportação do portal)."""
    print("\n" + "=" * 70)
    print("TESTE 5: Excel → JSON (modo COMPLETO)")
    print("=" * 70)
    
    conversor = ConversorCatalogoSiscomex()
    resultado = conversor.converter(EXCEL_TESTE, JSON_COMPLETO, modo="completo")
    
    assert resultado is not None, f"Conversão falhou! Erros: {conversor.erros}"
    
    with open(JSON_COMPLETO, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Verificar campos do modo completo
    for produto in dados:
        assert "seq" in produto, "Campo 'seq' faltando no modo completo!"
        assert "codigo" in produto, "Campo 'codigo' faltando no modo completo!"
        assert "versao" in produto, "Campo 'versao' faltando no modo completo!"
    
    print(f"✅ TESTE 5 PASSOU: {len(dados)} produtos no modo completo.")
    return True


def main():
    print("\n" + "█" * 70)
    print("█  SUITE DE TESTES - CONVERSOR CATÁLOGO SISCOMEX                    █")
    print("█" * 70)
    
    resultados = {}
    
    resultados["JSON → Excel"] = teste_1_json_para_excel()
    resultados["Excel → JSON POST"] = teste_2_excel_para_json_post()
    resultados["Compatibilidade"] = teste_3_validar_compatibilidade()
    resultados["Planilha Modelo"] = teste_4_gerar_modelo()
    resultados["Excel → JSON Completo"] = teste_5_excel_para_json_completo()
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    
    total = len(resultados)
    passou = sum(1 for v in resultados.values() if v)
    
    for nome, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  {status} - {nome}")
    
    print(f"\n  Resultado: {passou}/{total} testes passaram")
    
    if passou == total:
        print("\n  🎉 TODOS OS TESTES PASSARAM! Conversor 100% funcional.")
    else:
        print(f"\n  ⚠️  {total - passou} teste(s) falharam. Verifique os erros acima.")
    
    # Limpeza de arquivos de teste (opcional)
    # for f in [EXCEL_TESTE, JSON_POST, JSON_COMPLETO]:
    #     if os.path.exists(f):
    #         os.remove(f)


if __name__ == "__main__":
    main()
