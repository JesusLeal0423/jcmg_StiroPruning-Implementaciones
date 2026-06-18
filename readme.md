# Proyecto de Embeddings y Clustering

Este proyecto implementa un sistema de generación de embeddings y clustering usando UMAP + HDBSCAN con diferentes modelos de embeddings (Universal Sentence Encoder y Sentence Transformers).

## 📋 Requisitos del Sistema

* Python 3.8 o superior
* pip (gestor de paquetes de Python)
* Git (opcional, para clonar el repositorio)

## 🚀 Instalación del Entorno

### Crear Entorno Virtual

```
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### Instalar Dependencias

```
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

├── `src/`

│ ├── `Modules/`
│ │ ├── `model_manager.py` – Gestor de modelos de embeddings
│ │ ├── `clustering_manager.py` – Gestor de clustering (UMAP + HDBSCAN)
│ │ ├── `grid_search.py` – Búsqueda en grilla de hiperparámetros
│ │ └── `predict_vector.py` – Predicción y búsqueda de similares
│ ├── `generate_embedding.py` – Generación de embeddings
│ ├── `predict.py` – Script de predicción
│ └── `clustering_pipeline.py` – Pipeline completo de clustering

├── `data/`
│ └── `sample.csv` – Dataset de ejemplo

├── `test/`
│ ├── `embeddings/` – Embeddings generados
│ └── `Modelos/` – Modelos entrenados

└── `requirements.txt` – Dependencias del proyecto

## 🔧 Configuración Inicial

### Preparar Datos

Coloca tu dataset en `data/sample.csv` con el formato requerido.

### Crear Directorios

Directorio de pruebas para la generacion de embeddings.

```
mkdir -p test/embeddings
```

Directorio de pruebas para el guaardado de modelos de clustering y UMAP.

```
mkdir -p test/Modelos
```

## 📖 Uso Básico

### 1. Generar Embeddings

Colocarle en el directorio donde se encuentran los .py principales

```
cd src
```

Ejecutar el generador de embedings

```
python generate_embedding.py --modelo st1
```

* Modelos disponibles:
* `use`: Universal Sentence Encoder
* `st1`: all-mpnet-base-v2
* `st2`: all-MiniLM-L6-v2
* `st3`: paraphrase-mpnet-base-v2

### 2. Ejecutar Clustering

```
python clustering_pipeline.py --modelo <name_model> --max_evals <int>
```

### Realizar Predicciones

```
python predict.py --modelo <name_model> --params bayesiano --embeddings_path "../test/embeddings/<name_model>" --params_dir "../test/Modelos"
```

# Incorporaciones

En esta implementación se agregaron las siguientes funcionalidades al proyecto original:

- **Módulo STORI:** Conversión automática de datos observacionales al formato STORI a partir de un archivo de configuración (`input_config.json`).
- **Generación automática de `sample.csv`:** El pipeline genera el archivo `data/sample.csv`, que sirve como entrada para las siguientes etapas del procesamiento.
- **Perfilado de datos CSV:** Se incorporó un módulo que obtiene métricas generales del conjunto de datos, incluyendo:
  - Tamaño del archivo.
  - Número de registros y columnas.
  - Memoria estimada utilizada.
  - Tipo de dato por columna.
  - Valores nulos y porcentaje de nulos.
  - Valores únicos por columna.
  - Memoria consumida por cada columna.
- **Integración del pipeline:** El proceso de generación de STORI, perfilado del dataset y generación de embeddings se ejecuta de forma secuencial desde `generate_embedding.py`.

## 📝 Notas Adicionales

* Los modelos de Sentence Transformers se descargan automáticamente la primera vez
* Universal Sentence Encoder requiere conexión a internet para la descarga inicial
* Los archivos de embeddings pueden ser grandes (varios GB dependiendo del dataset)
* Recomendado: al menos 8GB de RAM para datasets medianos
