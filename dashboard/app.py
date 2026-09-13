import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

import pandas as pd
import streamlit as st
from db import get_connection

st.set_page_config(page_title="Sentinel Dashboard", layout="wide")
st.title("Sentinel — Prompt Injection Firewall Dashboard")

conn = get_connection()

col1, col2, col3 = st.columns(3)

total = conn.execute("SELECT COUNT(*) FROM SENTINEL.AUDIT_LOG").fetchone()[0]
blocked = conn.execute(
    "SELECT COUNT(*) FROM SENTINEL.AUDIT_LOG WHERE DECISION = 'BLOCK'"
).fetchone()[0]
flagged = conn.execute(
    "SELECT COUNT(*) FROM SENTINEL.AUDIT_LOG WHERE DECISION = 'FLAG'"
).fetchone()[0]

col1.metric("Total prompts", total)
col2.metric("Blocked", blocked)
col3.metric("Flagged", flagged)

st.subheader("Attack category breakdown")
cat_rows = conn.execute(
    """
    SELECT MATCHED_CATEGORY, COUNT(*) AS CNT
    FROM SENTINEL.AUDIT_LOG
    WHERE DECISION IN ('BLOCK', 'FLAG')
    GROUP BY MATCHED_CATEGORY
    ORDER BY CNT DESC
    """
).fetchall()
if cat_rows:
    df_cat = pd.DataFrame(cat_rows, columns=["Category", "Count"])
    st.bar_chart(df_cat.set_index("Category"))
else:
    st.write("No blocked/flagged prompts yet — send some traffic through the proxy.")

st.subheader("Live audit log (most recent 50)")
rows = conn.execute(
    """
    SELECT TS, SESSION_ID, PROMPT, DECISION, MATCHED_CATEGORY,
           HEURISTIC_SCORE, SIMILARITY_SCORE, LATENCY_MS
    FROM SENTINEL.AUDIT_LOG
    ORDER BY TS DESC
    LIMIT 50
    """
).fetchall()
df = pd.DataFrame(
    rows,
    columns=[
        "Time", "Session", "Prompt", "Decision", "Category",
        "Heuristic", "Similarity", "Latency (ms)",
    ],
)
st.dataframe(df, use_container_width=True)

st.caption("Replay: pick a session ID above, filter, and walk through it live during your demo.")
