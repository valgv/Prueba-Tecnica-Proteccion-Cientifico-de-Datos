import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from ..utils.database import Database
from ..utils.export_results import save_to_csv, save_plot

db = Database()

# Consulta 1: Top ciudades por ingresos totales
query_ciudades_ingresos = db.query("""
    SELECT 
        c.customer_city,
        c.customer_state,
        COUNT(DISTINCT c.customer_id) as unique_customers,
        COUNT(DISTINCT o.order_id) as total_orders,
        COUNT(oi.order_item_id) as total_items,
        ROUND(SUM(oi.price), 2) as total_revenue,
        ROUND(AVG(oi.price), 2) as avg_price_per_item
    FROM customers_dataset c
    INNER JOIN orders_dataset o ON c.customer_id = o.customer_id
    INNER JOIN order_items_dataset oi ON o.order_id = oi.order_id
    GROUP BY c.customer_city, c.customer_state
    ORDER BY total_revenue DESC
    LIMIT 15
""")

save_to_csv(query_ciudades_ingresos, file="top_ciudades_ingresos.csv", folder="answer_05")

# Gráfico 1: Top ciudades por ingresos
fig1, ax1 = plt.subplots(figsize=(14, 8))
top_ciudades = query_ciudades_ingresos.head(10)
ax1.barh(top_ciudades['customer_city'] + ' (' + top_ciudades['customer_state'] + ')', 
         top_ciudades['total_revenue'], color='#1f77b4', edgecolor='black')
ax1.set_xlabel('Ingresos Totales ($)', fontweight='bold')
ax1.set_title('Top 10 Ciudades por Ingresos Totales', fontweight='bold', fontsize=14)
for i, v in enumerate(top_ciudades['total_revenue']):
    ax1.text(v + 5000, i, f'${v:,.0f}', va='center', fontweight='bold', fontsize=9)
plt.tight_layout()

save_plot(fig1, file="top_ciudades_ingresos.png", folder="answer_05", dpi=300)

# Consulta 2: Clientes por ciudad (densidad)
query_densidad_clientes = db.query("""
    SELECT 
        c.customer_city,
        c.customer_state,
        COUNT(DISTINCT c.customer_id) as unique_customers,
        ROUND(AVG(oi.price), 2) as ticket_promedio,
        COUNT(DISTINCT o.order_id) as total_orders
    FROM customers_dataset c
    INNER JOIN orders_dataset o ON c.customer_id = o.customer_id
    INNER JOIN order_items_dataset oi ON o.order_id = oi.order_id
    GROUP BY c.customer_city, c.customer_state
    ORDER BY unique_customers DESC
    LIMIT 15
""")

save_to_csv(query_densidad_clientes, file="densidad_clientes_por_ciudad.csv", folder="answer_05")

# Gráfico 2: Densidad de clientes (scatter plot: clientes vs ingresos)
fig2, ax2 = plt.subplots(figsize=(12, 8))
merged_data = query_ciudades_ingresos.merge(
    query_densidad_clientes[['customer_city', 'unique_customers']], 
    on='customer_city',
    suffixes=('_ingresos', '_densidad')
)
scatter = ax2.scatter(merged_data['unique_customers_ingresos'], 
                      merged_data['total_revenue'],
                      s=300, alpha=0.6, c=range(len(merged_data)), cmap='viridis', edgecolors='black', linewidth=1.5)
ax2.set_xlabel('Cantidad de Clientes Únicos', fontweight='bold', fontsize=12)
ax2.set_ylabel('Ingresos Totales ($)', fontweight='bold', fontsize=12)
ax2.set_title('Matriz: Densidad de Clientes vs Ingresos', fontweight='bold', fontsize=14)
ax2.grid(True, alpha=0.3)
for idx, row in merged_data.head(10).iterrows():
    ax2.annotate(f"{row['customer_city']}", 
                (row['unique_customers_ingresos'], row['total_revenue']),
                fontsize=8, alpha=0.7)
plt.tight_layout()
save_plot(fig2, file="matriz_clientes_ingresos.png", folder="answer_05", dpi=300)

# Consulta 3: Categorías premium por ciudad top
top_ciudades_lista = query_ciudades_ingresos.head(3)['customer_city'].tolist()
ciudades_str = "'" + "','".join(top_ciudades_lista) + "'"

