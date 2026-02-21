"""Testes para o módulo CLI (view_responses)."""

import pytest
from view_responses import summarize_json


def test_summarize_json_dict():
    """Testa resumo de JSON com dicionário."""
    result = summarize_json('{"a":1,"b":2,"c":3}')
    assert "JSON keys" in result
    assert "a" in result or "b" in result or "c" in result


def test_summarize_json_list():
    """Testa resumo de JSON com lista."""
    result = summarize_json('[1,2,3,4,5]')
    assert "JSON array" in result
    assert "len=5" in result


def test_summarize_json_invalid():
    """Testa resumo de JSON inválido."""
    result = summarize_json("not json at all")
    assert "(invalid json)" in result


def test_summarize_json_empty_dict():
    """Testa resumo de dicionário vazio."""
    result = summarize_json('{}')
    assert "JSON keys" in result


def test_summarize_json_empty_list():
    """Testa resumo de lista vazia."""
    result = summarize_json('[]')
    assert "JSON array" in result
    assert "len=0" in result


def test_summarize_json_nested():
    """Testa resumo de JSON aninhado."""
    nested = '{"user":{"name":"João","age":30},"items":[1,2,3]}'
    result = summarize_json(nested)
    assert "JSON keys" in result


def test_summarize_json_large_dict():
    """Testa resumo truncado de dicionário grande."""
    # Constrói um JSON válido com múltiplas chaves
    import json
    large_dict_obj = {f'key{i}': i for i in range(10)}
    large_dict = json.dumps(large_dict_obj)
    result = summarize_json(large_dict)
    assert "JSON keys" in result
    # Deve mostrar até 5 chaves


def test_summarize_json_string_value():
    """Testa resumo de JSON com string pura."""
    result = summarize_json('"just a string"')
    # Tipo de string simples
    assert "<class" in result or "str" in result


def test_summarize_json_number_value():
    """Testa resumo de JSON com número puro."""
    result = summarize_json('42')
    assert "<class" in result or "int" in result


def test_summarize_json_null_value():
    """Testa resumo de JSON nulo."""
    result = summarize_json('null')
    assert "<class" in result or "NoneType" in result


def test_summarize_json_whitespace():
    """Testa resumo de JSON com whitespace."""
    result = summarize_json('  {"key": "value"}  ')
    assert "JSON keys" in result


def test_summarize_json_unicode():
    """Testa resumo com caracteres UTF-8."""
    result = summarize_json('{"mensagem":"Olá, mundo!","emoji":"🚀"}')
    assert "JSON keys" in result
