# Usar imagem Python 3.11 slim (mais leve)
FROM python:3.11-slim

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Copiar arquivo de dependências
COPY requirements.txt .

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY web_app.py .
COPY templates/ templates/
COPY Colet_JSON_autentic.py .
COPY colet_json_noautentic.py .


# Criar volume para o banco de dados persistir
VOLUME ["/app/data"]

# Expor porta 5000
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "web_app.py"]
