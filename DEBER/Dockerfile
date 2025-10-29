FROM python:3.9-slim

WORKDIR /app

# 1. Instalar herramientas básicas (versión actualizada)
RUN apt-get update && \
    apt-get install -y curl gnupg2 && \
    rm -rf /var/lib/apt/lists/*

# 2. Configurar repositorio MS SQL (método alternativo)
RUN mkdir -p /etc/apt/keyrings && \
    curl -sS https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# 3. Instalar dependencias
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev g++ && \
    rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "api/app.py"]