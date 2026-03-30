import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from ..utils.database import Database
from ..utils.export_results import save_to_csv, save_plot

db = Database()

print("\nIniciando análisis de segmentación de clientes (RFM)...")

# =============================================================================
# PASO 1: CONSTRUCCIÓN DE MÉTRICAS RFM
# =============================================================================

def build_rfm(reference_date=None):
    """
    Construye tabla RFM (Recency, Frequency, Monetary) por cliente único.
    """
    
    query = """
        SELECT 
            c.customer_unique_id,
            o.customer_id,
            o.order_id,
            o.order_purchase_timestamp,
            COALESCE(SUM(p.payment_value), 0) as order_value
        FROM customers_dataset c
        INNER JOIN orders_dataset o ON c.customer_id = o.customer_id
        LEFT JOIN order_payments_dataset p ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id, o.customer_id, o.order_id, o.order_purchase_timestamp
    """
    
    orders_payments = db.query(query)
    orders_payments["order_purchase_timestamp"] = pd.to_datetime(
        orders_payments["order_purchase_timestamp"]
    )
    
    if reference_date is None:
        reference_date = orders_payments["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    
    print(f"   Fecha de referencia RFM: {reference_date.date()}")
    print(f"   Total órdenes analizadas: {len(orders_payments)}")
    
    rfm = (
        orders_payments.groupby("customer_unique_id")
        .agg(
            recency=(
                "order_purchase_timestamp",
                lambda x: (reference_date - x.max()).days,
            ),
            frequency=("order_id", "count"),
            monetary=("order_value", "sum"),
        )
        .reset_index()
    )
    
    print(f"   Total clientes únicos: {len(rfm)}")
    
    return rfm


# =============================================================================
# PASO 2: ASIGNACIÓN DE SCORES RFM
# =============================================================================

def add_rfm_scores(rfm, q=4):
    """Asigna scores de 1 a q para cada métrica RFM."""
    
    r = rfm.copy()
    
    r["R_score"] = pd.qcut(
        r["recency"], q=q, labels=range(q, 0, -1), duplicates="drop"
    )
    r["F_score"] = pd.qcut(
        r["frequency"].rank(method="first"),
        q=q,
        labels=range(1, q + 1),
        duplicates="drop",
    )
    r["M_score"] = pd.qcut(
        r["monetary"].rank(method="first"),
        q=q,
        labels=range(1, q + 1),
        duplicates="drop",
    )
    
    r["RFM_score"] = (
        r["R_score"].astype(int) + r["F_score"].astype(int) + r["M_score"].astype(int)
    )
    
    return r


# =============================================================================
# PASO 3: CONSTRUCCIÓN Y VISUALIZACIÓN RFM
# =============================================================================

print("\nConstruyendo métricas RFM...")
rfm = build_rfm()
rfm = add_rfm_scores(rfm)  # type: ignore

rfm_summary = rfm[["recency", "frequency", "monetary", "RFM_score"]].describe().round(2)
save_to_csv(rfm_summary, file="rfm_summary.csv", folder="answer_03")

print("Generando visualización RFM...")
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, col, label in zip(
    axes,
    ["recency", "frequency", "monetary"],
    ["Recency (días)", "Frequency (compras)", "Monetary (BRL)"],
):
    data_clipped = rfm[col].clip(upper=rfm[col].quantile(0.95))
    ax.hist(data_clipped, bins=40, color="skyblue", edgecolor="black", alpha=0.7)
    ax.set_title(f"{label}", fontweight="bold", fontsize=12)
    ax.set_xlabel(label, fontweight="bold")
    ax.set_ylabel("Cantidad de Clientes", fontweight="bold")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
save_plot(fig, file="distribucion_rfm.png", folder="answer_03", dpi=300)

# =============================================================================
# PASO 4: DETERMINACIÓN DE K ÓPTIMO Y CLUSTERING
# =============================================================================

def optimal_k(X_scaled: np.ndarray, k_range: range = range(2, 8)) -> int:
    """Determina k óptimo usando Silhouette Score."""
    print("\nCalculando k óptimo...")
    scores: dict[int, float] = {}
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        scores[k] = float(silhouette_score(X_scaled, labels))
        print(f"   k={k}: Silhouette Score = {scores[k]:.4f}")
    
    best_k = int(max(scores, key=lambda x: scores[x]))
    print(f"   Mejor k: {best_k}")
    return best_k


print("\nEjecutando clustering KMeans...")
features = ["recency", "frequency", "monetary"]
X = rfm[features].fillna(0)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

best_k = optimal_k(X_scaled)

km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
rfm["cluster"] = km.fit_predict(X_scaled)

cluster_scores = (
    rfm.groupby("cluster")["RFM_score"].mean().sort_values(ascending=False)
)

SEGMENT_LABELS = {
    0: "Clientes Fieles",
    1: "En Riesgo",
    2: "Inactivos",
    3: "Nuevos",
}

rank_map = {orig: rank for rank, orig in enumerate(cluster_scores.index)}
rfm["cluster_ranked"] = rfm["cluster"].map(rank_map)
rfm["segment"] = rfm["cluster_ranked"].map(SEGMENT_LABELS).fillna("Otros")

# =============================================================================
# PASO 5: ESTADÍSTICAS Y EXPORTACIÓN
# =============================================================================

print("\nGenerando estadísticas por segmento...")

segment_stats = (
    rfm.groupby("segment")
    .agg(
        n_clientes=("customer_unique_id", "count"),
        recency_mean=("recency", "mean"),
        frequency_mean=("frequency", "mean"),
        monetary_mean=("monetary", "mean"),
        monetary_total=("monetary", "sum"),
        rfm_score_mean=("RFM_score", "mean"),
    )
    .round(2)
    .sort_values("monetary_total", ascending=False)
)

print("\n" + "="*80)
print("ESTADÍSTICAS DE SEGMENTACIÓN")
print("="*80)
print(segment_stats)
print("="*80)

save_to_csv(segment_stats, file="segment_statistics.csv", folder="answer_03")

rfm_export = rfm[
    [
        "customer_unique_id",
        "recency",
        "frequency",
        "monetary",
        "R_score",
        "F_score",
        "M_score",
        "RFM_score",
        "segment",
    ]
]
save_to_csv(rfm_export, file="clientes_segmentacion.csv", folder="answer_03")

# =============================================================================
# PASO 6: VISUALIZACIONES DE SEGMENTOS
# =============================================================================

print("\nGenerando visualizaciones...")

# Gráfico 1: Métricas por segmento
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, metric in zip(axes, ["recency", "frequency", "monetary"]):
    data = rfm.groupby("segment")[metric].mean().sort_values()
    data.plot.barh(ax=ax, color="#1f77b4", edgecolor="black")  # type: ignore
    ax.set_title(f"{metric.capitalize()} Promedio", fontweight="bold", fontsize=12)
    ax.grid(True, alpha=0.3, axis="x")

plt.tight_layout()
save_plot(fig, file="metricas_por_segmento.png", folder="answer_03", dpi=300)

# Gráfico 2: Distribución de clientes
fig, ax = plt.subplots(figsize=(10, 6))
segment_counts = rfm["segment"].value_counts().sort_values(ascending=False)
colors_pie = ["#2ca02c", "#d73027", "#fee090", "#91bfdb"]
result = ax.pie(
    segment_counts.to_numpy().astype(float),
    labels=segment_counts.index.tolist(),
    autopct="%1.1f%%",
    colors=colors_pie[:len(segment_counts)],
)
wedges = result[0]
texts = result[1]
autotexts = result[2] if len(result) > 2 else []
ax.set_title("Distribución de Clientes", fontweight="bold", fontsize=14)
for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontweight("bold")

plt.tight_layout()
save_plot(fig, file="distribucion_segmentos.png", folder="answer_03", dpi=300)

# Gráfico 3: Ingresos por segmento
fig, ax = plt.subplots(figsize=(12, 6))
segment_revenue = rfm.groupby("segment")["monetary"].sum().sort_values(ascending=False)
colors_bar = ["#2ca02c", "#d73027", "#fee090", "#91bfdb"]
ax.bar(
    segment_revenue.index.tolist(),
    segment_revenue.to_numpy().astype(float),
    color=colors_bar[:len(segment_revenue)],
    edgecolor="black",
)
ax.set_ylabel("Ingresos (BRL)", fontweight="bold")
ax.set_title("Ingresos Totales por Segmento", fontweight="bold", fontsize=14)
ax.grid(True, alpha=0.3, axis="y")
revenue_values = segment_revenue.to_numpy().astype(float)
for i, val in enumerate(revenue_values):
    ax.text(i, float(val), f"${val:,.0f}", ha="center", va="bottom", fontweight="bold")

plt.tight_layout()
save_plot(fig, file="ingresos_por_segmento.png", folder="answer_03", dpi=300)

# Gráfico 4: Scatter 3D
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection="3d")

