import pandas as pd
from datetime import datetime

from ..utils.database import Database
from ..utils.export_results import save_to_csv, save_to_json

db = Database()

print("\nIniciando análisis de base de conocimientos de productos...")

# =============================================================================
# PASO 1: EXTRAE ESTADÍSTICAS DE LAS TOP 3 CATEGORÍAS
# =============================================================================

print("\nExtrayendo estadísticas de precios por categoría...")

query_stats = """
    SELECT 
        p.product_category_name as categoria_portugues,
        pt.product_category_name_english as categoria_ingles,
        COUNT(oi.order_item_id) as items_vendidos,
        ROUND(AVG(oi.price), 2) as precio_promedio,
        ROUND(MIN(oi.price), 2) as precio_minimo,
        ROUND(MAX(oi.price), 2) as precio_maximo,
        ROUND(SUM(oi.price), 2) as ingresos_totales
    FROM products_dataset p
    JOIN order_items_dataset oi ON p.product_id = oi.product_id
    LEFT JOIN product_category_name_translation pt ON p.product_category_name = pt.product_category_name
    GROUP BY p.product_category_name, pt.product_category_name_english
    ORDER BY items_vendidos DESC
    LIMIT 3
"""

price_stats = db.query(query_stats)
save_to_csv(price_stats, file="price_stats.csv", folder="answer_06")

# =============================================================================
# PASO 2: DEFINE CONTENIDO CURADO DE PRODUCTOS
# =============================================================================

CATEGORY_CONTENT = {
    'cama_mesa_banho': {
        'name_display': 'Cama, Baño y Mesa',
        'description': (
            'Renueva cada rincón de tu hogar con nuestra colección premium de cama, baño y mesa. '
            'Desde sábanas de alto hilo que transforman el descanso hasta toallas ultra absorbentes '
            'y manteles que elevan cada comida a una experiencia especial. '
            'Diseños modernos y clásicos que combinan estética y funcionalidad, con textiles suaves al tacto y resistentes al uso diario. '
            'Calidad que se siente desde el primer uso, diseñada para durar y deleitar.'
        ),
        'key_features': [
            'Materiales certificados sin sustancias nocivas',
            'Alta durabilidad tras múltiples lavados',
            'Amplia variedad de tamaños y colores',
            'Textiles suaves, hipoalergénicos y transpirables',
            'Envío protegido y devolución sin complicaciones',
        ],
        'use_cases': [
            'Renovación del hogar',
            'Regalo ideal',
            'Hostelería y Airbnb',
            'Mejora de la experiencia de descanso',
            'Decoración de espacios interiores'
        ],
        'cross_sell_opportunities': [
            'Decoración del hogar',
            'Iluminación',
            'Muebles auxiliares'
        ],
        'seasonality': [
            'Alta demanda en fin de año',
            'Picos en temporadas de descuentos',
            'Incremento en cambios de estación'
        ],
    },
    'beleza_saude': {
        'name_display': 'Salud y Belleza',
        'description': (
            'Descubre nuestra selección curada de los mejores productos de salud y belleza diseñados para potenciar tu bienestar integral. '
            'Desde rutinas de skincare con activos de última generación hasta suplementos y herramientas de cuidado personal. '
            'Ofrecemos soluciones para diferentes tipos de piel, necesidades y estilos de vida, combinando innovación, seguridad y resultados visibles. '
            'Tu bienestar merece lo mejor: marcas reconocidas, formulaciones seguras, experiencias que elevan tu rutina diaria y precios que sorprenden gratamente.'
        ),
        'key_features': [
            'Fórmulas dermatológicamente testeadas',
            'Opciones sin parabenos ni fragancias agresivas',
            'Certificaciones cruelty-free y sostenibles',
            'Amplia gama para diferentes tipos de piel y necesidades',
            'Empaque seguro y protegido para envío',
        ],
        'use_cases': [
            'Cuidado personal diario',
            'Regalos premium',
            'Bienestar físico y emocional',
            'Rutinas de skincare especializadas',
            'Autocuidado y spa en casa'
        ],
        'cross_sell_opportunities': [
            'Accesorios de belleza',
            'Productos de cuidado capilar',
            'Fitness y bienestar'
        ],
        'seasonality': [
            'Alta demanda en fechas especiales',
            'Picos en campañas de descuentos',
            'Incremento en tendencias virales y lanzamientos'
        ],
    },
    'esporte_lazer': {
        'name_display': 'Deportes y Ocio',
        'description': (
            'Lleva tu rendimiento al siguiente nivel con equipamiento deportivo y de ocio de alta calidad, diseñado para acompañarte en cada desafío. '
            'Nuestra línea cubre desde el entrenamiento más intenso hasta las aventuras al aire libre, '
            'con productos duraderos, funcionales y adaptados a diferentes niveles de experiencia. '
            'Ya sea que busques mejorar tu condición física, explorar nuevas aventuras o disfrutar de tu tiempo libre, '
            'aquí encontrarás aliados confiables para cada objetivo. Invierte en tu salud hoy: tu versión futura te lo agradecerá.'
        ),
        'key_features': [
            'Material de alta resistencia para uso intensivo',
            'Diseño ergonómico, liviano y funcional',
            'Tallas completas para todos los perfiles',
            'Amplia variedad de disciplinas y categorías',
            'Opciones para principiantes y atletas avanzados',
            'Garantía extendida en productos seleccionados',
        ],
        'use_cases': [
            'Entrenamiento diario',
            'Actividades outdoor',
            'Recuperación y rehabilitación',
            'Ocio y entretenimiento',
            'Preparación para cometencias'
        ],
        'cross_sell_opportunities': [
            'Ropa deportiva',
            'Tecnología wearable',
            'Nutrición deportiva'
        ],
        'seasonality': [
            'Alta demanda en inicio de año',
            'Picos antes de vacaciones',
            'Incremento en eventos deportivos'
        ],
    },
}

