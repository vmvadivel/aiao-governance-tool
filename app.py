import time
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from datetime import datetime
from typing import Optional

# --- CONFIG & CONSTANTS ---
# Always set page config first to avoid the "layout shift" glitch
st.set_page_config(
    page_title="AIAO | Governance Control Plane", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define our color palette here so it's easy to tweak later (DRY principle)
STATUS_COLORS = {
    'Healthy': '#2ecc71',  # Green
    'Flagged': '#f1c40f',  # Yellow
    'Critical': '#e74c3c'  # Red
}

# --- BACKEND LOGIC ---
def clear_cache_callback():
    """
    Clears the cache. Used when the user hits the 'Refresh' button to force a fresh data pull.
    """
    st.cache_data.clear()

@st.cache_data(ttl=60) # Cache this for 60s so we don't hit the "API" on every UI click
def get_fleet_telemetry(is_stressed: bool = False, n_agents: int = 250) -> pd.DataFrame:
    """
    Simulates a connection to the Model Registry (e.g., MLflow/Databricks). Generates synthetic telemetry for the demo.
    """
    
    # Departments we want to monitor
    depts = ['Commercial', 'Risk/Legal', 'Operations', 'Product']
    
    # Adjust thresholds based on the 'Stress Mode' toggle
    # If stressed, we lower the floor for compliance and bump up latency
    latency_floor = 600 if is_stressed else 200
    compliance_floor = 0.50 if is_stressed else 0.75
    
    # Generate the fleet data using numpy (much faster than looping)
    data = pd.DataFrame({
        "agent_id": [f"ID-{1000+i}" for i in range(n_agents)],
        "dept": np.random.choice(depts, n_agents),
        # Default mostly to Healthy, sprinkle in some trouble
        "status": np.random.choice(['Healthy', 'Flagged', 'Critical'], 
                                   n_agents, 
                                   p=[0.8, 0.15, 0.05]),
        "compliance_score": np.random.uniform(compliance_floor, 1.0, n_agents),
        "latency": np.random.randint(latency_floor, 900, n_agents),
        "tokens_24h": np.random.randint(5000, 500000, n_agents)
    })
    
    # Business Logic: If compliance is trash, force the status to 'Critical'
    # This prevents logical inconsistencies in the visual
    data.loc[data['compliance_score'] < 0.78, 'status'] = 'Critical'
    
    return data

# --- FRONTEND UI ---

def main():
    # Sidebar Controls for Admin option
    with st.sidebar:
        st.title("🛠️ Admin Controls")
        
        # The 'Refresh' button mimics a live API poll
        st.button("🔄 Refresh Fleet Data", on_click=clear_cache_callback)
        st.markdown("---")
        
        st.subheader("Simulation Settings")
        # Using a checkbox is safer than toggle for older Streamlit versions
        stress_test = st.checkbox("Simulate System Stress", value=False)
        
        if stress_test:
            st.warning("STRESS MODE ACTIVE")
            st.caption("Injecting high latency & compliance failures.")

    st.title("🛡️ AIAO Governance Control Plane")
    
    # Dynamic timestamp makes it feel "live"
    last_update = datetime.now().strftime('%H:%M:%S UTC')
    st.caption(f"Enterprise AI Fleet Monitoring | Last Heartbeat: {last_update}")
    
    # Data Loading
    with st.spinner('Syncing with Agent Registry...'):
        # Fetch data (cached unless arguments change)
        df = get_fleet_telemetry(is_stressed=stress_test)
        
        # Add a tiny fake delay if we aren't stressed, just to make the 
        # "loading" spinner visible for a split second (UX trick)
        if not stress_test:
            time.sleep(0.4)

    # Top Level KPIs
    # Create 3 columns for metrics
    k1, k2, k3 = st.columns(3)
    
    k1.metric("Active Fleet", len(df))
    
    avg_compliance = df['compliance_score'].mean()
    k2.metric("Compliance Avg", f"{avg_compliance:.1%}")
    
    critical_count = len(df[df['status'] == 'Critical'])
    k3.metric(
        "Critical Alerts", 
        critical_count, 
        delta="Stable" if not stress_test else "DANGER", 
        delta_color="inverse" # Automatically turns red if delta is negative/danger
    )

    st.markdown("---")

    # The Command Center Layout
    # Split screen: Chart takes 2/3rds, Logs take 1/3rd
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.subheader("Performance vs. Compliance Matrix")
        
        # Plotly Scatter - The hero visual
        fig = px.scatter(
            df, 
            x="latency", 
            y="compliance_score", 
            color="status",
            hover_data=['agent_id', 'dept'],
            color_discrete_map=STATUS_COLORS, # Use constant from top
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("Security Event Log")
    
        # Define a list of realistic AI violations
        VIOLATION_TYPES = [
            "PII Leak: Potential SSN detected in output.",
            "Toxicity: Negative sentiment threshold exceeded.",
            "Hallucination: Grounding score below 0.4.",
            "Compliance: Unauthorized financial advice detected.",
            "Security: Potential source code injection attempt."
        ]
    
        critical_hits = df[df['status'] == 'Critical'].head(3)
    
        if not critical_hits.empty:
            for _, row in critical_hits.iterrows():
                # Randomly pick a violation for each row so it looks authentic
                reason = np.random.choice(VIOLATION_TYPES)
            
                st.error(
                    f"**{row['agent_id']}** ({row['dept']})\n\n"
                    f"**Violation:** {reason}"
                )
        else:
            st.success("✅ No active critical violations.")

    # Raw Data View (Hidden by default to keep UI clean)
    with st.expander("View Full Agent Registry"):
        st.dataframe(df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
