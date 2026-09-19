import streamlit as st
from datetime import datetime
from guardrail import guardrail_check
import time
import pandas as pd

st.set_page_config(page_title="AI Guardrail Control Center", layout="wide")

if "logs" not in st.session_state:
    st.session_state.logs = []

st.title("The AI Safety Hub")
st.caption("A Simple, Tiered Security for Chatbots")

total_checks = len(st.session_state.logs)
blocked_count = sum(1 for log in st.session_state.logs if log["blocked"])

if st.session_state.logs:
    avg_latency = f"{round(sum(l['latency'] for l in st.session_state.logs) / len(st.session_state.logs))}ms"
else:
    avg_latency = "—"

col1, col2, col3 = st.columns(3)
col1.metric("Total Requests", total_checks)
col2.metric("Threats Blocked", blocked_count)
col3.metric("Avg. Latency", avg_latency)

st.divider()

left, right = st.columns(2)

# 1. Capture User Input on the Left
with left:
    st.subheader("Input")
    user_input = st.text_area("Type a message to test:", height=150, key="guardrail_user_input")
    check_button = st.button("Run Guardrail Check", type="primary")

# 2. Process and Render Results on the Right
with right:
    st.subheader("Result")
    
    if check_button and user_input.strip():
        start_time = time.time()
        result = guardrail_check(user_input)
        latency_ms = round((time.time() - start_time) * 1000)

        st.session_state.logs.insert(0, {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "input": user_input,
            "language": result["detected_language"],
            "blocked": result["blocked"],
            "layer": result.get("triggered_layer"),
            "latency": latency_ms,
        })

        if result["blocked"]:
            st.error(f"🔴 BLOCKED: caught by {result.get('triggered_layer')}")
        else:
            st.success("🟢 PASSED")

        st.write(f"**Detected language:** {result['detected_language']}")
        if result["translated_text"] != user_input:
            st.write(f"**Translated:** {result['translated_text']}")
        if result.get("confidence") is not None:
            st.write(f"**ML confidence:** {result['confidence']}")
        st.write(f"**Latency:** {latency_ms}ms")
        
    elif check_button:
        st.warning("Type something first.")

st.divider()
st.subheader("Security Pipeline Visualizer")

p1, p2, p3 = st.columns(3)

if st.session_state.logs:
    last = st.session_state.logs[0]
    layer_triggered = last["layer"]
else:
    last = None
    layer_triggered = None

with p1:
    st.markdown("**Layer 1: Normalizer**")
    if last:
        st.info(f"Detected: {last['language']}")
    else:
        st.write("Waiting for input...")

with p2:
    st.markdown("**Layer 2: Rule Matcher**")
    if layer_triggered == "Layer 2 (Regex)":
        st.error("BLOCKED here")
    elif last:
        st.success("Passed")
    else:
        st.write("Waiting for input...")

with p3:
    st.markdown("**Layer 3: ML Classifier**")
    if layer_triggered == "Layer 3 (ML)":
        st.error("BLOCKED here")
    elif layer_triggered == "Layer 2 (Regex)":
        st.write("Bypassed (blocked earlier)")
    elif last:
        st.success("Passed")
    else:
        st.write("Waiting for input...")

st.divider()
st.subheader("Recent Security Events")

if st.session_state.logs:
    df_logs = pd.DataFrame(st.session_state.logs[:10])
    df_logs["blocked"] = df_logs["blocked"].map({True: "🔴 BLOCKED", False: "🟢 PASSED"})
    st.dataframe(
        df_logs[["timestamp", "input", "language", "blocked", "layer"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.write("No events yet, run a check above.")
