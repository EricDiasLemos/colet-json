from flask import Flask, render_template, g, request, Response, jsonify, current_app
import sqlite3
import json
import base64
import urllib.error
import urllib.request
import datetime
import os
import io
import csv

# Caminho para o arquivo SQLite que já existe no workspace
DATABASE = os.path.join(os.path.dirname(__file__), 'responses.db')

app = Flask(__name__)


def init_sqlite(db_path: str = DATABASE) -> None:
    """Cria o arquivo de banco e a tabela necessária caso não existam."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Cria tabela com campos: id, url, status, timestamp, body, json
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


def fetch_url(url: str, timeout: int = 10, username: str = None, password: str = None) -> tuple[int, str]:
    """Busca uma URL via HTTP com autenticação básica opcional."""
    headers = {
        "User-Agent": "PythonAutomator/1.0",
        "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
    }
    
    if username and password:
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers["Authorization"] = f"Basic {encoded_credentials}"
    
    request_obj = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(request_obj, timeout=timeout) as response:
            status_code = response.status
            body = response.read().decode("utf-8", errors="replace")
            return status_code, body
    except urllib.error.HTTPError as e:
        # Captura erros HTTP (ex: 401, 404, 500) e retorna o status
        status_code = e.code
        body = e.read().decode("utf-8", errors="replace")
        return status_code, body


def save_response_sqlite(url: str, status: int, body: str, json_obj: dict | None = None, db_path: str = None) -> None:
    """Insere resposta no banco de dados."""
    if db_path is None:
        db_path = DATABASE
    
    json_text = None
    if json_obj is not None:
        json_text = json.dumps(json_obj, ensure_ascii=False)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO responses (url, status, timestamp, body, json) VALUES (?, ?, ?, ?, ?)",
        (url, status, datetime.datetime.utcnow().isoformat(), body, json_text),
    )
    conn.commit()
    conn.close()


def get_db():
    """Abre (ou retorna) uma conexão SQLite por request usando `g`.

    Usa `row_factory` para permitir acesso por nome de coluna (row['id']).
    Também inicializa o banco se não existir.
    """
    # Obtém o caminho do banco da config ou usa o padrão
    db_path = current_app.config.get('DATABASE', DATABASE)
    
    # Garante que o banco de dados foi inicializado
    if not os.path.exists(db_path):
        init_sqlite(db_path)
    
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Fecha a conexão SQLite no final do contexto da aplicação (request)."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    """Página principal: lista registros recentes com link para detalhes."""
    limit = int(request.args.get('limit', 50))
    cur = get_db().execute('SELECT id, url, status, timestamp FROM responses ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cur.fetchall()
    return render_template('index.html', rows=rows)


@app.route('/view/<int:record_id>')
def view(record_id):
    """Mostra detalhes de um registro, incluindo JSON formatado quando presente."""
    cur = get_db().execute('SELECT * FROM responses WHERE id = ?', (record_id,))
    row = cur.fetchone()
    if not row:
        return 'Registro não encontrado', 404

    pretty_json = None
    if row['json']:
        try:
            obj = json.loads(row['json'])
            pretty_json = json.dumps(obj, indent=2, ensure_ascii=False)
        except Exception:
            pretty_json = '(JSON inválido)'

    return render_template('view.html', row=row, pretty_json=pretty_json)


@app.route('/export/<int:record_id>')
def export(record_id):
    """Exporta um registro individual como HTML e retorna como download."""
    cur = get_db().execute('SELECT id, url, status, timestamp, body, json FROM responses WHERE id = ?', (record_id,))
    row = cur.fetchone()
    
    if not row:
        return 'Registro não encontrado', 404

    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Registro """ + str(row['id']) + """ - Responses</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    h1 { color: #333; }
    .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .info { margin: 15px 0; }
    .label { font-weight: bold; color: #555; }
    .status-200 { color: #22863a; font-weight: bold; }
    .status-error { color: #cb2431; font-weight: bold; }
    .body-content { background: #f6f8fa; padding: 15px; border-radius: 4px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; font-family: monospace; font-size: 0.85em; margin-top: 10px; }
    a { color: #2563eb; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Registro #""" + str(row['id']) + """</h1>
    
    <div class="info">
      <span class="label">Timestamp:</span> """ + str(row['timestamp']) + """
    </div>
    
    <div class="info">
      <span class="label">Status:</span> 
      <span class=\"""" + ('status-200' if row['status'] == 200 else 'status-error') + """\">""" + str(row['status']) + """</span>
    </div>
    
    <div class="info">
      <span class="label">URL:</span> 
      <a href=\"""" + str(row['url']) + """\" target="_blank">""" + str(row['url']) + """</a>
    </div>
    
    <div class="info">
      <span class="label">Body:</span>
      <div class="body-content">""" + (row['body'].replace('<', '&lt;').replace('>', '&gt;') if row['body'] else '(vazio)') + """</div>
    </div>
  </div>
</body>
</html>"""
    
    return Response(html, mimetype='text/html; charset=utf-8', headers={'Content-Disposition': f'attachment; filename=response_{record_id}.html'})


@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    """Deleta um registro do banco de dados."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('DELETE FROM responses WHERE id = ?', (record_id,))
        conn.commit()
        return jsonify({'success': True, 'message': f'Registro {record_id} deletado com sucesso'}), 200
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Erro ao deletar: {str(exc)}'}), 500


@app.route('/collect', methods=['POST'])
def collect():
    """Coleta dados de uma URL e salva no banco de dados."""
    url = request.form.get('url', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if not url:
        return jsonify({'success': False, 'message': 'URL vazia'}), 400
    
    try:
        # Primeira tentativa: sem autenticação
        status, body = fetch_url(url)
        
        # Se retornar 401, pede credenciais
        if status == 401:
            if not username or not password:
                return jsonify({'success': False, 'auth_required': True, 'message': 'Este site requer autenticação. Por favor, forneça login e senha.'}), 401
            # Se forneceu credenciais, tenta novamente com autenticação
            status, body = fetch_url(url, username=username, password=password)
        
        # Tenta parsear como JSON
        json_obj = None
        try:
            json_obj = json.loads(body)
        except json.JSONDecodeError:
            pass
        
        # Salva no banco
        save_response_sqlite(url, status, body, json_obj)
        
        return jsonify({'success': True, 'message': f'Coletado com sucesso! Status: {status}'}), 200
    
    except urllib.error.URLError as exc:
        return jsonify({'success': False, 'message': f'Erro de rede: {exc.reason}'}), 400
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Erro: {str(exc)}'}), 500


if __name__ == '__main__':
    init_sqlite(DATABASE)
    print(f"[OK] Banco de dados inicializado: {DATABASE}")

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
