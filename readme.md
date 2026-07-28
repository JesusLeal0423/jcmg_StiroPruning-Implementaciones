# Proyecto de Embeddings y Clustering

Este proyecto implementa un sistema de preparación, vectorización y búsqueda semántica basado en STORI, UMAP, HDBSCAN y modelos de embeddings. El sistema permite cargar cualquier conjunto de datos en formato CSV, construir dinámicamente una matriz STORI mediante el mapeo de columnas definido por el usuario, generar embeddings, almacenarlos en ChromaDB y realizar búsquedas semánticas sobre los datos preparados.

## 📋 Requisitos del Sistema

* Python 3.8 o superior (Recomendación)
* pip (gestor de paquetes de Python)
* Git (opcional, para clonar el repositorio)
* Docker Desktop (Para deplegar la aplicación)



## 📁 Estructura del Proyecto
```
├── `data/`
│ ├── `H_Rates.csv` – Dataset principal de entrada  
│ ├── `clean_csv.py`
│ ├── `sample.py` 
│ └── `sample.csv` – Archivo de datos de prueba

├── `src`
│   ├── `Modules`
│   │   │── `chroma_service.py/` – Servicio para administrar ChromaDB y el almacenamiento
│   │   │── `ver_chroma.py/` – Este script nos ayuda a poder visualizar las colecciones guardadas en chroma
│   │   │── `classification_manager.py/` 
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
│
├── `test/`
│ ├── `embeddings/` – Embeddings generados
│ └── `Modelos/` – Modelos entrenados
│
│── `requirements.txt` – Dependencias del proyecto
│
├── `.dockerignore`
├── `docker-compose.yml`
├── `dockerfile` 
```


## 🚀 Instalación del Entorno

### 1. Clonar el repositorio

```bash
git clone https://github.com/JesusLeal0423/jcmg_StiroPruning-Implementaciones.git
```

### 2. Construir el proyecto

Primero nos colocamos en la raiz del proyecto:
```
cd jcmg_StiroPruning
```

Para posteriormente contruir la imagen del servicio de FastApi
```
docker compose build
```
Este comando realiza:
* La construcción del servicio
* Instala automáticamente todas las dependencias definidas en requirements.txt.

### 3. Iniciar los servicios

Una vez construida la imagen, ejecutar:

```
docker compose up
```
o
```
docker compose up -d
```
para ejecutarlo en segundo plano.

Docker va a iniciar automáticamente:

* El servicio FastAPI.
* La base de datos ChromaDB.

### 4. Verificar los contenedores

```
docker ps
```

Deberian aparecer dos contenedores parecidos a:
```
stiro_api
chromadb
```

### 5. Acceder a la API

Una vez iniciados los contenedores, la intefaz Swagger estará disponible en:
```
http://localhost:8001/docs
```
Desde esa interfaz pueden ejecutarse todos los endpoints disponibles.

## Complemetos

### 1. Detener los servicios
```
docker compose down
```

### 2. Reconstruir el proyecto
En caso de realizar modificaciones al código fuente:
```
docker compose up --build
```
## 📈 Flujo del sistema

Una vez desplegado el sistema, el flujo recomendado seria:

### 1. Carga del DataSet

Ejecutar el endpoint:
```
POST /api/v1/upload-csv
```
Este endpoint permite cargar cualquier archivo CSV (solamente archivos .csv) que será utilizado durante el proceso de preparación.

El archivo es almacenado automáticamente en la carpeta:
```
data/uploads/
```

### 2. Consultar Columnas

Una vez cargado el archivo, ejecutar:

```
GET /api/v1/csv/columnas
```
Este endpoint devuelve las columnas detectadas en el último CSV cargado.

Esto nos ayuda para poder tener una nocion sobre que columnas que tenemos en el DataSet para poder contruir la matriz STORI.

### 3. Preparación

Ejecutar el endpoint:
```
POST /api/v1/preparacion/iniciar
```
Este proceso realiza automáticamente:

* Construcción de la matriz STORI.
* Perfilado del dataset.
* Validación de columnas.
* Generación de embeddings.
* Almacenamiento de embeddings en ChromaDB.
* Optimización mediante Grid Search.

