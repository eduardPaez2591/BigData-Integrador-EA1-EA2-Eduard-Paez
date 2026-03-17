import pandas as pd
import sqlite3
import os
from datetime import datetime

def realizar_eda():
    """
    Análisis Exploratorio de Datos (EDA) - Fase 1 de EA2
    Identifica problemas de calidad en los datos crudos
    """
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS EXPLORATORIO DE DATOS (EDA)")
    print("="*80)
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect("src/db/ingestion.db")
        df = pd.read_sql_query("SELECT * FROM laptop_raw", conn)
        conn.close()
        
        print(f"\n✅ Datos cargados: {len(df)} registros, {len(df.columns)} columnas\n")
        
        # 1. INFORMACIÓN GENERAL
        print("-" * 80)
        print("1️⃣  INFORMACIÓN GENERAL DEL DATASET")
        print("-" * 80)
        print(f"Total de registros: {len(df)}")
        print(f"Total de columnas: {len(df.columns)}")
        print(f"\nColumnas: {', '.join(df.columns.tolist())}\n")
        
        # 2. ANÁLISIS DE VALORES NULOS
        print("-" * 80)
        print("2️⃣  ANÁLISIS DE VALORES NULOS")
        print("-" * 80)
        null_analysis = df.isnull().sum()
        null_percentage = (df.isnull().sum() / len(df) * 100).round(2)
        
        null_data = pd.DataFrame({
            'Columna': null_analysis.index,
            'Nulos': null_analysis.values,
            'Porcentaje': null_percentage.values
        })
        null_data = null_data[null_data['Nulos'] > 0].sort_values('Nulos', ascending=False)
        
        if len(null_data) > 0:
            print(f"\nEncontrados valores nulos en {len(null_data)} columnas:")
            print(null_data.to_string(index=False))
        else:
            print("✅ No hay valores nulos en el dataset")
        print()
        
        # 3. ANÁLISIS DE DUPLICADOS
        print("-" * 80)
        print("3️⃣  ANÁLISIS DE DUPLICADOS")
        print("-" * 80)
        duplicados_totales = df.duplicated().sum()
        duplicados_por_key = df.duplicated(subset=['Company', 'Product'], keep=False).sum()
        
        print(f"Filas duplicadas (completamente): {duplicados_totales}")
        print(f"Filas duplicadas (por Company + Product): {duplicados_por_key}")
        
        if duplicados_totales == 0:
            print("✅ No hay duplicados totales en el dataset\n")
        else:
            print(f"⚠️  Detectados {duplicados_totales} registros duplicados\n")
        
        # 4. ANÁLISIS DE TIPOS DE DATOS
        print("-" * 80)
        print("4️⃣  ANÁLISIS DE TIPOS DE DATOS")
        print("-" * 80)
        print(df.dtypes.to_string())
        print()
        
        # 5. ESTADÍSTICAS DESCRIPTIVAS (NUMÉRICAS)
        print("-" * 80)
        print("5️⃣  ESTADÍSTICAS DESCRIPTIVAS (COLUMNAS NUMÉRICAS)")
        print("-" * 80)
        print(df.describe().to_string())
        print()
        
        # 6. ANÁLISIS ESPECÍFICO DE COLUMNAS CRÍTICAS
        print("-" * 80)
        print("6️⃣  ANÁLISIS ESPECÍFICO DE COLUMNAS CRÍTICAS")
        print("-" * 80)
        
        # Precios
        print("\n📌 PRECIOS (Price_euros):")
        print(f"  Mínimo: €{df['Price_euros'].min():.2f}")
        print(f"  Máximo: €{df['Price_euros'].max():.2f}")
        print(f"  Media: €{df['Price_euros'].mean():.2f}")
        print(f"  Mediana: €{df['Price_euros'].median():.2f}")
        precios_bajos = (df['Price_euros'] < 100).sum()
        if precios_bajos > 0:
            print(f"  ⚠️  Precios < 100€: {precios_bajos} registros (OUTLIERS)")
        
        # RAM
        if 'Ram' in df.columns:
            print("\n📌 RAM:")
            print(f"  Nulos: {df['Ram'].isnull().sum()}")
            print(f"  Valores únicos: {df['Ram'].nunique()}")
            print(f"  Ejemplos: {df['Ram'].dropna().head(3).tolist()}")
        
        # Weight
        if 'Weight' in df.columns:
            print("\n📌 WEIGHT:")
            print(f"  Nulos: {df['Weight'].isnull().sum()}")
            print(f"  Valores únicos: {df['Weight'].nunique()}")
            print(f"  Ejemplos: {df['Weight'].dropna().head(3).tolist()}")
        
        # Company
        if 'Company' in df.columns:
            print("\n📌 COMPANY (Marcas):")
            print(f"  Total de marcas: {df['Company'].nunique()}")
            print(f"  Top 5 marcas más frecuentes:")
            print(df['Company'].value_counts().head(5).to_string())
        
        # 7. DETECCIÓN DE OUTLIERS (IQR)
        print("\n" + "-" * 80)
        print("7️⃣  DETECCIÓN DE OUTLIERS (Método IQR)")
        print("-" * 80)
        
        def detectar_outliers(columna_nombre):
            if pd.api.types.is_numeric_dtype(df[columna_nombre]):
                Q1 = df[columna_nombre].quantile(0.25)
                Q3 = df[columna_nombre].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[columna_nombre] < Q1 - 1.5*IQR) | (df[columna_nombre] > Q3 + 1.5*IQR)]
                return len(outliers)
        
        columnas_numericas = df.select_dtypes(include=['number']).columns
        outliers_dict = {}
        for col in columnas_numericas:
            outliers_count = detectar_outliers(col)
            if outliers_count > 0:
                outliers_dict[col] = outliers_count
        
        if outliers_dict:
            print("\nOutliers detectados:")
            for col, count in sorted(outliers_dict.items(), key=lambda x: x[1], reverse=True):
                print(f"  {col}: {count} outliers")
        else:
            print("\n✅ No se detectaron outliers significativos")
        
        # 8. RESUMEN Y RECOMENDACIONES
        print("\n" + "="*80)
        print("📋 RESUMEN Y RECOMENDACIONES")
        print("="*80)
        
        recomendaciones = []
        
        if df.isnull().sum().sum() > 0:
            recomendaciones.append("• Manejar valores nulos con imputación o eliminación")
        
        if precios_bajos > 0:
            recomendaciones.append(f"• Revisar/eliminar {precios_bajos} registros con precios < 100€")
        
        if duplicados_totales > 0:
            recomendaciones.append(f"• Eliminar/revisar {duplicados_totales} registros duplicados")
        
        if outliers_dict:
            recomendaciones.append(f"• Validar {len(outliers_dict)} columnas con outliers")
        
        if recomendaciones:
            print("\n🔧 ACCIONES RECOMENDADAS:")
            for rec in recomendaciones:
                print(rec)
        else:
            print("\n✅ Dataset en buena calidad - pocas acciones necesarias")
        
        # Guardar reporte EDA
        os.makedirs("src/static/auditoria", exist_ok=True)
        with open("src/static/auditoria/eda_report.txt", "w", encoding='utf-8') as f:
            f.write(f"REPORTE DE ANÁLISIS EXPLORATORIO - {datetime.now()}\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total de registros: {len(df)}\n")
            f.write(f"Total de columnas: {len(df.columns)}\n")
            f.write(f"Valores nulos encontrados: {df.isnull().sum().sum()}\n")
            f.write(f"Registros duplicados: {duplicados_totales}\n")
            f.write(f"Outliers detectados: {sum(outliers_dict.values())}\n\n")
            f.write("Columnas con valores nulos:\n")
            if len(null_data) > 0:
                f.write(null_data.to_string())
            else:
                f.write("Ninguna")
            f.write("\n\nRecomendaciones:\n")
            for rec in recomendaciones:
                f.write(rec + "\n")
        
        print("\n✅ Reporte EDA guardado en: src/static/auditoria/eda_report.txt\n")
        
    except FileNotFoundError:
        print("❌ Error: La base de datos no existe.")
        print("Ejecuta primero: python ingestion.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    realizar_eda()
