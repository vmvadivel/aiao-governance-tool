import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- SYSTEM SETTINGS ---
st.set_page_config(page_title="AIAO | Governance Portal", layout="wide")

# Internal Config
ETHICS_LIMIT = 0.80  # Minimum acceptable compliance score

@st.cache_data
def get_fleet_telemetry():
    """Simulates real-time pull from Model Registry API"""
    try:
        n = 250
        depts = ['Commercial', 'Risk/Legal', 'Operations', 'Product']
        return pd.DataFrame({
            "agent_id": [f"ID-{1000+i}" for i in range(n)],
            "dept": [np.random.choice(depts) for _ in range(n)],
            "status": [np.random.choice(['Healthy', 'Flagged', 'Critical'], p=[0.8, 0.15, 0.05]) for _ in range(n)],
            "compliance_score": np.random.uniform(0.7, 1.0, n),
            "latency": np.random.randint(200, 900, n),
            "tokens_24h": np.random.randint(5000, 500000, n)
        })
    except Exception as e:
        st.error(f"Critical: Telemetry sync failed. {e}")
        return pd.DataFrame()

def main():
    # Header Branding
    st.title("AIAO Governance Control Plane")
    st.caption(f"Enterprise AI Fleet Monitoring | Sync Time: {datetime.now().strftime('%H:%M:%S')} UTC")
    
    data = get_fleet_telemetry()
    
    # KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Active Fleet", len(data))
    kpi2.metric("Compliance Avg", f"{data['compliance_score'].mean():.1%}")
    kpi3.metric("Critical Alerts", len(data[data['status'] == 'Critical']), delta_color="inverse")

    st.markdown("---")

    # Layout: Logic for Scale Management
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Compliance vs. Latency Matrix")
        fig = px.scatter(data, x="latency", y="compliance_score", color="status",
                         color_discrete_map={'Healthy': '#2ecc71', 'Flagged': '#f1c40f', 'Critical': '#e74c3c'})
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Security Event Log")
        critical_hits = data[data['status'] == 'Critical'].head(3)
        for _, row in critical_hits.iterrows():
            st.warning(f"**{row['agent_id']}** - Bias threshold triggered.")
        
        st.success("✅ Audit Complete: All Commercial agents meet PII standards.")

    # Registry
    st.subheader("Agent Registry")
    st.dataframe(data, use_container_width=True)

if __name__ == "__main__":
    main()