Durante esta etapa el usuario define cómo construir la matriz STORI indicando qué columnas del CSV corresponden a cada componente.


#### Ejemplo

```
{
  "modelo": "st1",
  "saveCSV_Local": true,

  "spatialVariables": [
    "PAIS",
    "ESTADO",
    "CIUDAD"
  ],

  "temporalVariable": "ANIO",

  "interestVariables": [
    "SEXO",
    "RANGO_EDAD",
    "ENFERMEDAD"
  ],

  "observableVariable": "CASOS",

  "referenceVariable": "FUENTE"
}
```



### 4. Carga o Entrenamiento del clasificador

Una vez generado el clustering, ejecutar el endpoint:
```
POST /loadClassifier
```
Si el clasificador solicitado no existe, el sistema lo entrenará automáticamente y almacenará el modelo para futuras consultas.

#### Ejemplo de petición
```

{
  "modelo": "st1",  // Modelo a elegir 
  "params": "separate_grid",
  "models_dir": "test/Modelos",
  "name_modelo": "mlp",
  "use_adjusted": false,
  "embeddings_path": "test/Embeddings"
}

```
* Modelos disponibles:
* `use`: Universal Sentence Encoder
* `st1`: all-mpnet-base-v2
* `st2`: all-MiniLM-L6-v2
* `st3`: paraphrase-mpnet-base-v2

Nota: Tendria que ser el mismo modelo con el cual se genero la preparacion;

## 5. Predicción

Finalmente ejecutar:
```
POST /api/v1/prediction/iniciar
```
Este endpoint:

* Genera el embedding de la consulta.
* Clasifica el vector.
* Consulta ChromaDB.
* Recupera los vectores más similares.
* Devuelve la respuesta en formato JSON.

#### Ejemplo de petición
```

{
  "modelo": "st1",    // Modelo a elegir 
  "classifier_model": "mlp",
  "use_adjusted": false,
  "vector_input": [   // Consulta a realizar
    "Total.Total",
    "2000",
    "Total.Total.H",
    "0.0668115769278366", 
    "100k"
  ],
  "domain": "H_Rates_Short", // Aqui se pone el nombre de la coleccion  a la cual se va a pedir la consulta, en otros terminos seria el nombre del dataset para mas practicidad
  "n_results": 10   // Numero de resultados similares a retornar
}

```
* Modelos disponibles:
* `use`: Universal Sentence Encoder
* `st1`: all-mpnet-base-v2
* `st2`: all-MiniLM-L6-v2
* `st3`: paraphrase-mpnet-base-v2

Nota: Tendria que ser el mismo modelo con el cual se genero la preparacion y con el que se guardo en el clasificador

## 📒 Endpoints Extra

### 1. GET /api/v1/prediction/status/{id_query} y tambien GET /api/v1/prediction/status

Permite consultar el estado de una predicción previamente iniciada.

Devuelve información como:

- Identificador de la consulta.
- Estado de la predicción.
- Resultado generado (cuando la ejecución ha finalizado).

Pide ingresar como parametros el id de la consulta que se vaya querer obtener infromación

### 2. /listClassifiers

Permite consultar con cuantos modelos contamos ya disponibles

### 3. GET /api/v1/chroma/colecciones

Devuelve todas las colecciones almacenadas en ChromaDB, para poder conocer los datasets disponibles para realizar predicciones.

## 🗃️ Persistencia

La base de datos ChromaDB utiliza un volumen Docker, por lo que:

Los embeddings permanecen almacenados aunque el contenedor sea detenido.
No es necesario volver a generar los embeddings mientras el volumen no sea eliminado.

## 📝 Notas Adicionales

* Los modelos de Sentence Transformers se descargan automáticamente la primera vez
* Universal Sentence Encoder requiere conexión a internet para la descarga inicial
* Los archivos de embeddings pueden ser grandes (varios GB dependiendo del dataset)
* Recomendado: al menos 8GB de RAM para datasets medianos
* Se esta incorporando el generate_embedding.py en el endpoint de preparación 
