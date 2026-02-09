import os
from typing import List, Dict, Any
from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="BI Docker Workshop API", version="1.0.0")

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "sales"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin"),
        cursor_factory=RealDictCursor,
    )

@app.get("/health")
def health() -> Dict[str, str]:
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 as ok;")
                _ = cur.fetchone()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/sales")
def sales(limit: int = 200) -> List[Dict[str, Any]]:
    """Return sales rows (Power BI can ingest this via Web connector)."""
    query = """
        SELECT sale_date, country, channel, product_category, product,
               units, unit_price, revenue
        FROM sales
        ORDER BY sale_date DESC
        LIMIT %s;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
    return rows

@app.get("/kpi/revenue_by_country")
def revenue_by_country() -> List[Dict[str, Any]]:
    query = """
        SELECT country, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY country
        ORDER BY total_revenue DESC;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    return rows
