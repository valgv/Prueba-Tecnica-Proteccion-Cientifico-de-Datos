import json
from pathlib import Path

import pandas as pd

from ..utils.database import Database
from ..utils.export_results import save_to_csv, save_to_json

db = Database()

print("\nIniciando generación de System Prompts hiper-personalizados...")

# =============================================================================
# PASO 1: DEFINICIÓN DE LOS TRES SYSTEM PROMPTS
# =============================================================================

# ── SYSTEM PROMPT 1: Cliente joven, digital, comprador frecuente ──────────────
PROMPT_1 = """Eres Nova, asistente de compras personal de nuestra plataforma de e-commerce.
Tu estilo es fresco, preciso y orientado a la acción. Hablas de tú a tú.

## PERFIL DEL CLIENTE
- Edad: {EDAD} años
- Género: {GENERO}
- Segmento CRM: {PERFIL_CLIENTE}
- Historial de compras:
{HISTORIAL_COMPRAS}

## CATÁLOGO DE PRODUCTOS
{BASE_CONOCIMIENTO}

## INSTRUCCIONES DE COMPORTAMIENTO

TONO Y ESTILO:
- Directo, ágil y cercano. Este cliente ya conoce la plataforma.
- Puedes usar hasta 2 emojis por respuesta si enriquecen la comunicación.
- Usa su historial para personalizar, identifica patrones de frecuencia SIEMPRE: "Ya que eres fan de [categoría]..."
- Destaca tendencias, novedades y lanzamientos relevantes para sus categorías top.
- Incentiva la acción inmediata (urgencia suave: stock limitado, popularidad, etc.).
- Máximo 3 recomendaciones por respuesta, bien justificadas.

RECOMENDACIÓN:
- Prioriza productos de sus categorías top o complementarios.
- Si ya compró algo del catálogo, celebra la elección y sugiere el siguiente paso.
- Sugiere productos complementarios (cross-selling).
- Menciona el precio promedio real del dataset para anclar expectativas.

MANEJO DE OBJECIONES:
- Si pregunta por precio: usa los rangos reales del catálogo.
- Si no está seguro: ofrece comparativa rápida (pros/contras en 2 líneas).

RESTRICCIONES:
- No inventes precios fuera de los rangos del catálogo.
- No prometas fechas de entrega sin datos confirmados.
- Si la consulta está fuera de tu alcance, deriva a soporte de forma ágil.
"""

# ── SYSTEM PROMPT 2: Cliente mayor, conservador, con mala experiencia ─────────
PROMPT_2 = """Eres Nova, asistente de compras personal de nuestra plataforma de e-commerce.
Tu prioridad absoluta es la confianza, la seguridad y la satisfacción del cliente. Hablas con calidez y claridad.

## PERFIL DEL CLIENTE
- Edad: {EDAD} años
- Género: {GENERO}
- Segmento CRM: {PERFIL_CLIENTE}
- Historial de compras:
{HISTORIAL_COMPRAS}

## CATÁLOGO DE PRODUCTOS
{BASE_CONOCIMIENTO}

## INSTRUCCIONES DE COMPORTAMIENTO

TONO Y ESTILO:
- Empático, claro y sin tecnicismos. Sin prisas.
- Usa frases como: "Entendemos perfectamente su situación" o "Para nosotros su experiencia es lo primero".
- No presiones. El cliente decide el ritmo de la conversación.

MANEJO DE EXPERIENCIA NEGATIVA PREVIA:
- Si has_prior_complaint es true: reconoce SIEMPRE la situación antes de cualquier recomendación.
- Ejemplo: "Veo que su experiencia anterior no fue la que merecía. Queremos asegurarnos de que esta vez sea perfecta."
- Ofrece garantías concretas: política de devolución, tiempo de entrega, soporte disponible.
- Evita recomendar la misma categoría donde tuvo problemas, salvo que el cliente la solicite.

RECOMENDACIÓN:
- Introduce máximo 2 productos, con garantías explícitas.
- Siempre menciona: tiempo de entrega estimado, política de devolución y canal de soporte.
- Termina siempre preguntando si puede ayudar en algo más.

RESTRICCIONES:
- NUNCA minimices ni ignores una queja previa.
- Si el cliente está frustrado, escucha primero. No respondas con argumentos de venta.
- Sin emojis en este contexto.
"""

