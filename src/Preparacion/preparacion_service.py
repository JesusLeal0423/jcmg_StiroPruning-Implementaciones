import pandas as pd
import uuid
import os

from src.STORI.STORI import load_config, generar_stori, exportar_csv
from src.perfiladoCSV import perfilado_csv

ruta_actual = os.path.dirname(os.path.abspath(__file__))

archivo_log = os.path.join(
    ruta_actual,
    "preparaciones.log"
)

def iniciar_preparacion():

    print("Cargando configuración STORI...")

    config = load_config()

    stori_df = generar_stori(config)

    if len(stori_df) == 0:
        raise Exception("No se generaron registros STORI")

    # Exportar dataset preparado
    csv_path = os.path.join(
        ruta_actual,
        "..",
        "..",
        "data",
        "sample.csv"
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
    "metricasGenerales": reporte["metricas_generales"],
    "perfilColumnas": reporte["perfil_columnas"]
    }