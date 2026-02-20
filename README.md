# Colet JSON - Coletor de Dados HTTP com Interface Web

Sistema automatizado para coletar dados de URLs com suporte a autenticação básica, armazenamento em SQLite e visualização web.

## Funcionalidades

- ✅ Coleta de dados via HTTP com autenticação básica (401 Unauthorized)
- ✅ Armazenamento em banco SQLite
- ✅ Interface web (Flask) para gerenciar coletas
- ✅ Exportação individual de registros em HTML
- ✅ Deleção de registros
- ✅ Suporte a Docker para fácil deploy

## Estrutura do Projeto

```
.
├── web_app.py                    # Aplicação Flask principal
├── Colet_JSON_autentic.py       # Coleta com autenticação
├── colet_json_noautentic.py     # Coleta sem autenticação
├── view_responses.py             # Visualizador CLI do banco
├── templates/                    # Templates HTML (Jinja2)
│   ├── index.html               # Página principal
│   └── view.html                # Página de detalhes
├── requirements.txt              # Dependências Python
├── Dockerfile                    # Build Docker
├── docker-compose.yml            # Orquestração Docker
└── README.md                     # Este arquivo
```

## Instalação Local

### Pré-requisitos
- Python 3.11+
- pip

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/colet-json.git
cd colet-json
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python web_app.py
```

5. Abra no navegador:
```
http://127.0.0.1:5000
```

## Uso com Docker

### Build e Run Rápido

```bash
docker-compose up --build
```

Acesse: `http://localhost:5000`

### Parar o container

```bash
docker-compose down
```

## Uso da Aplicação Web

### 1. Coletar dados de uma URL

1. Digite a URL no campo de entrada
2. Clique em "Coletar"
3. Se o site pedir autenticação (401), preencha login e senha
4. Os dados serão salvos no banco SQLite

### 2. Visualizar um registro

- Clique em "Ver" para abrir os detalhes do registro

### 3. Exportar para HTML

- Clique em "HTML" para baixar o registro como arquivo HTML

### 4. Deletar um registro

- Clique em "Apagar" para remover o registro (pede confirmação)

### 5. Atualizar a página

- Clique em "Atualizar" para recarregar a lista de registros

## Scripts Utilitários

### Visualizar banco via CLI

```bash
python view_responses.py --limit 20
python view_responses.py --show-body
python view_responses.py --export responses_export.csv
```

### Coletar dados direto (sem interface web)

```bash
python Colet_JSON_autentic.py
```

## Banco de Dados

O banco SQLite (`responses.db`) é criado automaticamente com a tabela:

```sql
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    status INTEGER,
    timestamp TEXT NOT NULL,
    body TEXT,
    json TEXT
);
```

## Variáveis de Ambiente (Docker)

No `docker-compose.yml`, você pode configurar:

```yaml
environment:
  - FLASK_ENV=production
  - FLASK_DEBUG=0
```

## Deploy em Produção

### Usando Gunicorn (WSGI)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Em Docker

```bash
docker-compose -f docker-compose.yml up -d
```

## Estrutura de Dados

### Tabela `responses`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID único |
| url | TEXT | URL coletada |
| status | INTEGER | Código HTTP (200, 401, etc) |
| timestamp | TEXT | ISO 8601 (UTC) |
| body | TEXT | Corpo bruto da resposta |
| json | TEXT | JSON parseado (se aplicável) |

## Autenticação HTTP Basic

Quando um site retorna **401 Unauthorized**, a interface exibe um formulário para login e senha. O sistema usa autenticação **HTTP Basic** (Base64).

## Limitações e Considerações

- O SQLite é ideal para desenvolvimento local. Para produção, considere PostgreSQL/MySQL
- Sem HTTPS em desenvolvimento; adicione SSL em produção
- Sem controle de acesso (adicione autenticação web conforme necessário)
- Limite de tamanho de resposta: sem limite explícito (ajuste conforme necessário)

## Desenvolvimento

### Modo Debug

```bash
# Local (já ativa debug)
python web_app.py

# Docker (modo debug)
# Edite docker-compose.yml:
environment:
  - FLASK_ENV=development
  - FLASK_DEBUG=1
```

## Contribuição

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -am 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes

## Autor

Seu Nome - [GitHub](https://github.com/seu-usuario)

## Suporte

Para dúvidas ou issues, abra uma [issue no GitHub](https://github.com/seu-usuario/colet-json/issues)