# ── SYSTEM PROMPT 3: Cliente VIP / Corporativo ────────────────────────────────
PROMPT_3 = """Eres Luxa, asistente personal VIP de compras de nuestra plataforma de e-commerce.
Operas en el segmento de clientes de alto valor. Tu enfoque es consultivo, proactivo y sofisticado.

## PERFIL DEL CLIENTE
- Edad: {EDAD} años
- Género: {GENERO}
- Segmento CRM: {PERFIL_CLIENTE}
- Historial de compras:
{HISTORIAL_COMPRAS}

## CATÁLOGO PREMIUM
{BASE_CONOCIMIENTO}

## INSTRUCCIONES DE COMPORTAMIENTO

TONO Y ESTILO:
- Ejecutivo, preciso y consultivo. Sin jerga informal.
- Usa "usted" y tono formal cuando el contexto lo requiera.
- Trátalo como socio estratégico, no como comprador ocasional.
- Referencia su historial para demostrar conocimiento profundo del cliente.
- Prioriza calidad, exclusividad y eficiencia sobre precio.

RECOMENDACIÓN PROACTIVA:
- Anticipa necesidades basadas en su historial de categorías.
- Ejemplo: "Dado su volumen en [categoría], le anticipo que tenemos acceso preferencial a..."
- Para compras corporativas: menciona facturación, entregas múltiples y gestor de cuenta.
- Si aplica, sugiere soluciones integrales en lugar de productos individuales.

BENEFICIOS VIP A MENCIONAR CUANDO SEA RELEVANTE:
- Línea directa de soporte (respuesta < 2h garantizada)
- Devoluciones sin preguntas hasta 60 días
- Acceso anticipado a nuevos productos
- Facturación y envío a múltiples destinos

RESTRICCIONES:
- No ofrezcas beneficios VIP a clientes que no sean de este segmento.
- Mantén la confidencialidad del esquema de segmentación interno.
- Si solicita algo fuera del catálogo, ofrece cotización personalizada vía gestor.
"""

# =============================================================================
# PASO 2: IDENTIFICAR CLIENTES REPRESENTATIVOS POR ESCENARIO VÍA SQL
# =============================================================================

print("\nIdentificando clientes representativos por escenario via SQL...")

# Escenario 1: Comprador frecuente con buen rating
df_frecuente = db.query("""
    SELECT
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        COUNT(DISTINCT o.order_id)          AS total_orders,
        ROUND(SUM(p.payment_value), 2)      AS total_spent,
        ROUND(AVG(r.review_score), 2)       AS avg_rating
    FROM customers_dataset c
    JOIN orders_dataset o         ON c.customer_id = o.customer_id
    JOIN order_payments_dataset p ON o.order_id    = p.order_id
    LEFT JOIN order_reviews_dataset r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
    ORDER BY total_orders DESC, avg_rating DESC
    LIMIT 1
""")

# Escenario 2: Cliente con queja previa documentada (min_rating <= 2)
df_queja = db.query("""
    SELECT * FROM (
        SELECT
            c.customer_unique_id,
            c.customer_city,
            c.customer_state,
            COUNT(DISTINCT o.order_id)          AS total_orders,
            ROUND(SUM(p.payment_value), 2)      AS total_spent,
            ROUND(MIN(r.review_score), 0)       AS min_rating,
            ROUND(AVG(r.review_score), 2)       AS avg_rating
        FROM customers_dataset c
        JOIN orders_dataset o         ON c.customer_id = o.customer_id
        JOIN order_payments_dataset p ON o.order_id    = p.order_id
        JOIN order_reviews_dataset r  ON o.order_id    = r.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
    ) sub
    WHERE sub.min_rating <= 2
    ORDER BY sub.avg_rating ASC, sub.total_orders ASC
    LIMIT 1
""")

# Escenario 3: Cliente VIP (top gasto, múltiples órdenes)
df_vip = db.query("""
    SELECT * FROM (
        SELECT
            c.customer_unique_id,
            c.customer_city,
            c.customer_state,
            COUNT(DISTINCT o.order_id)          AS total_orders,
            ROUND(SUM(p.payment_value), 2)      AS total_spent,
            ROUND(AVG(r.review_score), 2)       AS avg_rating
        FROM customers_dataset c
        JOIN orders_dataset o         ON c.customer_id = o.customer_id
        JOIN order_payments_dataset p ON o.order_id    = p.order_id
        LEFT JOIN order_reviews_dataset r ON o.order_id = r.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
    ) sub
    WHERE sub.total_orders >= 3
    ORDER BY sub.total_spent DESC
    LIMIT 1
""")

print(f"  Escenario 1 (Frecuente): {df_frecuente.iloc[0]['customer_unique_id']}")
print(f"  Escenario 2 (Queja):     {df_queja.iloc[0]['customer_unique_id']}")
print(f"  Escenario 3 (VIP):       {df_vip.iloc[0]['customer_unique_id']}")

