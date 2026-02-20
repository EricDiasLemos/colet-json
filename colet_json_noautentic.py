"""Exemplo simples de acesso HTTP automatizado (sem bibliotecas externas)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
import sqlite3
import datetime

def fetch_url(url: str, timeout: int = 10) -> tuple[int, str]:
	"""Busca uma URL via HTTP e retorna (status_code, corpo_texto)."""
	request = urllib.request.Request(
		url,
		headers={
			"User-Agent": "PythonAutomator/1.0",
			"Accept": "application/json, text/html;q=0.9, */*;q=0.8",
		},
	)

	with urllib.request.urlopen(request, timeout=timeout) as response:
		status_code = response.status
		body = response.read().decode("utf-8", errors="replace")
		return status_code, body


def fetch_json(url: str) -> dict:
	"""Exemplo de acesso a JSON."""
	status, body = fetch_url(url)
	if status != 200:
		raise RuntimeError(f"Resposta inesperada: {status}")
	return json.loads(body)

def init_sqlite(db_path: str = "responses.db") -> None:
	"""Cria o arquivo de banco e a tabela necessária caso não existam.

	A tabela `responses` armazena a resposta bruta (`body`) e uma cópia
	serializada em JSON (`json`) quando disponível, além de metadados.
	"""
	conn = sqlite3.connect(db_path)
	cur = conn.cursor()
	# Cria tabela com campos básicos: id, url, status, timestamp, body, json
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
	conn.close()


def save_response_sqlite(url: str, status: int, body: str, json_obj: dict | None = None, db_path: str = "responses.db") -> None:
	"""Insere uma linha na tabela `responses` com os dados fornecidos.

	- `json_obj` é serializado com `json.dumps` se não for None.
	- Usa timestamp UTC em formato ISO.
	"""
	# Serializa objeto JSON em string, se fornecido
	json_text = None
	if json_obj is not None:
		json_text = json.dumps(json_obj, ensure_ascii=False)

	# Abre conexão, insere e fecha conexão imediatamente para simplicidade
	conn = sqlite3.connect(db_path)
	cur = conn.cursor()
	cur.execute(
		"INSERT INTO responses (url, status, timestamp, body, json) VALUES (?, ?, ?, ?, ?)",
		(url, status, datetime.datetime.utcnow().isoformat(), body, json_text),
	)
	conn.commit()
	conn.close()


if __name__ == "__main__":
	try:  # Executar uma única vez
		# Define a URL alvo em uma variável para reutilização posterior
		url = "https://ericdiaslemos.github.io/Apresentacao/"

		# Faz a requisição usando a variável `url`
		status, body = fetch_url(url)
		print(f"Status: {status}")
		print(f"Resposta:\n{body}")

		try:
			data = json.loads(body)
			print(f"\n✓ Resposta em JSON:")
			print(json.dumps(data, indent=2, ensure_ascii=False))
			# Se foi possível parsear para JSON, garante que o DB exista e
			# salva a resposta completa e o JSON parseado no SQLite
			init_sqlite()
			save_response_sqlite(url, status, body, data)
		except json.JSONDecodeError:
			# Se não for JSON válido, ainda assim inicializa o DB e salva
			# a resposta bruta (campo json ficará NULL)
			init_sqlite()
			save_response_sqlite(url, status, body, None)

	except urllib.error.HTTPError as exc:
		print(f"Erro HTTP: {exc.code} - {exc.reason}")
	except urllib.error.URLError as exc:
		print(f"Erro de rede: {exc.reason}")

