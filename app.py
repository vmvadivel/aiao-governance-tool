import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import time

# --- SYSTEM SETTINGS ---
st.set_page_config(page_title="AIAO | Governance Portal", layout="wide")

# This allows us to clear the cache and "pull" new data
def refresh_callback():
    st.cache_data.clear()

@st.cache_data
def get_fleet_telemetry(is_stressed=False):
    """Simulates real-time pull from Model Registry API"""
    n = 250
    depts = ['Commercial', 'Risk/Legal', 'Operations', 'Product']
    
    # If 'Stress Test' is on, we make the data look worse (higher latency, lower compliance)
    latency_min = 600 if is_stressed else 200
    compliance_min = 0.5 if is_stressed else 0.75
    
    data = pd.DataFrame({
        "agent_id": [f"ID-{1000+i}" for i in range(n)],
        "dept": [np.random.choice(depts) for _ in range(n)],
        "status": [np.random.choice(['Healthy', 'Flagged', 'Critical'], p=[0.8, 0.15, 0.05]) for _ in range(n)],
        "compliance_score": np.random.uniform(compliance_min, 1.0, n),
        "latency": np.random.randint(latency_min, 900, n),
        "tokens_24h": np.random.randint(5000, 500000, n)
    })
    
    # Ensure 'Critical' status matches poor compliance scores for realism
    data.loc[data['compliance_score'] < 0.78, 'status'] = 'Critical'
    return data

def main():
    # --- SIDEBAR CONTROLS ---
    st.sidebar.title("🛠️ Admin Controls")
    st.sidebar.button("🔄 Refresh Fleet Data", on_click=refresh_callback)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Simulation Settings")
    stress_test = st.sidebar.toggle("Simulate System Stress", help="Artificially increases latency and risk across the fleet.")
    
    if stress_test:
        st.sidebar.warning("STRESS MODE ACTIVE")

    # --- MAIN DASHBOARD ---
    st.title("🛡️ AIAO Governance Control Plane")
    st.caption(f"Enterprise AI Fleet Monitoring | Last Heartbeat: {datetime.now().strftime('%H:%M:%S')} UTC")
    
    # Load Data
    with st.spinner('Syncing with Agent Registry...'):
        data = get_fleet_telemetry(is_stressed=stress_test)
        if not stress_test:
            time.sleep(0.5) # Fake network delay for a "human" feel

    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Active Fleet", len(data))
    k2.metric("Compliance Avg", f"{data['compliance_score'].mean():.1%}")
    k3.metric("Critical Alerts", len(data[data['status'] == 'Critical']), 
              delta="Live" if not stress_test else "DANGER", delta_color="inverse")

    st.markdown("---")

    # Visuals
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Performance vs. Compliance Matrix")
        fig = px.scatter(data, x="latency", y="compliance_score", color="status",
                         hover_data=['agent_id', 'dept'],
                         color_discrete_map={'Healthy': '#2ecc71', 'Flagged': '#f1c40f', 'Critical': '#e74c3c'},
                         template="plotly_dark") # Looks very "Command Center"
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Security Event Log")
        critical_hits = data[data['status'] == 'Critical'].head(3)
        if not critical_hits.empty:
            for _, row in critical_hits.iterrows():
                st.error(f"**{row['agent_id']}** ({row['dept']})\n\nViolation: Ethical Guardrail Triggered.")
        else:
            st.success("No active critical violations.")

    # Table
    with st.expander("View Full Agent Registry"):
        st.dataframe(data, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