# =============================================================================
# PASO 3: FUNCIÓN PARA CALCULAR HISTORIAL DE COMPRAS
# =============================================================================

def compute_purchase_history(customer_unique_id: str) -> dict:
    """
    Genera un resumen compacto del historial de un cliente para inyectar
    como {HISTORIAL_COMPRAS} en el system prompt.
    Usa db.tables para no depender de rutas hardcodeadas.
    """
    customers    = db.tables['customers_dataset']
    orders       = db.tables['orders_dataset']
    order_items  = db.tables['order_items_dataset']
    products     = db.tables['products_dataset']
    payments     = db.tables['order_payments_dataset']
    reviews      = db.tables['order_reviews_dataset']
    translations = db.tables['product_category_name_translation']

    customer_ids = customers[
        customers['customer_unique_id'] == customer_unique_id
    ]['customer_id'].tolist()

    if not customer_ids:
        return {'error': 'cliente no encontrado', 'customer_unique_id': customer_unique_id}

    cust_orders = orders[orders['customer_id'].isin(customer_ids)]
    if cust_orders.empty:
        return {'error': 'sin pedidos', 'customer_unique_id': customer_unique_id}

    order_ids = cust_orders['order_id'].tolist()

    # Pagos
    cust_payments     = payments[payments['order_id'].isin(order_ids)]
    total_spent       = cust_payments['payment_value'].sum()
    preferred_payment = (
        cust_payments['payment_type'].mode().iloc[0]
        if not cust_payments.empty else 'N/A'
    )
    avg_installments  = cust_payments['payment_installments'].mean()

    # Categorías compradas
    bought = order_items[order_items['order_id'].isin(order_ids)].copy()
    bought = bought.merge(
        products[['product_id', 'product_category_name']], on='product_id', how='left'
    ).merge(translations, on='product_category_name', how='left')
    bought['cat'] = (
        bought['product_category_name_english']
        .combine_first(bought['product_category_name'])
    )
    top_categories = bought['cat'].value_counts().head(3).index.tolist()

    # Reseñas
    cust_reviews   = reviews[reviews['order_id'].isin(order_ids)]
    avg_score      = cust_reviews['review_score'].mean() if not cust_reviews.empty else None
    has_complaints = bool((cust_reviews['review_score'] <= 3).any()) if not cust_reviews.empty else False
    n_negative     = int((cust_reviews['review_score'] <= 3).sum()) if not cust_reviews.empty else 0

    # Fechas
    last_purchase  = pd.to_datetime(cust_orders['order_purchase_timestamp'].max())
    first_purchase = pd.to_datetime(cust_orders['order_purchase_timestamp'].min())
    tenure_days    = (last_purchase - first_purchase).days if pd.notna(first_purchase) else 0

    return {
        'customer_unique_id':  customer_unique_id,
        'total_orders':        len(order_ids),
        'total_items':         len(bought),
        'total_spent_BRL':     round(total_spent, 2),
        'avg_order_value_BRL': round(total_spent / len(order_ids), 2),
        'preferred_payment':   preferred_payment,
        'avg_installments':    round(avg_installments, 1) if not pd.isna(avg_installments) else 1,
        'top_categories':      top_categories,
        'avg_review_score':    round(avg_score, 2) if avg_score else None,
        'has_prior_complaint': has_complaints,
        'n_negative_reviews':  n_negative,
        'first_purchase':      str(first_purchase)[:10] if pd.notna(first_purchase) else None,
        'last_purchase':       str(last_purchase)[:10] if pd.notna(last_purchase) else None,
        'tenure_days':         tenure_days,
        'order_statuses':      cust_orders['order_status'].value_counts().to_dict(),
    }


def format_purchase_history(hist: dict) -> str:
    """Convierte el dict de historial en texto legible para inyectar en el prompt."""
    if 'error' in hist:
        return "Sin historial de compras disponible."
    cats = ', '.join(hist.get('top_categories', [])) or 'N/A'
    return (
        f"- Total pedidos:             {hist['total_orders']}\n"
        f"- Total gastado:             BRL {hist['total_spent_BRL']:,.2f}\n"
        f"- Ticket promedio:           BRL {hist['avg_order_value_BRL']:,.2f}\n"
        f"- Categorías favoritas:      {cats}\n"
        f"- Método de pago preferido:  {hist['preferred_payment']}\n"
        f"- Cuotas promedio:           {hist['avg_installments']}\n"
        f"- Rating promedio:           {hist['avg_review_score'] or 'N/A'}\n"
        f"- Quejas previas:            {'Sí' if hist['has_prior_complaint'] else 'No'}\n"
        f"- Primera compra:            {hist['first_purchase'] or 'N/A'}\n"
        f"- Última compra:             {hist['last_purchase'] or 'N/A'}\n"
        f"- Antigüedad:                {hist['tenure_days']} días"
    )

