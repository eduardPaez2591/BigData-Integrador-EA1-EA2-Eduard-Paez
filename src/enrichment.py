import pandas as pd
import sqlite3
import os
from datetime import datetime


def ejecutar_enriquecimiento():
    # 1. Carga desde la DB (Simulando Nube)
    path_base = "src/xlsx/cleaned_data.csv"
    if not os.path.exists(path_base):
        print(f"Archivo no encontrado: {path_base}")
        return
    
    df_base = pd.read_csv(path_base)

    # 2. CREACIÓN/LECTURA DE FUENTES ADICIONALES (Simulando múltiples formatos)
    # Fuente A: JSON (Costos de Garantía)
    data_garantia = {
        "Company": ["dell", "hp", "lenovo", "asus", "acer"],
        'Warranty_Price_EUR': [50, 150, 60, 45, 55]
    }
    df_garantia = pd.DataFrame(data_garantia)

    # Fuente B: TXT/CSV (Slogan de marketing)
    data_marketing = {
        "Company": ["dell", "hp", "lenovo", "asus", "acer"],
        'Slogan': ["Powerful and Reliable", "Innovation at its Best", "Think Different", "Inspiring Innovation", "Explore Beyond Limits"]
    }
    df_marketing = pd.DataFrame(data_marketing)

    # 3. ENRIQUECIMIENTO DE DATOS (JOINs)
    print("Enriqueciendo datos con información de garantía...")

    # Unimos con garantía (Left Join para no perder laptops si no hay garantía)
    df_enriquecido = pd.merge(df_base, df_garantia, on='Company', how='left')

    # Unimos con marketing (Left Join para no perder laptops si no hay slogan)
    df_enriquecido = pd.merge(df_enriquecido, df_marketing, on='Company', how='left')

    # 4. Transformaciones adicionales (Ejemplo: Costo total = laptop + Garantía)
    df_enriquecido['Total_Cost_EUR'] = df_enriquecido['Price_euros'] + df_enriquecido['Warranty_Price_EUR'].fillna(0)

    # 5. Guardar resultado enriquecido (Simulando subida a Nube)
    output_path = "src/xlsx/enriched_data.csv"
    df_enriquecido.to_csv(output_path, index=False)
    print(f"Enriquecimiento completado. Archivo guardado en: {output_path}")

    # 6. ARCHIVO DE AUDITORÍA (enrichment_report.txt)
    os.makedirs("src/static/auditoria", exist_ok=True)
    with open("src/static/auditoria/enriched_report.txt", "w", encoding='utf-8') as f:
        f.write("REPORTE DE ENRIQUECIMIENTO DE DATOS - EA3\n")
        f.write("="*50 + "\n")
        f.write(f"Fecha de proceso: {datetime.now()}\n")
        f.write(f"Registros Dataset Base: {len(df_base)}\n")
        f.write(f"Registros Dataset Enriquecido: {len(df_enriquecido)}\n")
        f.write("\nFUENTES INTEGRADAS:\n")
        f.write("- garantias.json: Incorporación de costos de servicio técnico.\n")
        f.write("- descripciones.txt: Agregado de slogans comerciales por marca.\n")
        f.write("\nOPERACIONES DE CRUCE:\n")
        f.write(f"- Coincidencias detectadas: {df_enriquecido['Warranty_Price_EUR'].notna().sum()} registros enriquecidos.\n")
        f.write("- Cálculo de nueva métrica: 'Total_Price_With_Warranty'.\n")

    print("✅ EA3: Enriquecimiento completado. Archivo generado en src/xlsx/enriched_data.csv")

if __name__ == "__main__":
    ejecutar_enriquecimiento()
