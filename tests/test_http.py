"""Testes para o módulo HTTP (fetch_url)."""

from unittest.mock import patch, MagicMock
import pytest
from colet_json_noautentic import fetch_url


@patch("urllib.request.urlopen")
def test_fetch_url_success(mock_urlopen):
    """Testa busca bem-sucedida de URL."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = b'{"ok": true}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    status, body = fetch_url("http://fake-url.example.com")

    assert status == 200
    assert body == '{"ok": true}'
    mock_urlopen.assert_called_once()


@patch("urllib.request.urlopen")
def test_fetch_url_404(mock_urlopen):
    """Testa resposta 404."""
    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.read.return_value = b"Not Found"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    status, body = fetch_url("http://fake-url.example.com/notfound")

    assert status == 404
    assert body == "Not Found"


@patch("urllib.request.urlopen")
def test_fetch_url_timeout(mock_urlopen):
    """Testa timeout na requisição."""
    import urllib.error
    mock_urlopen.side_effect = urllib.error.URLError("Connection timeout")

    with pytest.raises(urllib.error.URLError):
        fetch_url("http://fake-url.example.com", timeout=1)


@patch("urllib.request.urlopen")
def test_fetch_url_headers(mock_urlopen):
    """Valida headers na requisição."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = b"OK"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    fetch_url("http://example.com")

    # Verifica que a chamada foi feita
    mock_urlopen.assert_called_once()
    # Extrai o Request object passado
    call_args = mock_urlopen.call_args
    request_obj = call_args[0][0]
    
    # Valida header (case-insensitive)
    assert any(k.lower() == 'user-agent' for k in request_obj.headers.keys())
    # Obtém o valor do header independente do case
    ua_value = next(v for k, v in request_obj.headers.items() if k.lower() == 'user-agent')
    assert ua_value == "PythonAutomator/1.0"


@patch("urllib.request.urlopen")
def test_fetch_url_encoding(mock_urlopen):
    """Testa decodificação de UTF-8."""
    mock_response = MagicMock()
    mock_response.status = 200
    # Simula conteúdo UTF-8 com acentos
    mock_response.read.return_value = "Resposta com acentuação: café".encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    status, body = fetch_url("http://example.com")

    assert status == 200
    assert "café" in body