# =============================================================================
# PASO 4: CALCULAR HISTORIALES Y CONSTRUIR PERFILES
# =============================================================================

print("\nCalculando historiales de compra para clientes representativos...")

# Perfiles CRM simulados (en producción vienen del CRM real)
PERFILES_CRM = {
    'escenario_1_joven_digital': {
        'edad': 27, 'genero': 'Masculino', 'segment': 'Clientes Fieles',
        'uid': df_frecuente.iloc[0]['customer_unique_id'],
    },
    'escenario_2_mayor_conservador': {
        'edad': 62, 'genero': 'Femenino', 'segment': 'En Riesgo',
        'uid': df_queja.iloc[0]['customer_unique_id'],
    },
    'escenario_3_vip_corporativo': {
        'edad': 45, 'genero': 'Masculino', 'segment': 'Clientes Fieles',
        'uid': df_vip.iloc[0]['customer_unique_id'],
    },
}

historiales = {
    key: compute_purchase_history(val['uid'])
    for key, val in PERFILES_CRM.items()
}

# =============================================================================
# PASO 5: LEER BASE DE CONOCIMIENTO (generada en answer_06)
# =============================================================================

kb_path = Path(__file__).parent.parent.parent / 'results' / 'answer_06' / 'knowledge_base.json'
if kb_path.exists():
    with open(kb_path, encoding='utf-8') as f:
        knowledge_base = json.load(f)
    kb_str = json.dumps(knowledge_base, ensure_ascii=False, indent=2)
    print("  Base de conocimiento cargada desde answer_06/knowledge_base.json")
else:
    kb_str = "[BASE DE CONOCIMIENTO NO DISPONIBLE - ejecutar answer_06 primero]"
    print("  ADVERTENCIA: knowledge_base.json no encontrado. Ejecute answer_06 primero.")

# =============================================================================
# PASO 6: RENDERIZAR PROMPTS CON DATOS REALES
# =============================================================================

PROMPTS_TEMPLATE = {
    'escenario_1_joven_digital':     PROMPT_1,
    'escenario_2_mayor_conservador': PROMPT_2,
    'escenario_3_vip_corporativo':   PROMPT_3,
}

print("\nRenderizando prompts con datos reales de clientes...")

rendered_rows = []
for key, perfil in PERFILES_CRM.items():
    hist     = historiales[key]
    hist_str = format_purchase_history(hist)
    template = PROMPTS_TEMPLATE[key]
    rendered = template.format(
        EDAD=perfil['edad'],
        GENERO=perfil['genero'],
        PERFIL_CLIENTE=perfil['segment'],
        HISTORIAL_COMPRAS=hist_str,
        BASE_CONOCIMIENTO=kb_str,
    )
    rendered_rows.append({
        'escenario':          key,
        'customer_unique_id': perfil['uid'],
        'edad_simulada':      perfil['edad'],
        'genero_simulado':    perfil['genero'],
        'segmento_crm':       perfil['segment'],
        'agente':             'Luxa' if key == 'escenario_3_vip_corporativo' else 'Nova',
        'longitud_prompt':    len(rendered),
        'prompt_preview':     rendered[:300].replace('\n', ' ') + '...',
        'prompt_completo':    rendered,
    })

df_rendered = pd.DataFrame(rendered_rows)

# =============================================================================
# PASO 7: GUARDAR RESULTADOS EN answer_07
# =============================================================================

print("\nGuardando resultados en answer_07/...")

prompts_only = {
    'escenario_1_joven_digital':     PROMPT_1,
    'escenario_2_mayor_conservador': PROMPT_2,
    'escenario_3_vip_corporativo':   PROMPT_3,
}
save_to_json(prompts_only, file="prompts_templates.json", folder="answer_07")

save_to_csv(
    df_rendered[[
        'escenario', 'customer_unique_id', 'edad_simulada', 'genero_simulado',
        'segmento_crm', 'agente', 'longitud_prompt', 'prompt_completo',
    ]],
    file="prompts_renderizados.csv",
    folder="answer_07",
)

print("\n✓ System Prompts completados. Archivos guardados en results/answer_07/")
