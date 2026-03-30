import matplotlib.pyplot as plt
from ..utils.database import Database
from ..utils.export_results import save_to_csv, save_plot

db = Database()

# Consulta 1: Top 5 por Volumen
resultado_volumen = db.query("""
    SELECT 
        p.product_category_name as categoria_portugues,
        pt.product_category_name_english as categoria_ingles,
        COUNT(oi.order_item_id) as items_vendidos
    FROM products_dataset p
    JOIN order_items_dataset oi ON p.product_id = oi.product_id
    LEFT JOIN product_category_name_translation pt ON p.product_category_name = pt.product_category_name
    GROUP BY p.product_category_name, pt.product_category_name_english
    ORDER BY items_vendidos DESC
    LIMIT 5
""")

save_to_csv(resultado_volumen, file="top_categorias_volumen.csv", folder="answer_01")

# Gráfico 1: Volumen
fig1, ax1 = plt.subplots(figsize=(12, 6))
ax1.bar(resultado_volumen['categoria_ingles'], resultado_volumen['items_vendidos'], color='#2ca02c', edgecolor='black')
ax1.set_ylabel('Items Vendidos', fontweight='bold')
ax1.set_title('Top 5 Categorías por Volumen de Ventas', fontweight='bold', fontsize=14)
ax1.tick_params(axis='x', rotation=45)
for i, v in enumerate(resultado_volumen['items_vendidos']):
    ax1.text(i, v, f'{int(v):,}', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()

save_plot(fig1, file="top_categorias_volumen.png", folder="answer_01", dpi=300)

# Consulta 2: Top 5 por Ingresos
resultado_ingresos = db.query("""
    SELECT 
        p.product_category_name as categoria_portugues,
        pt.product_category_name_english as categoria_ingles,
        ROUND(SUM(oi.price), 2) as ingresos_totales
    FROM products_dataset p
    JOIN order_items_dataset oi ON p.product_id = oi.product_id
    LEFT JOIN product_category_name_translation pt ON p.product_category_name = pt.product_category_name
    GROUP BY p.product_category_name, pt.product_category_name_english
    ORDER BY ingresos_totales DESC
    LIMIT 5
""")

save_to_csv(resultado_ingresos, file="top_categorias_ingresos.csv", folder="answer_01")

# Gráfico 2: Ingresos
fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.bar(resultado_ingresos['categoria_ingles'], resultado_ingresos['ingresos_totales'], color='#1f77b4', edgecolor='black')
ax2.set_ylabel('Ingresos ($)', fontweight='bold')
ax2.set_title('Top 5 Categorías por Ingresos Totales', fontweight='bold', fontsize=14)
ax2.tick_params(axis='x', rotation=45)
for i, v in enumerate(resultado_ingresos['ingresos_totales']):
    ax2.text(i, v, f'${v:,.0f}', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()

save_plot(fig2, file="top_categorias_ingresos.png", folder="answer_01", dpi=300)