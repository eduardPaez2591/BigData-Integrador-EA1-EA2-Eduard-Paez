# EA2: Preprocesamiento y Limpieza de Datos - Pipeline de Big Data

Implementación de la **Actividad Evaluable 2 (EA2)** del Proyecto Integrador de Big Data. Este proyecto realiza el preprocesamiento y limpieza de un dataset de precios de laptops utilizando Pandas en un entorno que simula procesamiento en la nube.

## 📋 Descripción

Este proyecto implementa un **pipeline automatizado de data cleaning** que:

1. **Ingiere datos** desde archivos CSV a una base de datos SQLite (simulando almacenamiento cloud)
2. **Realiza análisis exploratorio (EDA)** para identificar problemas de calidad
3. **Limpia y transforma** los datos aplicando técnicas de preprocesamiento
4. **Genera evidencias** documentando todas las operaciones realizadas
5. **Automatiza el flujo** mediante GitHub Actions para ejecución continua

## 🏗️ Estructura del Proyecto

```
.
├── .github/
│   └── workflows/
│       └── bigdata.yml                 # Workflow automatizado en GitHub Actions
├── data_raw/
│   └── laptop_prices.csv              # Dataset original (Kaggle)
├── src/
│   ├── db/
│   │   └── ingestion.db               # Base de datos SQLite
│   ├── static/
│   │   └── auditoria/
│   │       ├── eda_report.txt         # Reporte de análisis exploratorio
│   │       └── cleaning_report.txt    # Reporte de limpieza
│   └── xlsx/
│       ├── cleaned_data.csv           # Datos limpios (CSV)
│       └── cleaned_data.xlsx          # Datos limpios (Excel)
├── ingestion.py                       # Script de ingestión de datos
├── exploratory_analysis.py            # Script de análisis exploratorio
├── cleaning.py                        # Script de limpieza y transformación
├── requirements.txt                   # Dependencias de Python
├── setup.py                           # Configuración del paquete
└── README.md                          # Este archivo
```

## 📊 Dataset

**Origen:** Laptop Prices Dataset (Kaggle)

**Características:**

- **Registros:** 1,275 laptops
- **Columnas:** 23 atributos (marca, tipo, RAM, peso, precio, etc.)
- **Formato:** CSV

## 🔧 Instalación

### Requisitos Previos

- Python >= 3.10
- Git

### Pasos de Instalación

1. **Clonar el repositorio:**

```bash
git clone https://github.com/tu-usuario/eduard_paez_EA2_trans.git
cd eduard_paez_EA2_trans
```

2. **Crear entorno virtual:**

```bash
python -m venv .venv

# En Windows:
.venv\Scripts\activate

# En macOS/Linux:
source .venv/bin/activate
```

3. **Instalar dependencias:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ▶️ Ejecución

### Opción 1: Ejecución Manual (Recomendado para desarrollo)

Ejecutar los scripts en orden:

````bash
# Paso 1: Ingestión de datos (CSV → SQLite)
python ingestion.py

# Paso 2: Análisis Exploratorio (EDA)
python exploratory_analysis.py

# Paso 3: Limpieza y transformación
python cleaning.py

### Opción 2: Ejecución Automatizada (GitHub Actions)

El workflow se ejecuta automáticamente cuando hace push a la rama `main`:

```bash
git add .
git commit -m "feat: nueva versión del pipeline"
git push origin main
````

Verificar en: `Settings > Actions > Workflows` → `Pipeline Laptop Data EA1 & EA2`

## 📈 Proceso de Limpieza

### Paso 1: Ingestion (ingestion.py)

- Lee el CSV `data_raw/laptop_prices.csv`
- Carga 1,275 registros en SQLite
- Crea tabla `laptop_raw`

**Salida:**

```
✅ EA1: 1275 registros de Kaggle cargados en SQLite.
```

### Paso 2: Análisis Exploratorio (exploratory_analysis.py)

Identifica problemas de calidad:

- ✅ **Valores nulos por columna** (cantidad y %)
- ✅ **Registros duplicados**
- ✅ **Tipos de datos**
- ✅ **Estadísticas descriptivas**
- ✅ **Outliers** (método IQR)
- ✅ **Análisis específico** de columnas críticas

**Salida:** `src/static/auditoria/eda_report.txt`

Ejemplo de análisis:

```
ANÁLISIS EXPLORATORIO DE DATOS
Total de registros: 1275
Valores nulos encontrados: 5 (RAM), 1 (Weight)
Registros duplicados: 0
Outliers detectados en: Price_euros (3), Weight (2)
```

### Paso 3: Limpieza y Transformación (cleaning.py)

Operaciones realizadas:

1. **Eliminación de duplicados**
   - Detecta y elimina registros duplicados

2. **Normalización de texto**
   - Company: convertir a minúsculas, eliminar espacios

3. **Conversión de tipos**
   - RAM: "8GB" → 8 (número)
   - Weight: "2.1kg" → 2.1 (número)

4. **Imputación de valores nulos**
   - RAM: mediana por marca (Company)
   - Weight: mediana global
   - OS: "Unknown" si faltan

5. **Eliminación de outliers**
   - Precios < 100€ (errores de datos)

6. **Feature Engineering**
   - `Price_Category`: Categorización de precios (Budget, Mid-Range, Premium, Ultra-Premium)
   - `Price_per_kg`: Ratio precio por kg

**Salidas:**

- `src/xlsx/cleaned_data.csv` - Datos limpios en CSV
- `src/xlsx/cleaned_data.xlsx` - Datos limpios en Excel
- `src/static/auditoria/cleaning_report.txt` - Reporte detallado

## 📋 Reporte de Auditoría

El archivo `cleaning_report.txt` documenta:

```
REPORTE TÉCNICO DE PREPROCESAMIENTO Y LIMPIEZA DE DATOS
================================================================================

