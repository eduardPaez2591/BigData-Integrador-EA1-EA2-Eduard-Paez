import pandas as pd
import sqlite3
import os
import numpy as np
from datetime import datetime

def ejecutar_limpieza_avanzada():
    # 1. Carga desde la DB (Simulando Nube)
    conn = sqlite3.connect("src/db/ingestion.db")
    df = pd.read_sql_query("SELECT * FROM laptop_raw", conn)
    conn.close()

    # Rastrear estadísticas para auditoría
    stats = {
        "registros_iniciales": len(df),
        "nulos_antes": df.isnull().sum().to_dict(),
        "duplicados_antes": df.duplicated().sum(),
        "operaciones": []
    }

    # --- PROCESO DE LIMPIEZA Y TRANSFORMACIÓN AVANZADA ---

    # A. Detectar y documentar duplicados
    duplicados_idx = df.duplicated(keep=False)
    if duplicados_idx.sum() > 0:
        df = df[~df.duplicated(keep='first')]
        stats["operaciones"].append(f"Eliminación de duplicados: {duplicados_idx.sum()} registros removidos")

    # B. Limpieza de Texto Básica
    # Normalizar nombres de fabricantes
    df['Company'] = df['Company'].str.strip().str.lower()
    stats["operaciones"].append("Normalización de Company (lowercase, sin espacios)")

    # C. Limpieza de RAM (Convertir de "8GB" a número)
    nulos_ram_antes = df['Ram'].isnull().sum()
    df['Ram'] = df['Ram'].astype(str).str.replace('GB', '', regex=False).str.replace('gb', '', regex=False).str.strip()
    df['Ram'] = pd.to_numeric(df['Ram'], errors='coerce')
    # Imputar nulos en Ram con mediana por empresa
    df['Ram'] = df.groupby('Company')['Ram'].transform(lambda x: x.fillna(x.median()))
    nulos_ram_despues = df['Ram'].isnull().sum()
    stats["operaciones"].append(f"Limpieza de RAM: conversión de string a número, imputación de {nulos_ram_antes} → {nulos_ram_despues} valores nulos")

    # D. Limpieza de Peso (Convertir de "2.1kg" a número en kg)
    nulos_weight_antes = df['Weight'].isnull().sum()
    df['Weight'] = df['Weight'].astype(str).str.replace('kg', '', regex=False).str.replace('Kg', '', regex=False).str.strip()
    df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
    # Imputar nulos en Weight con mediana global
    df['Weight'] = df['Weight'].fillna(df['Weight'].median())
    nulos_weight_despues = df['Weight'].isnull().sum()
    stats["operaciones"].append(f"Limpieza de Weight: conversión de string a número, imputación de {nulos_weight_antes} → {nulos_weight_despues} valores nulos")

    # E. Normalización de Sistema Operativo
    if 'OS' in df.columns:
        df['OS'] = df['OS'].str.strip().str.lower()
        df['OS'] = df['OS'].fillna('Unknown')
        stats["operaciones"].append("Normalización de OS (lowercase, rellenado de valores nulos)")

    # F. Manejo de Outliers (Precios)
    outliers_precio = (df['Price_euros'] < 100).sum()
    df = df[df['Price_euros'] > 100]
    if outliers_precio > 0:
        stats["operaciones"].append(f"Eliminación de outliers en precio: {outliers_precio} registros con precio < 100€")

    # G. Feature Engineering - Crear nuevas características
    # Categoría de precio basada en rango
    df['Price_Category'] = pd.cut(df['Price_euros'], 
                                   bins=[0, 500, 1000, 1500, float('inf')],
                                   labels=['Budget', 'Mid-Range', 'Premium', 'Ultra-Premium'])

    # Crear ratio precio-peso (valor por kg)
    df['Price_per_kg'] = df['Price_euros'] / df['Weight']
    stats["operaciones"].append("Feature Engineering: creación de Price_Category y Price_per_kg")

    # H. Validación de tipos de datos finales
    df['OS'] = df['OS'].fillna('Unknown')
    stats["registros_finales"] = len(df)
    stats["nulos_despues"] = df.isnull().sum().to_dict()

    # --- GENERACIÓN DE EVIDENCIAS ---
    os.makedirs("src/xlsx", exist_ok=True)
    df.to_csv("src/xlsx/cleaned_data.csv", index=False)
    
    # Exportar también a Excel (Excel o CSV según requisito)
    df.to_excel("src/xlsx/cleaned_data.xlsx", index=False, engine='openpyxl')

    # Generar reporte de auditoría dinámico con datos reales
    os.makedirs("src/static/auditoria", exist_ok=True)
    with open("src/static/auditoria/cleaning_report.txt", "w", encoding='utf-8') as f:
        f.write(f"REPORTE TÉCNICO DE PREPROCESAMIENTO Y LIMPIEZA DE DATOS - {datetime.now()}\n")
        f.write("="*80 + "\n\n")
        
        f.write("📊 ESTADÍSTICAS GENERALES:\n")
        f.write("-"*80 + "\n")
        f.write(f"Registros iniciales: {stats['registros_iniciales']}\n")
        f.write(f"Registros finales: {stats['registros_finales']}\n")
        f.write(f"Registros eliminados: {stats['registros_iniciales'] - stats['registros_finales']}\n")
        f.write(f"Duplicados detectados: {stats['duplicados_antes']}\n\n")
        
        f.write("🔧 OPERACIONES REALIZADAS:\n")
        f.write("-"*80 + "\n")
        for i, op in enumerate(stats['operaciones'], 1):
            f.write(f"{i}. {op}\n")
        
        f.write("\n📋 ANÁLISIS DE VALORES NULOS:\n")
        f.write("-"*80 + "\n")
        f.write("ANTES:\n")
        nulos_antes_total = sum([v for v in stats['nulos_antes'].values() if isinstance(v, (int, float))])
        if nulos_antes_total == 0:
            f.write("  ✓ Sin valores nulos detectados\n")
        else:
            for col, count in stats['nulos_antes'].items():
                f.write(f"  {col}: {count} nulos ({count/stats['registros_iniciales']*100:.2f}%)\n")
        
        f.write("\nDESPUÉS:\n")
        nulos_despues_total = sum([v for v in stats['nulos_despues'].values() if isinstance(v, (int, float))])
        if nulos_despues_total == 0:
            f.write("  ✓ Sin valores nulos detectados\n")
        else:
            for col, count in stats['nulos_despues'].items():
                f.write(f"  {col}: {count} nulos ({count/stats['registros_finales']*100:.2f}%)\n")
        
        f.write("\n✅ CALIDAD DE DATOS FINAL:\n")
        f.write("-"*80 + "\n")
        nulos_totales_despues = sum([v for v in stats['nulos_despues'].values() if isinstance(v, (int, float))])
        f.write(f"Completitud: {(1 - nulos_totales_despues/(len(df)*len(df.columns)))*100:.2f}%\n")
        f.write(f"Registros con integridad completa: {len(df[~df.isnull().any(axis=1)])}\n")
        f.write(f"Registros sin integridad total: {len(df[df.isnull().any(axis=1)])}\n")
        
        f.write("\n📁 ARCHIVOS GENERADOS:\n")
        f.write("-"*80 + "\n")
        f.write("- src/xlsx/cleaned_data.csv (CSV con datos limpios)\n")
        f.write("- src/xlsx/cleaned_data.xlsx (Excel con datos limpios)\n")
        f.write("- src/static/auditoria/cleaning_report.txt (Este archivo)\n")

    print("✅ EA2: Preprocesamiento avanzado completado con éxito.")
    print(f"   📊 {stats['registros_finales']} registros limpios generados")
    print(f"   📁 Archivos guardados en src/xlsx/ y src/static/auditoria/")

if __name__ == "__main__":
    ejecutar_limpieza_avanzada()


