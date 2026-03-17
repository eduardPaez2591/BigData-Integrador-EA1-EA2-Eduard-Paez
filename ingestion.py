import pandas as pd
import os
import sqlite3

def ingest_data():
    # Ruta del archivo CSV
    csv_file = 'data_raw/laptop_prices.csv'

    if not os.path.exists(csv_file):
        # Creamos un DataFrame de ejemplo
        print("⚠️ Archivo local no encontrado, creando datos de prueba basados en Kaggle...")
        data = {
            'Company': ['HP', 'Apple', 'Dell ', 'hp', 'Apple', 'Asus'],
            'Ram': ['8GB', '16GB', '8GB', '4GB', None, '16GB'],
            'Weight': ['2.1kg', '1.37kg', '2.3kg', '1.86kg', '1.34kg', None],
            'Price_euros': [950, 1339.69, 722, 439, 1200, 1500]
        }

        df = pd.DataFrame(data)
        os.makedirs("data_raw", exist_ok=True)
        df.to_csv(csv_file, index=False)

    df = pd.read_csv(csv_file)

    # Guardamos en SQLite
    os.makedirs("src/db", exist_ok=True)
    conn = sqlite3.connect("src/db/ingestion.db")
    df.to_sql('laptop_raw', conn, if_exists='replace', index=False)
    conn.close()

    print(f"✅ EA1: {len(df)} registros de Kaggle cargados en SQLite.")

if __name__ == "__main__":
    ingest_data()