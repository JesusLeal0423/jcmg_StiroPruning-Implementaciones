import json
import pandas as pd
import os


'''
def load_config(path="input_config.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["observatory"] if "observatory" in data else data
'''

def load_config(path=None):
    if path is None:
        path = os.path.join(
            os.path.dirname(__file__),
            "input_config.json"
        )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["observatory"] if "observatory" in data else data


def validar_columnas(df, columnas):
    faltantes = [col for col in columnas if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas en el CSV: {faltantes}")


def generar_stori(config, csv_path=None):
    print(" Leyendo CSV...")
    import os

    print("Ruta actual:", os.getcwd())
    print("Archivo existe:", os.path.exists(config["csv_path"]))
    
    #df = pd.read_csv(config["csv_path"])
####################################################
    base_dir = os.path.dirname(__file__)

    if csv_path is None:
        csv_path = os.path.abspath(
            os.path.join(base_dir, config["csv_path"])
        )
    
    print("Ruta actual:", os.getcwd())
    print("CSV utilizado:", csv_path)
    print("Archivo existe:", os.path.exists(csv_path))
    
    df = pd.read_csv(csv_path)
####################################################
    print(df.columns.tolist())

    # Obtiene nombres reales de columnas
    spatial_cols = list(config["spatialVariables"].values())
    temporal_col = config["temporalVariables"]["Date"]
    observable_col = list(config["observableVariables"].values())[0]
    interest_cols = list(config["interestVariables"].values())

    # Valida que existan en el CSV
    validar_columnas(df, spatial_cols + [temporal_col, observable_col] + interest_cols)

    print(" Transformando datos a formato STORI...")

    # Spatial 
    df["spatial"] = df[spatial_cols].astype(str).agg(".".join, axis=1)

    # Temporal
    df["temporal"] = df[temporal_col]

    # Interest (puedes ajustar combinación)
    df["interest"] = df[interest_cols].astype(str).agg(".".join, axis=1)

    # Observation
    df["observation"] = df[observable_col]

    # Reference (placeholder)
    df["reference"] = df["TASA_TYPE"]

    # Seleccionar columnas finales
    stori_df = df[["spatial", "temporal", "interest", "observation", "reference"]]

    print(" STORI generado correctamente")
    print(stori_df.head())

    return stori_df


def exportar_csv(df, output_path):
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"CSV exportado en: {output_path}")

def main():
    print(" Cargando configuración...")
    config = load_config()

    stori_df = generar_stori(config)

    print(f"\n Total registros: {len(stori_df)}")

    exportar_csv(stori_df)


if __name__ == "__main__":
    main()