segments_unique = rfm["segment"].unique()
colors_3d = {
    "Clientes Fieles": "#2ca02c",
    "En Riesgo": "#d73027",
    "Inactivos": "#fee090",
    "Nuevos": "#91bfdb",
}

for seg in segments_unique:
    mask = rfm["segment"] == seg
    recency_vals = np.asarray(rfm.loc[mask, "recency"], dtype=np.float64)
    frequency_vals = np.asarray(rfm.loc[mask, "frequency"], dtype=np.float64)
    monetary_vals = np.asarray(rfm.loc[mask, "monetary"], dtype=np.float64)
    ax.scatter(
        recency_vals,
        frequency_vals,
        monetary_vals,  # type: ignore
        label=seg,
        color=colors_3d.get(seg, "#1f77b4"),
        alpha=0.6,
        s=30,
    )

ax.set_xlabel("Recency (días)", fontweight="bold")
ax.set_ylabel("Frequency (compras)", fontweight="bold")
ax.set_zlabel("Monetary (BRL)", fontweight="bold")
ax.set_title("Segmentación RFM - Visualización 3D", fontweight="bold", fontsize=14)
ax.legend(fontsize=10)

plt.tight_layout()
save_plot(fig, file="segmentacion_3d.png", folder="answer_03", dpi=300)

print("\n✓ Análisis de segmentación completado.")
print("✓ Resultados guardados en: results/answer_03/")
