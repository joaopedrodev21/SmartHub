
# Imagem base do Python compatível com o venv do projeto
FROM python:3.14-slim 

# Evita gerar arquivos .pyc e mantém logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Define diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do projeto necessárias 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos para o diretório de trabalho e instala as dependências do projeto
COPY requirements.txt .
# Instalação das dependências do projeto a partir do arquivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Exposição da porta da aplicação 
EXPOSE 8000

# Comando padrão para rodar o server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]