# =============================================================================
# PASO 3: CONSTRUCCIÓN DE LA BASE DE CONOCIMIENTOS
# =============================================================================

print("\nConstruyendo base de conocimientos...")

knowledge_base = {}
stats_dict = price_stats.set_index('categoria_portugues').to_dict('index')

for cat_key, content in CATEGORY_CONTENT.items():
    if cat_key in stats_dict:
        stats = stats_dict[cat_key]
        
        knowledge_base[cat_key] = {
            'category_key': cat_key,
            'category_display_name': content['name_display'],
            'pricing': {
                'avg_BRL': float(stats['precio_promedio']),
                'median_BRL': float(stats['precio_promedio']),  # Usamos promedio como proxy
                'min_BRL': float(stats['precio_minimo']),
                'max_BRL': float(stats['precio_maximo']),
                'currency': 'BRL',
            },
            'units_sold': int(stats['items_vendidos']),
            'total_revenue': float(stats['ingresos_totales']),
            'description': content['description'],
            'key_features': content['key_features'],
            'use_cases': content['use_cases'],
            'cross_sell_opportunities': content['cross_sell_opportunities'],
            'seasonality': content['seasonality'],
            'data_source': 'olist_datasets',
            'last_updated': str(datetime.today().date()),
        }

# Guardar la base de conocimientos en JSON
save_to_json(knowledge_base, file="knowledge_base.json", folder="answer_06")

# =============================================================================
# PASO 4: EXPORTACIÓN Y VISUALIZACIÓN
# =============================================================================

print("\nGenerando visualizaciones...")

# Crear un resumen de texto
print("\n" + "=" * 80)
print("BASE DE CONOCIMIENTOS - PRODUCTOS TOP 3".center(80))
print("=" * 80)

for cat_key, data in knowledge_base.items():
    print(f"\n{'=' * 80}")
    print(f"  {data['category_display_name'].upper()}")
    print(f"{'=' * 80}")
    print(f"  Precio promedio:   BRL ${data['pricing']['avg_BRL']:,.2f}")
    print(f"  Rango:             BRL ${data['pricing']['min_BRL']:,.2f} – ${data['pricing']['max_BRL']:,.2f}")
    print(f"  Unidades vendidas: {data['units_sold']:,}")
    print(f"  Ingresos totales:  BRL ${data['total_revenue']:,.2f}")
    print(f"\n  {data['description']}")
    print(f"\n  Características clave:")
    for feature in data['key_features']:
        print(f"    • {feature}")
    print(f"\n  Casos de uso:")
    for use_case in data['use_cases']:
        print(f"    • {use_case}")
    print(f"\n  Oportunidades de venta cruzada:")
    for cross_sell in data['cross_sell_opportunities']:
        print(f"    • {cross_sell}")
    print(f"\n  Estacionalidad:")
    for season in data['seasonality']:
        print(f"    • {season}")

print("\n" + "=" * 80)

print("\n✓ Análisis de base de conocimientos completado.")
print("✓ Resultados guardados en: results/answer_06/")
