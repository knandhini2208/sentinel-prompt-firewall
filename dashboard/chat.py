import uuid
import requests
import streamlit as st

st.set_page_config(page_title="Sentinel Chat", layout="centered")
st.title("Sentinel — Try it live")

PROXY_URL = "http://127.0.0.1:8001/chat"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "history" not in st.session_state:
    st.session_state.history = []

badge = {"ALLOW": "🟢 ALLOW", "FLAG": "🟡 FLAG", "BLOCK": "🔴 BLOCK"}

for msg in st.session_state.history:
    with st.chat_message("user"):
        st.write(msg["prompt"])
    with st.chat_message("assistant"):
        st.write(msg["response"])
        st.caption(
            f"{badge.get(msg['decision'], msg['decision'])} · "
            f"category: {msg['matched_category']} · "
            f"heuristic: {msg['heuristic_score']} · "
            f"similarity: {msg['similarity_score']} · "
            f"{msg['latency_ms']}ms"
        )

prompt = st.chat_input("Type a message (try a normal question, or a jailbreak attempt)")

if prompt:
    try:
        resp = requests.post(
            PROXY_URL,
            json={"session_id": st.session_state.session_id, "prompt": prompt},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        st.error(f"Could not reach the proxy at {PROXY_URL}. Is it running? ({e})")
        st.stop()

    st.session_state.history.append(
        {
            "prompt": prompt,
            "response": data["response"],
            "decision": data["decision"],
            "matched_category": data["matched_category"],
            "heuristic_score": data["heuristic_score"],
            "similarity_score": data["similarity_score"],
            "latency_ms": data["latency_ms"],
        }
    )
    st.rerun()