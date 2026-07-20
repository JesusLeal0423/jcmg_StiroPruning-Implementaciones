FROM python:3.11-slim

# Evita generar archivos .pyc y fuerza salida inmediata de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer FastAPI
EXPOSE 8000

# Ejecutar la API
CMD ["uvicorn", "src.predictApi.main:app", "--host", "0.0.0.0", "--port", "8000"]