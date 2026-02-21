"""Configurações compartilhadas entre todos os testes."""

import pytest
import sqlite3
import tempfile
import os


@pytest.fixture
def temp_db():
    """Cria um banco de dados SQLite temporário para testes.
    
    Yields:
        str: Caminho para o banco de dados temporário.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        # Importa aqui para evitar dependências circulares
        from colet_json_noautentic import init_sqlite
        init_sqlite(db_path)
        yield db_path


@pytest.fixture
def sample_json_response():
    """Fornece respostas JSON de exemplo para testes."""
    return {
        "id": 123,
        "name": "Test User",
        "email": "test@example.com",
        "tags": ["python", "testing", "api"],
        "active": True
    }


@pytest.fixture
def temp_in_memory_db():
    """Cria um banco de dados SQLite em memória para testes rápidos."""
    from colet_json_noautentic import init_sqlite
    # Usar ':memory:' cria um DB apenas em RAM
    init_sqlite(':memory:')
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            status INTEGER,
            timestamp TEXT NOT NULL,
            body TEXT,
            json TEXT
        );
        """
    )
    conn.commit()
    yield conn
    conn.close()
