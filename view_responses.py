import sqlite3
# Biblioteca para manipular JSON (serializar / desserializar)
import json
# Biblioteca para tratar argumentos de linha de comando
import argparse
# Biblioteca para operações com caminhos e verificação de arquivos
import os
# Biblioteca para exportar CSVs
import csv

# Caminho padrão do banco de dados: arquivo "responses.db" no mesmo diretório
DEFAULT_DB = os.path.join(os.path.dirname(__file__), "responses.db")


def summarize_json(json_text: str) -> str:
    """Tenta converter `json_text` em objeto Python e retorna um resumo curto.

    - Se for um dicionário, retorna as primeiras chaves.
    - Se for uma lista, retorna o tamanho.
    - Se não for JSON válido, retorna um marcador.
    """
    try:
        # Desserializa o texto JSON em um objeto Python
        obj = json.loads(json_text)
        # Se for dict, mostra até 5 chaves como resumo
        if isinstance(obj, dict):
            keys = list(obj.keys())[:5]
            return f"JSON keys: {keys}"
        # Se for lista, informa o tamanho
        if isinstance(obj, list):
            return f"JSON array, len={len(obj)}"
        # Caso geral: retorna o tipo do objeto
        return str(type(obj))
    except Exception:
        # Em caso de erro de parse, informa que não é JSON válido
        return "(invalid json)"


def main():
    """Entrada principal do script: lista registros e opcionalmente exporta CSV."""

    # Parser para os argumentos de linha de comando
    p = argparse.ArgumentParser(description="List and export responses.db records")
    # Argumento para caminho do DB (usa DEFAULT_DB por padrão)
    p.add_argument("--db", default=DEFAULT_DB, help="Path to responses.db")
    # Quantos registros recentes listar
    p.add_argument("--limit", type=int, default=20, help="How many recent records to show")
    # Caminho de saída CSV opcional
    p.add_argument("--export", help="Optional CSV path to export results")
    # Flag para imprimir o corpo das respostas (pode ser grande)
    p.add_argument("--show-body", action="store_true", help="Print body contents (may be large)")
    args = p.parse_args()

    # Verifica se o arquivo do DB existe antes de abrir
    if not os.path.exists(args.db):
        print(f"Database not found: {args.db}")
        return

    # Abre conexão SQLite e obtém um cursor
    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    # Obtém número total de registros da tabela (tratando erros)
    try:
        cur.execute("SELECT count(*) FROM responses")
        total = cur.fetchone()[0]
    except sqlite3.Error as e:
        # Em caso de erro SQL, fecha conexão e termina
        print(f"DB error: {e}")
        conn.close()
        return

    # Mostra resumo básico do banco
    print(f"DB: {args.db}")
    print(f"Total records: {total}\n")

    # Lê a estrutura da tabela `responses` usando PRAGMA
    cur.execute("PRAGMA table_info(responses)")
    cols = [r[1] for r in cur.fetchall()]
    print("Columns:", cols)
    print()

    # Consulta as linhas mais recentes conforme o limite informado
    cur.execute(
        "SELECT id, url, status, timestamp, body, json FROM responses ORDER BY timestamp DESC LIMIT ?",
        (args.limit,),
    )

    # Busca todos os resultados retornados pela query
    rows = cur.fetchall()

    # Lista temporária com dicionários para exportação se pedido
    out_rows = []
    for r in rows:
        # Desempacota cada linha nas colunas conhecidas
        id_, url, status, ts, body, json_text = r
        # Formata uma linha compacta para visualização no console
        line = f"{id_:4d} | {ts} | {status or '-':3} | {url}"
        print(line)
        # Se houver JSON salvo, imprime um resumo do JSON
        if json_text:
            print("    ", summarize_json(json_text))
        else:
            # Caso não haja JSON, opcionalmente mostra preview do body
            if args.show_body and body:
                preview = body[:400].replace('\n', '\\n')
                print("    body preview:", preview)
        # Acumula o registro para possível exportação em CSV
        out_rows.append({
            "id": id_,
            "url": url,
            "status": status,
            "timestamp": ts,
            "body": body,
            "json": json_text,
        })

    # Fecha a conexão com o banco
    conn.close()

    # Se foi solicitado exportar, grava um CSV com os registros exibidos
    if args.export:
        keys = ["id", "url", "status", "timestamp", "body", "json"]
        try:
            with open(args.export, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for r in out_rows:
                    writer.writerow(r)
            print(f"\nExported {len(out_rows)} rows to {args.export}")
        except Exception as e:
            # Mostra erro e não lança exceção para não quebrar o script
            print(f"Failed to export CSV: {e}")


if __name__ == "__main__":
    # Ponto de entrada: executa a função principal quando chamado diretamente
    main()
    main()
