import os
import pandas as pd

def perfilado_csv(ruta_csv):

    # Cargar la DB
    df = pd.read_csv(ruta_csv)

    
    # Metricas de almacenamiento y volumen

    tamano_archivo = os.path.getsize(ruta_csv) / (1024 * 1024)  # Los convertimos aMB

    total_registros = len(df)

    total_columnas = len(df.columns)    

    memoria_ram = df.memory_usage(deep=True).sum() / (1024 * 1024)  # Los convertimos a MB

    reporte = {
        "metricas_generales": {
            "Tamaño del archivo (MB)": round(tamano_archivo, 4),
            "Total de registros": total_registros,
            "Total de columnas": total_columnas,
            "Memoria RAM estimada (MB)": round(memoria_ram, 4)
        },
        "perfil_columnas": []
    }


    # Perfilado por columna

    for columna in df.columns:

        tipo = str(df[columna].dtype)

        nulos = df[columna].isnull().sum()
        
        porcentaje_nulos = (nulos / total_registros) * 100

        unicos = df[columna].nunique(dropna=True)

        memoria_columna = df[columna].memory_usage(deep=True) / (1024 * 1024)

        reporte["perfil_columnas"].append({
            "Nombre": columna,
            "Tipo": tipo,
            "Nulos": int(nulos),
            "Porcentaje Nulos": round(porcentaje_nulos, 2),
            "Valores Únicos": int(unicos),
            "Memoria (MB)": round(memoria_columna, 4)
        })

    return reporte