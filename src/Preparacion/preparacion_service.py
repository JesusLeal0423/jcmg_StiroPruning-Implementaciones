import pandas as pd
import uuid
import os
import chromadb

from src.STORI.STORI import load_config, generar_stori, exportar_csv
from src.perfiladoCSV import perfilado_csv
from src.find_hyperparams import run_grid_search

#from STORI.STORI import load_config, generar_stori, exportar_csv
#from perfiladoCSV import perfilado_csv

ruta_actual = os.path.dirname(os.path.abspath(__file__))

archivo_log = os.path.join(
    ruta_actual,
    "preparaciones.log"
)

from pathlib import Path

UPLOAD_DIR = Path("data/uploads")

def obtener_ultimo_csv():

    archivos = list(UPLOAD_DIR.glob("*.csv"))

    if not archivos:
        raise Exception("No hay archivos CSV cargados.")

    return max(
        archivos,
        key=lambda x: x.stat().st_mtime
    )

def iniciar_preparacion(
    modelo= None, 
    saveCSV=None, 
    
    spatialVariables = None, 
    interestVariables = None, 
    temporalVariable = None, 
    observableVariable = None, 
    referenceVariable = None
    
    ):

    print("Cargando configuración STORI...")

    config = load_config()
    
    config["spatialVariables"] = {
    str(i): col
        for i, col in enumerate(spatialVariables)
    }

    config["interestVariables"] = {
        str(i): col
        for i, col in enumerate(interestVariables)
    }

    config["temporalVariables"]["Date"] = temporalVariable

    config["observableVariables"] = {
        "observable": observableVariable
    }

    config["referenceVariable"] = referenceVariable

    csv_subido = obtener_ultimo_csv()

    stori_df = generar_stori(
        config,
        csv_path=str(csv_subido)
    )

    if len(stori_df) == 0:
        raise Exception("No se generaron registros STORI")

    # Exportar dataset preparado
    
    nombre_stori = f"{csv_subido.stem}_stori.csv"
    
    csv_path = os.path.join(
        ruta_actual,
        "..",
        "..",
        "data",
        nombre_stori
    )

    csv_path = os.path.abspath(csv_path)

    exportar_csv(stori_df, csv_path)
    

    # Perfilado
    reporte = perfilado_csv(csv_path)


    print("\n---- Metricas de Almacenamiento y Volumen ----")
    for k, v in reporte["metricas_generales"].items():
        print(f"{k}: {v}")


    print("\n---- Perfilado por Columna ----")
    for col in reporte["perfil_columnas"]:
        print("---------------------------")
        for k, v in col.items():
            print(f"{k}: {v}")  

    # Validaciones
    columnas_requeridas = [
        "spatial",
        "temporal",
        "interest",
        "reference",
        "observation"
    ]

    faltantes = [
        col
        for col in columnas_requeridas
        if col not in stori_df.columns
    ]

    
    print("\n---- Validación de Columnas Requeridas ----")
    if len(faltantes) > 0:
        raise Exception(
            f"Columnas faltantes: {faltantes}"
        )
    print("\nInfo: Todas las columnas requeridas estan completas\n")
        
    
    # Identificador de preparación
    id_preparacion = f"PREP-{str(uuid.uuid4())[:8]}"
    '''
    registro = pd.DataFrame([{
        "idPreparacion": id_preparacion,
        "registros": len(stori_df),
        "estatus": "PREPARACION_COMPLETADA",
        "fecha": pd.Timestamp.now()
    }])

    if os.path.exists(archivo_indices):
        anterior = pd.read_csv(archivo_indices)
        registro = pd.concat([anterior, registro], ignore_index=True)

    registro.to_csv(archivo_indices, index=False)
    '''
    
    #Implementación de la generación de embeddings automáticamente después de la preparación
    try:
        from src.generate_embedding import generar_embeddings

        print(f"saveCSV iniciar_preparacion: {saveCSV}")
        
        print("\nGenerando embeddings automáticamente...")
        generar_embeddings(
            modelo=modelo,
            input_data=csv_path,
            output_dir="test",
            resultado_preparacion={
                "idPreparacion": id_preparacion
            },
            saveCSV=saveCSV,
            dataset_name=csv_subido.stem
        )
        
        print("Antes de ejecutar optimización de clustering...")
        print("\nEjecutando optimización de clustering...")

        run_grid_search(
            modelo=modelo,
            output_dir="test",
            use_adjusted=False,
            max_evals=10
        )
        
        print("\nGrid Search finalizado.")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
    ''' '''
    with open(archivo_log, "a", encoding="utf-8") as log:

        log.write(
            f"[{pd.Timestamp.now()}] "
            f"ID={id_preparacion} | "
            f"REGISTROS={len(stori_df)} | "
            f"ESTATUS=PREPARACION_COMPLETADA\n"
        )
    
    return {
    "idPreparacion": id_preparacion,
    "estatus": "PREPARACION_COMPLETADA",
    "registrosDetectados": len(stori_df),
    "columnasDetectadas": len(stori_df.columns),
    #"\nmetricasGenerales": reporte["metricas_generales"],
    #"\nperfilColumnas": reporte["perfil_columnas"]
    }