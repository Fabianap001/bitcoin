import requests
import pandas as pd
from datetime import datetime
import os
from sklearn.linear_model import LinearRegression
import numpy as np
import time

# --- Parte 1: Obtener precio actual de Bitcoin y guardarlo en el historial ---

url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    precio_btc = data["bitcoin"]["usd"]
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_nuevo = pd.DataFrame([[fecha_actual, precio_btc]], columns=["Fecha", "Precio USD"])

    archivo_historial = "historial_btc.csv"
    if os.path.isfile(archivo_historial):
        df_nuevo.to_csv(archivo_historial, mode='a', header=False, index=False, sep=';')
    else:
        df_nuevo.to_csv(archivo_historial, index=False, sep=';')

    print("Precio actual de Bitcoin guardado:")
    print(df_nuevo)

except requests.exceptions.RequestException as e:
    print(f"Error al conectar con la API de CoinGecko: {e}")
except KeyError:
    print("Error: No se encontró 'bitcoin' o 'usd' en la respuesta de la API. Verifica el formato de la respuesta.")
    print("Respuesta de la API:", data)
except Exception as e:
    print(f"Ocurrió un error inesperado al procesar el precio: {e}")

# --- Parte 2: Cargar historial, entrenar modelo y predecir ---

archivo_historial = "historial_btc.csv"
archivo_prediccion = "prediccion_btc.csv"

if not os.path.isfile(archivo_historial):
    print("\nError: El archivo 'historial_btc.csv' no existe. No se puede realizar la predicción sin datos.")
else:
    try:
        df_hist = pd.read_csv(archivo_historial, sep=';')
        df_hist = df_hist[df_hist["Fecha"].str.len() >= 19].copy()
        df_hist["Timestamp"] = pd.to_datetime(df_hist["Fecha"], format="%Y-%m-%d %H:%M:%S", errors='coerce').astype(int) / 10**9
        df_hist.dropna(subset=["Timestamp"], inplace=True)

        if df_hist.empty:
            print("\nEl historial está vacío o no contiene datos válidos después de la limpieza. No se puede entrenar el modelo.")
        elif len(df_hist) < 2:
            print(f"\nSe necesitan al menos 2 puntos de datos para entrenar el modelo. Actualmente hay {len(df_hist)}.")
        else:
            X = df_hist["Timestamp"].values.reshape(-1, 1)
            y = df_hist["Precio USD"].values

            modelo = LinearRegression()
            modelo.fit(X, y)

            siguiente_timestamp = time.time() + 60  # 1 minuto adelante
            prediccion = modelo.predict([[siguiente_timestamp]])

            fecha_prediccion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df_pred = pd.DataFrame([[fecha_prediccion, round(prediccion[0], 2)]],
                                   columns=["Fecha", "Predicción USD"])

            # Guardar en el mismo archivo sin sobrescribir, manteniendo el historial
            if os.path.isfile(archivo_prediccion):
                df_pred.to_csv(archivo_prediccion, mode='a', header=False, index=False, sep=';')
            else:
                df_pred.to_csv(archivo_prediccion, index=False, sep=';')

            print("\nPredicción agregada al archivo de historial:")
            print(df_pred)

    except FileNotFoundError:
        print(f"\nError: El archivo '{archivo_historial}' no se encontró.")
    except pd.errors.EmptyDataError:
        print(f"\nError: El archivo '{archivo_historial}' está vacío. No hay datos para procesar.")
    except Exception as e:
        print(f"\nOcurrió un error al procesar el historial o al realizar la predicción: {e}")