📊 ESTADÍSTICAS GENERALES:
Registros iniciales: 1275
Registros finales: 1275
Registros eliminados: 0
Duplicados detectados: 0

🔧 OPERACIONES REALIZADAS:
1. Eliminación de duplicados: 0 registros removidos
2. Normalización de Company (lowercase, sin espacios)
3. Limpieza de RAM: conversión de string a número, imputación de 5 → 0 valores nulos
4. Limpieza de Weight: conversión de string a número, imputación de 1 → 0 valores nulos
5. Normalización de OS (lowercase, rellenado de valores nulos)
6. Eliminación de outliers en precio: 0 registros con precio < 100€
7. Feature Engineering: creación de Price_Category y Price_per_kg

📋 ANÁLISIS DE VALORES NULOS:
ANTES:
  Ram: 5 nulos (0.39%)
  Weight: 1 nulos (0.08%)

DESPUÉS:
  (Sin valores nulos)

✅ CALIDAD DE DATOS FINAL:
Completitud: 100.00%
```

## 🔄 GitHub Actions Workflow

El archivo `.github/workflows/bigdata.yml` automatiza:

```yaml
Pipeline:
├── 1. Checkout del repositorio
├── 2. Configurar Python 3.10
├── 3. Instalar dependencias (requirements.txt)
├── 4. Ejecutar ingestion.py
├── 5. Ejecutar exploratory_analysis.py
├── 6. Ejecutar cleaning.py
├── 7. Guardar artefactos
│   ├── cleaned-data-csv
│   ├── cleaned-data-excel
│   ├── eda-report
│   └── audit-report
└── 8. Mostrar reporte en logs
```

**Acceso a artefactos:** GitHub → Actions → Última ejecución → Artifacts

## 📊 Ejemplo de Datos Limpios

**Entrada (raw):**

```
Company,Product,Ram,Weight,Price_euros
Apple,MacBook Pro,8,1.37,1339.69
Hp,250 G6,,1.86,575.0
Apple,Macbook Air,null,1.34,898.94
```

**Salida (cleaned):**

```
Company,Product,Ram,Weight,Price_euros,Price_Category,Price_per_kg
apple,MacBook Pro,8,1.37,1339.69,Premium,977.88
hp,250 G6,8,1.86,575.0,Mid-Range,309.14
apple,Macbook Air,8,1.34,898.94,Mid-Range,670.85
```

## 🧪 Validación

Verificar que todo funciona correctamente:

```bash
# 1. Comprobar que los archivos se generan
ls -la src/xlsx/
ls -la src/static/auditoria/

# 2. Verificar integridad de datos
tail -5 src/xlsx/cleaned_data.csv

# 3. Leer reporte de auditoría
cat src/static/auditoria/cleaning_report.txt
```

## 📚 Dependencias

```
pandas>=2.0.3      # Manipulación de datos
numpy>=1.24.3      # Computación numérica
openpyxl>=3.1.2    # Exportar a Excel
```

Instalar todas con:

```bash
pip install -r requirements.txt
```

## 🎯 Requisitos Cumplidos (EA2)

- ✅ Carga de datos desde base de datos (simulando cloud)
- ✅ Análisis exploratorio de datos (EDA)
- ✅ Eliminación de duplicados
- ✅ Manejo de valores nulos
- ✅ Corrección de tipos de datos
- ✅ Transformaciones adicionales (Feature Engineering)
- ✅ Archivo de datos limpios (CSV + Excel)
- ✅ Archivo de auditoría con documentación detallada
- ✅ Automatización mediante GitHub Actions
- ✅ README documentado con trazabilidad completa

## 🚀 Mejoras Futuras

- [ ] Agregar más técnicas de imputación (KNN, MICE)
- [ ] Detectar y manejar valores atípicos con métodos avanzados
- [ ] Crear visualizaciones (gráficos de distribuciones, correlaciones)
- [ ] Implementar pruebas unitarias
- [ ] Generar reportes en HTML interactivos
- [ ] Integrar con herramientas de Big Data (PySpark)

## 📞 Contacto

**Autor:** Eduard Paez  
**Email:** eduard2591.eapb@gmail.com

## 📄 Licencia

Este proyecto es parte del Proyecto Integrador de Ingeniería de Software y Datos.

## 🔗 Referencias

- [Dataset Original (Kaggle)](https://www.kaggle.com/datasets/ionaskel/laptop-prices)
- [Pandas Documentation](https://pandas.pydata.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

**Última actualización:** Marzo 2026  
**Estado:** ✅ Completo y Funcional