query_categorias_por_ciudad = db.query(f"""
    SELECT 
        c.customer_city,
        pt.product_category_name_english as categoria,
        COUNT(oi.order_item_id) as items_sold,
        ROUND(SUM(oi.price), 2) as category_revenue,
        ROUND(AVG(r.review_score), 2) as avg_rating
    FROM customers_dataset c
    INNER JOIN orders_dataset o ON c.customer_id = o.customer_id
    INNER JOIN order_items_dataset oi ON o.order_id = oi.order_id
    INNER JOIN products_dataset p ON oi.product_id = p.product_id
    INNER JOIN product_category_name_translation pt ON p.product_category_name = pt.product_category_name
    LEFT JOIN order_reviews_dataset r ON o.order_id = r.order_id
    WHERE c.customer_city IN ({ciudades_str})
    GROUP BY c.customer_city, pt.product_category_name_english
    ORDER BY c.customer_city, category_revenue DESC
""")

save_to_csv(query_categorias_por_ciudad, file="categorias_premium_por_ciudad.csv", folder="answer_05")

# Gráfico 3: Categorías top en ciudades principales
fig3, axes = plt.subplots(1, 3, figsize=(18, 6))
fig3.suptitle('Top Categorías por Ciudad Principal', fontweight='bold', fontsize=14)

for idx, ciudad in enumerate(top_ciudades_lista):
    if idx < 3:
        data_ciudad = query_categorias_por_ciudad[query_categorias_por_ciudad['customer_city'] == ciudad].head(5)
        axes[idx].barh(data_ciudad['categoria'], data_ciudad['category_revenue'], color='#2ca02c', edgecolor='black')
        axes[idx].set_xlabel('Ingresos ($)', fontweight='bold')
        axes[idx].set_title(f'{ciudad}', fontweight='bold', fontsize=12)
        for i, v in enumerate(data_ciudad['category_revenue']):
            axes[idx].text(v + 5000, i, f'${v:,.0f}', va='center', fontsize=9, fontweight='bold')
        axes[idx].grid(True, alpha=0.3, axis='x')

plt.tight_layout()
save_plot(fig3, file="categorias_por_ciudad.png", folder="answer_05", dpi=300)

# =============================================================================
# MAPA INTERACTIVO DE BRASIL CON UBICACIÓN ÓPTIMA EN SÃO PAULO
# =============================================================================

# Consulta: Top ciudades por ingresos totales
query_ciudades_ingresos_mapa = db.query("""
    SELECT 
        c.customer_city,
        c.customer_state,
        COUNT(DISTINCT c.customer_id) as unique_customers,
        ROUND(SUM(oi.price), 2) as total_revenue,
        COUNT(DISTINCT o.order_id) as total_orders
    FROM customers_dataset c
    INNER JOIN orders_dataset o ON c.customer_id = o.customer_id
    INNER JOIN order_items_dataset oi ON o.order_id = oi.order_id
    GROUP BY c.customer_city, c.customer_state
    ORDER BY total_revenue DESC
""")

# Cargar datos de geolocalización
geolocation = pd.read_csv('data/geolocation_dataset.csv')

# Agrupar geolocalización por ciudad para obtener coordenadas representativas
geo_cities = geolocation.groupby(['geolocation_city', 'geolocation_state']).agg({
    'geolocation_lat': 'mean',
    'geolocation_lng': 'mean'
}).reset_index()

geo_cities.rename(columns={
    'geolocation_city': 'customer_city',
    'geolocation_state': 'customer_state',
    'geolocation_lat': 'latitude',
    'geolocation_lng': 'longitude'
}, inplace=True)

# Merge de datos de ingresos con coordenadas
map_data = query_ciudades_ingresos_mapa.merge(
    geo_cities,
    on=['customer_city', 'customer_state'],
    how='left'
)

# Remover filas sin coordenadas
map_data = map_data.dropna(subset=['latitude', 'longitude'])

print("CREANDO MAPA INTERACTIVO DE BRASIL CON UBICACIÓN ÓPTIMA EN SÃO PAULO...")
print(f"Total ciudades con datos: {len(map_data)}")

# =============================================================================
# CALCULAR UBICACIÓN ÓPTIMA PARA SÃO PAULO
# =============================================================================

print("\nCalculando ubicación óptima para tienda en São Paulo...")

