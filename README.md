# Prueba Técnica Protección: Científico de Datos

![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

**Autora:** Beatriz Valentina Gómez Valencia

Plataforma integral de análisis de datos de e-commerce que responde 7 preguntas estratégicas clave usando SQL, Python, machine learning y análisis avanzado de datos.

---

## 🎯 Preguntas Estratégicas Respondidas

| # | Pregunta | Análisis |
|---|----------|---------|
| **1** | ¿Cuáles son los 5 productos más vendidos por volumen e ingresos? | Top Productos y Categorías |
| **2** | ¿Cuál es el mayor dolor del cliente y qué productos están relacionados? | Puntos de Dolor del Cliente |
| **3** | ¿Cómo segmentar clientes entre fieles, esporádicos y en riesgo? | Segmentación RFM con KMeans |
| **4** | ¿Cómo arquitecturar un modelo de recomendación en tiempo real? | Arquitectura del Modelo |
| **5** | ¿Dónde ubicar el centro comercial insignia con mayores ventas? | Análisis de Ubicación Óptima |
| **6** | ¿Cómo crear una base de conocimientos de productos con precios reales? | Base de Conocimiento (JSON) |
| **7** | ¿Cómo personalizar el tono de un agente IA por segmento de cliente? | System Prompts Dinámicos |

---

## 📊 Análisis Disponibles

| Código | Nombre | Método |
|--------|--------|--------|
| **01** | Top Productos y Categorías | SQL + Visualización |
| **02** | Puntos de Dolor del Cliente | SQL + Análisis de ratings |
| **03** | Segmentación RFM de Clientes | KMeans clustering + Silhouette Score |
| **04** | Arquitectura de Recomendaciones | Diseño de sistemas + SQL |
| **05** | Ubicación Óptima de Tienda | Geolocalización + Mapas interactivos |
| **06** | Base de Conocimiento de Productos | Extracción de datos + JSON |
| **07** | System Prompts para IA | Templates personalizados por segmento |

---

## 🗂️ Estructura del Proyecto

```
Prueba_Tecnica/
├── technical_test/              # Paquete principal
│   ├── utils/
│   │   ├── database.py         # Motor SQL para DataFrames
│   │   ├── export_results.py   # Exportar CSV, JSON, gráficos
│   │   └── __init__.py
│   ├── answers/                 # Análisis (01, 02, 03, 04, 05, 06, 07)
│   ├── __main__.py             # Orquestador de análisis
│   └── __init__.py
├── data/                        # 9 datasets CSV de OLIST
├── results/                     # Resultados (answer_01/ a answer_07/)
├── setup.py                     # Dependencias e instalación
├── README.md                    # Documentación
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Instalación (macOS / Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 1. Instalación (Windows)
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### 2. Ejecutar Análisis
```bash
# Todos los análisis
python -m technical_test

# Análisis específicos
python -m technical_test --select 01,03,05

# Modo interactivo
python -m technical_test --interactive
```

### 3. Resultados
Cada análisis genera archivos en `results/answer_XX/`:
- **CSV**: Datos procesados
- **JSON**: Bases de conocimiento
- **HTML**: Mapas interactivos
- **PNG**: Visualizaciones

---

## 🔧 Tecnologías Utilizadas

- **Python 3.13** - Lenguaje principal
- **pandas / pandasql** - Procesamiento de datos y SQL
- **scikit-learn** - Machine learning (KMeans, Silhouette Score)
- **matplotlib** - Visualizaciones estadísticas
- **folium** - Mapas geográficos interactivos
- **geopandas** - Análisis geoespacial

---

## 📈 Datasets

9 tablas CSV del sistema e-commerce:
- Clientes, pedidos, items, pagos, reseñas, productos, categorías, vendedores, geolocalización

**Total:** 93,358 clientes únicos | 99,441 pedidos | 112,650 items

---

## 👤 Autora

**Beatriz Valentina Gómez Valencia**  
Científica de Datos - Prueba Técnica Protección

---

**Última actualización:** 29 de marzo de 2026