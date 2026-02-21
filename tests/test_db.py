"""Testes para o módulo de banco de dados SQLite."""

import sqlite3
import pytest
from pathlib import Path
from colet_json_noautentic import init_sqlite, save_response_sqlite


def test_init_sqlite_creates_db(tmp_path):
    """Testa se init_sqlite cria o arquivo de banco corretamente."""
    db_file = tmp_path / "test.db"
    
    init_sqlite(str(db_file))
    
    assert db_file.exists()


def test_init_sqlite_creates_table(tmp_path):
    """Testa se init_sqlite cria a tabela responses."""
    db_file = tmp_path / "test.db"
    
    init_sqlite(str(db_file))
    
    # Valida que a tabela foi criada
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='responses'")
    table = cur.fetchone()
    conn.close()
    
    assert table is not None


def test_init_sqlite_idempotent(tmp_path):
    """Testa se init_sqlite é idempotent (pode ser chamado múltiplas vezes)."""
    db_file = tmp_path / "test.db"
    
    init_sqlite(str(db_file))
    init_sqlite(str(db_file))  # Segunda chamada não deve falhar
    
    assert db_file.exists()


def test_save_response_sqlite_basic(tmp_path):
    """Testa inserção básica de uma resposta."""
    db_file = tmp_path / "test.db"
    
    init_sqlite(str(db_file))
    save_response_sqlite(
        url="http://example.com",
        status=200,
        body="OK",
        json_obj=None,
        db_path=str(db_file)
    )
    
    # Valida dados foram inseridos
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT url, status, body FROM responses")
    row = cur.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == "http://example.com"
    assert row[1] == 200
    assert row[2] == "OK"


def test_save_response_sqlite_with_json(tmp_path):
    """Testa inserção de resposta com JSON serializado."""
    db_file = tmp_path / "test.db"
    
    init_sqlite(str(db_file))
    json_data = {"id": 1, "name": "Test", "emoji": "🧪"}
    
    save_response_sqlite(
        url="http://api.example.com/test",
        status=200,
        body='{"id": 1, "name": "Test"}',
        json_obj=json_data,
        db_path=str(db_file)
    )
    
    # Valida JSON foi serializado corretamente
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT json FROM responses")
    row = cur.fetchone()
    conn.close()
    
    assert row is not None
    assert '"id": 1' in row[0]
    assert '"name": "Test"' in row[0]


def test_save_response_sqlite_timestamp(tmp_path):
    """Testa se o timestamp é registrado automaticamente."""
    db_file = tmp_path / "test.db"
    
    init_sqlite(str(db_file))
    save_response_sqlite(
        url="http://example.com",
        status=200,
        body="OK",
        db_path=str(db_file)
    )
    
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT timestamp FROM responses")
    row = cur.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] is not None
    assert "T" in row[0]  # Formato ISO


def test_save_response_sqlite_multiple(tmp_path):
    """Testa inserção de múltiplas respostas."""
    db_file = tmp_path / "test.db"
    
    init_sqlite(str(db_file))
    
    for i in range(5):
        save_response_sqlite(
            url=f"http://example.com/{i}",
            status=200 + i,
            body=f"Response {i}",
            db_path=str(db_file)
        )
    
    # Valida todas as respostas foram inseridas
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM responses")
    count = cur.fetchone()[0]
    conn.close()
    
    assert count == 5


def test_save_response_sqlite_special_chars(tmp_path):
    """Testa salvar respostas com caracteres especiais."""
    db_file = tmp_path / "test.db"
    
    init_sqlite(str(db_file))
    
    special_url = "http://example.com/café?query=tëst&emoji=🚀"
    special_body = '{"mensagem": "Olá, mundo!", "emoji": "🎉"}'
    
    save_response_sqlite(
        url=special_url,
        status=200,
        body=special_body,
        db_path=str(db_file)
    )
    
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT url, body FROM responses")
    row = cur.fetchone()
    conn.close()
    
    assert row[0] == special_url
    assert "🎉" in row[1]
