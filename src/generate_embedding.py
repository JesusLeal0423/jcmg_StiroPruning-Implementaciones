import pandas as pd
from Modules.model_manager import EmbeddingModelManager
import time
import os
import argparse
from Modules.chroma_service import ChromaService


# Argumentos de línea de comandos para seleccionar el modelo
parser = argparse.ArgumentParser(description="Generar embeddings con el modelo seleccionado.")
parser.add_argument(
    "--modelo",
    type=str,
    choices=["use", "st1", "st2", "st3"],
    required=True, 
    help="Modelo de embeddings a utilizar: use, st1, st2 o st3"
)
parser.add_argument(
    "--input_data",
    type=str,
    default="data/sample.csv",
    help="Ruta al archivo CSV de entrada")
parser.add_argument(
    "--output_dir",
    type=str,
    default="test",
    help="Directorio donde se guardarán los embeddings generados"
)

def generar_embeddings(
    modelo,
    input_data="data/sample.csv",
    output_dir="test",
    resultado_preparacion=None
):

    # Cargar el dataset de intents
    start_time = time.time()
    print("\nCargando dataset...")
    data_sample = pd.read_csv(input_data, sep=',', encoding='utf-8', low_memory=False)
    tiempo_carga = time.time() - start_time
    print(f"Dataset cargado en {tiempo_carga:.2f} segundos\n")


        # Concatenar solo las primeras 3 columnas (Spatial, Temporal, Interest)
    start_time = time.time()
    print("\nProcesando texto: reemplazando espacios y concatenando las primeras 3 columnas simulando una sentencia corta")

        # Guardar las columnas Reference y Observation para agregarlas al final
    reference_column = data_sample['reference'].copy()
    observation_column = data_sample['observation'].copy()

        # Extracción de las variables a convertir a embeddings
    columnas_embedding = data_sample[['spatial', 'temporal', 'interest']]
        # Convertir a sentencia
    all_intents = columnas_embedding.astype(str).map(lambda x: x.replace(' ', '_')).agg(' '.join, axis=1).tolist()

    print(f"\nTotal de registros procesados: {len(all_intents)}")
    print("Ejemplo de texto procesado")
    print(all_intents[0])

    tiempo_preprocesado = time.time() - start_time
    print(f"Procesamiento de texto completado en {tiempo_preprocesado:.2f} segundos\n")



        # Crear el administrador de modelos de embeddings
    start_time = time.time()
    manager = EmbeddingModelManager(save_dir=f"{output_dir}/embeddings")
        # Selección y carga del modelo
    modelos_dict = {
        "use": ("use", "use", "https://tfhub.dev/google/universal-sentence-encoder/4"),
        "st1": ("st1", "sentence_transformer", "all-mpnet-base-v2"),
        "st2": ("st2", "sentence_transformer", "all-MiniLM-L6-v2"),
        "st3": ("st3", "sentence_transformer", "paraphrase-mpnet-base-v2")
    }

        # Extraccion parametros del modelo
    nombre, tipo, ruta = modelos_dict[modelo]

    print(f"\nCargando modelo {nombre}")
    manager.load_model(nombre, tipo, ruta)
    tiempo_carga_modelo = time.time() - start_time
    print(f"Modelo cargado en {tiempo_carga_modelo:.2f} segundos\n")


        # Generar embeddings
    start_time = time.time()
    print(f"\nGenerando embeddings para {nombre}...")
    embeddings = manager.embed(nombre, all_intents, save_csv=True)

    tiempo_embeddings = time.time() - start_time
    print(f"Embeddings generados en {tiempo_embeddings:.2f} segundos\n")

    # Guardar embeddings en ChromaDB por dominio
    start_time = time.time()
    print("\nGuardando embeddings en ChromaDB...")

    # Definir dominio a partir del nombre del archivo de entrada
    domain = os.path.splitext(os.path.basename(input_data))[0].lower()

    # Crear instancia de Chroma
    chroma = ChromaService(collection_prefix="stori")

    # ID de preparación para diferenciar ejecuciones
    if resultado_preparacion:
        id_preparacion = resultado_preparacion.get("idPreparacion", "PREP-SIN-ID")
    else:
        id_preparacion = "PREP-SIN-ID"

    # IDs únicos por registro
    ids = [f"{domain}_{id_preparacion}_{i}" for i in range(len(all_intents))]

    # Documents: texto STORI que se embebe
    documents = all_intents

    # Metadatos por registro
    metadatas = []
    for i in range(len(all_intents)):
        metadatas.append({
            "modelo": nombre,
            #"label": int(label),
            "id_preparacion": id_preparacion,
            "reference": str(reference_column.iloc[i]),
            "observation": str(observation_column.iloc[i])
        })

    # Insertar embeddings en la colección del dominio
    resultado_chroma = chroma.add_embeddings(
        domain=domain,
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings,
        metadatas=metadatas,
        batch_size=100
    )

    tiempo_chroma = time.time() - start_time

    print("\nEmbeddings guardados en ChromaDB.")
    print(f"Colección: {resultado_chroma['collection']}")
    print(f"Insertados: {resultado_chroma['inserted']} de {resultado_chroma['total_received']}")
    print(f"Tiempo guardado Chroma: {tiempo_chroma:.2f} segundos")

    if resultado_chroma["failed_batches"]:
        print("\nLotes con error en ChromaDB:")
        for error in resultado_chroma["failed_batches"]:
            print(error)

    start_time = time.time()
    # Crear DataFrame con las columnas Reference y Observation al inicio, seguidas de los embeddings
    print("\nConcatenando columnas Reference y Observation con los embeddings")
    embeddings_df = pd.DataFrame(embeddings)

    # Agregar las columnas Reference y Observation al inicio
    final_df = pd.DataFrame({
        'Reference': reference_column,
        'Observation': observation_column
    })

    # Concatenar con los embeddings
    final_df = pd.concat([final_df, embeddings_df], axis=1)

    # Guardar el DataFrame completo
    model_dir = os.path.join(f"{output_dir}/embeddings", nombre)
    os.makedirs(model_dir, exist_ok=True)
    save_csv_path = os.path.join(model_dir, f"{nombre}_complete.csv")

    final_df.to_csv(save_csv_path, index=False)
    time_saved = time.time() - start_time
    print(f"Embeddings con columnas Reference y Observation guardados en '{save_csv_path}'")
    print(f"Embeddings guardados en {time_saved:.2f} segundos")

    # Guardar los tiempos en un CSV
    times = pd.DataFrame([{
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "modelo": nombre,
        "dominio": domain,
        "coleccion_chroma": resultado_chroma["collection"],
        "embeddings_insertados_chroma": resultado_chroma["inserted"],
        "tiempo_carga_dataset": round(tiempo_carga, 2),
        "tiempo_procesado_texto": round(tiempo_preprocesado, 2),
        "tiempo_carga_modelo": round(tiempo_carga_modelo, 2),
        "tiempo_generacion_embeddings": round(tiempo_embeddings, 2),
        "tiempo_guardado_chroma": round(tiempo_chroma, 2),
        "tiempo_guardado_embeddings_csv": round(time_saved, 2)
    }])

    csv_path = f"{output_dir}/embeddings/times_embeddings.csv"
    os.makedirs(f"{output_dir}/embeddings", exist_ok=True)

    if os.path.exists(csv_path):
        times_ant = pd.read_csv(csv_path)
        times = pd.concat([times_ant, times], ignore_index=True)

    times.to_csv(csv_path, index=False)
    print(f"\nTiempos guardados en '{csv_path}'")
    

#Este se hace para que el script pueda ejecutarse desde la terminal
if __name__ == "__main__":
    from Preparacion.preparacion_service import iniciar_preparacion
    
    args = parser.parse_args()
    resultado_preparacion = iniciar_preparacion(args.modelo)

    print("\n===== RESUMEN PREPARACION =====")
    for k, v in resultado_preparacion.items():
        print(f"{k}: {v}")

    generar_embeddings(
        modelo=args.modelo,
        input_data=args.input_data,
        output_dir=args.output_dir,
        resultado_preparacion=resultado_preparacion
    )