# Obtener datos de clientes en São Paulo
customers_sp = db.query("""
    SELECT 
        c.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        COALESCE(geo.geolocation_lat, -23.5509) as geolocation_lat,
        COALESCE(geo.geolocation_lng, -46.6333) as geolocation_lng,
        COUNT(DISTINCT o.order_id) as num_compras,
        ROUND(SUM(oi.price), 2) as monto_total
    FROM customers_dataset c
    INNER JOIN orders_dataset o ON c.customer_id = o.customer_id
    INNER JOIN order_items_dataset oi ON o.order_id = oi.order_id
    LEFT JOIN (
        SELECT 
            geolocation_zip_code_prefix,
            AVG(geolocation_lat) as geolocation_lat,
            AVG(geolocation_lng) as geolocation_lng
        FROM geolocation_dataset
        GROUP BY geolocation_zip_code_prefix
    ) as geo
        ON c.customer_zip_code_prefix = geo.geolocation_zip_code_prefix
    WHERE c.customer_state = 'SP' AND c.customer_city = 'sao paulo'
    GROUP BY c.customer_id, c.customer_unique_id, c.customer_city, c.customer_state, geo.geolocation_lat, geo.geolocation_lng
""")

# Calcular métricas únicas de clientes en São Paulo
unique_customers_initial = customers_sp['customer_id'].nunique()
total_compras_initial = customers_sp.groupby('customer_id')['num_compras'].sum().sum()
monto_total_initial = customers_sp.groupby('customer_id')['monto_total'].sum().sum()

print(f"Total clientes en São Paulo: {int(unique_customers_initial)}")

if len(customers_sp) > 0:
    # Calcular localización óptima usando centroide ponderado
    # Peso = monto total (mayor peso a clientes que más gastan)
    weights = customers_sp['monto_total'].values.astype(float)  # type: ignore
    total_weight = float(weights.sum())  # type: ignore
    
    optimal_lat = float(np.average(  # type: ignore
        customers_sp['geolocation_lat'].values.astype(float),  # type: ignore
        weights=weights  # type: ignore
    ))
    optimal_lng = float(np.average(  # type: ignore
        customers_sp['geolocation_lng'].values.astype(float),  # type: ignore
        weights=weights  # type: ignore
    ))
    
    print(f"   [OK] Ubicación óptima: {optimal_lat:.4f}, {optimal_lng:.4f}")
    print(f"   [OK] Clientes analizados: {int(unique_customers_initial)}")
    print(f"   [OK] Total de compras: {int(total_compras_initial)}")
    print(f"   [OK] Monto total: ${monto_total_initial:,.2f}")
else:
    optimal_lat = None
    optimal_lng = None

# =============================================================================
# CREAR MAPA INTERACTIVO
# =============================================================================

# Calcular el centro del mapa (centro de Brasil)
center_lat = map_data['latitude'].mean()
center_lng = map_data['longitude'].mean()

# Crear el mapa base
m = folium.Map(
    location=[center_lat, center_lng],
    zoom_start=4,
    tiles='OpenStreetMap'
)

# Normalizar ingresos para tamaño de círculo (radius)
max_revenue = map_data['total_revenue'].max()
min_revenue = map_data['total_revenue'].min()

# Crear círculos con tamaño proporcional a ingresos - AUMENTADOS
print("Agregando ciudades al mapa...")
for idx, row in map_data.iterrows():
    # Calcular radio proporcional (AUMENTADO: entre 15 y 150 píxeles)
    normalized_revenue = (row['total_revenue'] - min_revenue) / (max_revenue - min_revenue)
    radius = 15 + (normalized_revenue * 135)
    
    # Color según ingresos (gradiente)
    if row['total_revenue'] > max_revenue * 0.75:
        color = '#d73027'  # Rojo oscuro
    elif row['total_revenue'] > max_revenue * 0.5:
        color = '#fee090'  # Amarillo
    else:
        color = '#91bfdb'  # Azul
    
    # Crear popup con información
    popup_text = f"""
    <b>{row['customer_city'].upper()} ({row['customer_state']})</b><br>
    Ingresos: ${row['total_revenue']:,.0f}<br>
    Clientes: {int(row['unique_customers'])}<br>
    Órdenes: {int(row['total_orders'])}
    """
    
    # Agregar círculo al mapa
    folium.Circle(
        location=[row['latitude'], row['longitude']],
        radius=radius * 200,  # AUMENTADO: factor multiplicador
        popup=folium.Popup(popup_text, max_width=250),
        color=color,
        fill=True,
        fillOpacity=0.7,
        weight=2,
        fillColor=color
    ).add_to(m)

