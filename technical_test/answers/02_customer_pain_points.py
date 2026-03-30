import matplotlib.pyplot as plt
from ..utils.database import Database
from ..utils.export_results import save_to_csv, save_plot

db = Database()

# Consulta 1: Categorías con peor calificación promedio
query_categorias_rating = db.query("""
    SELECT 
        pt.product_category_name_english as categoria,
        COUNT(DISTINCT r.order_id) as total_reviews,
        ROUND(AVG(r.review_score), 2) as rating_promedio,
        COUNT(CASE WHEN r.review_score <= 2 THEN 1 END) as reseñas_negativas,
        ROUND(
            COUNT(CASE WHEN r.review_score <= 2 THEN 1 END) * 100.0 / 
            COUNT(DISTINCT r.order_id), 
            2
        ) as porcentaje_negativo
    FROM order_reviews_dataset r
    INNER JOIN order_items_dataset oi ON r.order_id = oi.order_id
    INNER JOIN products_dataset p ON oi.product_id = p.product_id
    INNER JOIN product_category_name_translation pt ON p.product_category_name = pt.product_category_name
    GROUP BY pt.product_category_name_english
    HAVING COUNT(DISTINCT r.order_id) >= 5
    ORDER BY rating_promedio ASC, reseñas_negativas DESC
    LIMIT 15
""")

save_to_csv(query_categorias_rating, file="categorias_peor_rating.csv", folder="answer_02")

# Gráfico 1: Categorías con peor rating
fig1, ax1 = plt.subplots(figsize=(12, 8))
top_categorias = query_categorias_rating.head(10)
ax1.barh(top_categorias['categoria'], top_categorias['rating_promedio'], color='#d62728', edgecolor='black')
ax1.set_xlabel('Rating Promedio', fontweight='bold')
ax1.set_title('Top 10 Categorías con PEOR Rating Promedio', fontweight='bold', fontsize=14)
ax1.set_xlim(0, 5)
for i, v in enumerate(top_categorias['rating_promedio']):
    ax1.text(v + 0.1, i, f'{v}', va='center', fontweight='bold')
plt.tight_layout()

save_plot(fig1, file="categorias_peor_rating.png", folder="answer_02", dpi=300)

# Consulta 2: Productos más criticados
query_productos_problematicos = db.query("""
    SELECT 
        p.product_id,
        p.product_category_name as categoria_portugues,
        pt.product_category_name_english as categoria_ingles,
        COUNT(r.review_id) as total_reviews,
        ROUND(AVG(r.review_score), 2) as rating_promedio,
        COUNT(CASE WHEN r.review_score <= 2 THEN 1 END) as reseñas_negativas,
        COUNT(CASE WHEN r.review_comment_message != '' THEN 1 END) as reviews_con_comentario
    FROM order_reviews_dataset r
    INNER JOIN order_items_dataset oi ON r.order_id = oi.order_id
    INNER JOIN products_dataset p ON oi.product_id = p.product_id
    INNER JOIN product_category_name_translation pt ON p.product_category_name = pt.product_category_name
    WHERE r.review_score <= 2
    GROUP BY p.product_id, p.product_category_name, pt.product_category_name_english
    HAVING COUNT(r.review_id) >= 3
    ORDER BY reseñas_negativas DESC, rating_promedio ASC
    LIMIT 20
""")

save_to_csv(query_productos_problematicos, file="productos_problematicos.csv", folder="answer_02")

# Gráfico 2: Productos problemáticos por categoría
fig2, ax2 = plt.subplots(figsize=(12, 8))
top_productos = query_productos_problematicos.head(10)
ax2.barh(top_productos['categoria_ingles'] + ' (ID: ' + top_productos['product_id'].astype(str) + ')', 
         top_productos['reseñas_negativas'], color='#ff7f0e', edgecolor='black')
ax2.set_xlabel('Cantidad de Reseñas Negativas', fontweight='bold')
ax2.set_title('Top 10 Productos Más Criticados (Rating 1-2)', fontweight='bold', fontsize=14)
for i, v in enumerate(top_productos['reseñas_negativas']):
    ax2.text(v + 0.5, i, f'{int(v)}', va='center', fontweight='bold')
plt.tight_layout()

save_plot(fig2, file="productos_problematicos.png", folder="answer_02", dpi=300)