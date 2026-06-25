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
├── `data/`
│ ├── `H_Rates.csv` – Dataset principal de entrada  
│ ├── `clean_csv.py`
│ ├── `sample.py` 
│ └── `sample.csv` – Archivo de datos de prueba

├── `src`
│   ├── `Modules`
│   ├── `classification_manager.py/` 
│   │   ├── `clustering_manager.py/` – Gestor de clustering (UMAP + HDBSCAN)
│   │   ├── `estimators.py/`
│   │   ├── `model_manager.py/`  – Gestor de modelos de embeddings
│   │   └── `predict_vector.py/` – Predicción y búsqueda de similares
│   ├── `Preparacion/`
│   │   └── `preparacion_service.py/` – Servicio principal de preparación (validación, STORI, exportación) 
│   ├── `STORI/`
│   │   ├── `STORI.py/`  – Generación del formato STORI  
│   │   └── `input_config.json/` – Configuración de entrada STORI  
│   ├── `predictApi/`
│   │   ├── `main.py/` – Punto de entrada del servicio API
│   │   └── `train_clasifier.py/` – Entrenamiento de modelos
│   ├── `find_hyperparams.py/`
│   ├── `generate_embedding.py/` – Generación de embeddings
│   ├── `perfiladoCSV.py/` – Perfilado y análisis de sample.csv
│   └── `predict.py/` – Script de predicción

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

## Implementación realizada

Se implementó el servicio encargado de iniciar la etapa de preparación del sistema STIRO PRUNING. Esta funcionalidad permite:

- Recibir solicitudes mediante un endpoint REST.
- Validar la estructura mínima requerida de los datos de entrada.
- Generar la representación STORI a partir de los datos recibidos.
- Exportar los resultados a archivos CSV.
- Realizar el perfilado de los datos generados.
- Ejecutar validaciones sobre la información procesada.
- Registrar el estado de ejecución mediante logs.
- Retornar una respuesta en formato JSON con el resultado de la operación.

## Ejecución del proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/JesusLeal0423/jcmg_StiroPruning-Implementaciones.git
cd jcmg_StiroPruning
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar el servicio

```bash
uvicorn src.predictApi.main:app --reload
```

### 4. Acceder al servicio

Una vez iniciado, el servicio estará disponible en:

```
http://127.0.0.1:8000/docs
```

## Flujo de ejecución

1. Recepción de la solicitud.
2. Validación de la estructura mínima requerida.
3. Generación de la representación STORI.
4. Exportación de resultados a CSV.
5. Perfilado de datos.
6. Ejecución de validaciones.
7. Registro de logs.
8. Retorno de respuesta JSON.

## 📝 Notas Adicionales

* Los modelos de Sentence Transformers se descargan automáticamente la primera vez
* Universal Sentence Encoder requiere conexión a internet para la descarga inicial
* Los archivos de embeddings pueden ser grandes (varios GB dependiendo del dataset)
* Recomendado: al menos 8GB de RAM para datasets medianos