# =============================================================================
# AGREGAR UBICACIÓN ÓPTIMA CON ESTRELLA Y CLIENTES EN SÃO PAULO
# =============================================================================

if optimal_lat is not None and optimal_lng is not None:
    print(f"Agregando ubicación óptima y clientes de São Paulo...")
    
    # Calcular métricas correctas (sin duplicados por geolocation)
    unique_customers_count = customers_sp['customer_id'].nunique()
    total_compras_count = customers_sp.groupby('customer_id')['num_compras'].sum().sum()
    monto_total_count = customers_sp.groupby('customer_id')['monto_total'].sum().sum()
    
    # Marcar ubicación óptima con estrella
    folium.Marker(
        location=[optimal_lat, optimal_lng],
        popup=folium.Popup(
            f"""<b>📍 UBICACIÓN ÓPTIMA - SÃO PAULO</b><br><br>
            Coordenadas: {optimal_lat:.4f}, {optimal_lng:.4f}<br>
            Estrategia: Centroide ponderado por monto total gastado<br><br>
            <b>Métricas:</b><br>
            • Total clientes: {int(unique_customers_count)}<br>
            • Total compras: {int(total_compras_count)}<br>
            • Monto total: ${monto_total_count:,.2f}
            """,
            max_width=300
        ),
        icon=folium.Icon(color='orange', icon='star', prefix='fa', icon_color='white'),
        tooltip="🌟 Ubicación Óptima para Tienda en São Paulo"
    ).add_to(m)
    
    # Agregar los clientes de São Paulo en el mapa (solo una muestra para no sobrecargar)
    # Limitar a 1000 clientes para visualización (muestra aleatoria)
    customers_sample = customers_sp.drop_duplicates(subset=['customer_id']).sample(min(1000, len(customers_sp)), random_state=42)
    print(f"   Mostrando muestra de: {len(customers_sample)} clientes")
    
    for idx, customer in customers_sample.iterrows():
        folium.CircleMarker(
            location=[customer['geolocation_lat'], customer['geolocation_lng']],
            radius=3,
            popup=folium.Popup(
                f"""<b>Cliente São Paulo</b><br>
                Compras: {int(customer['num_compras'])}<br>
                Monto: ${customer['monto_total']:,.2f}
                """,
                max_width=200
            ),
            color='#1f77b4',
            fill=True,
            fillColor='#1f77b4',
            fillOpacity=0.5,
            weight=0.5,
            opacity=0.7
        ).add_to(m)
    
    print(f"   [OK] Total de clientes en la base: {len(customers_sp)}")

# Agregar leyenda mejorada
legend_html = '''
<div style="position: fixed; 
     bottom: 50px; right: 50px; width: 260px; height: 280px; 
     background-color: white; border:2px solid #333; border-radius: 5px; 
     z-index:9999; font-size:14px; padding: 15px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
     <b style="font-size:16px; color:#1f77b4;">📊 LEYENDA DEL MAPA</b><hr>
     
     <b>Ciudades por Ingresos:</b><br>
     <i style="background:#d73027; width:20px; height:20px; display:inline-block; border-radius:3px;"></i> Muy Alto (>75%)<br>
     <i style="background:#fee090; width:20px; height:20px; display:inline-block; border-radius:3px;"></i> Medio (50-75%)<br>
     <i style="background:#91bfdb; width:20px; height:20px; display:inline-block; border-radius:3px;"></i> Bajo (<50%)<br><br>
     
     <small><b>Tamaño = Ingresos totales</b><br>
     <b>★ = Ubicación óptima en SP</b><br>
     <b>🔵 = Clientes en São Paulo</b></small>
</div>
'''
# Agregar la leyenda al mapa
root = m.get_root()  # type: ignore
try:
    root.html.add_child(folium.Element(legend_html))  # type: ignore
except (AttributeError, TypeError):
    # Si no funciona el método anterior, usar alternativa
    try:
        root.script.add_child(folium.Element(legend_html))  # type: ignore
    except (AttributeError, TypeError):
        # Última opción: crear un usuario personalizado
        pass

# Guardar mapa HTML
output_path = 'results/answer_05/mapa_brasil_ingresos.html'
m.save(output_path)
print(f"\n Mapa interactivo guardado: {output_path}")