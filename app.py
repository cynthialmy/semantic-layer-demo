"""
Metric Trust Explorer - Semantic Layer Demo
Demonstrates why defining metrics once matters at enterprise scale.
"""

import streamlit as st
import pandas as pd
from engine.loaders import load_system_data, get_metric_by_name
from engine.compute import compute_metric_per_system, get_supplier_flags
from engine.lineage import create_lineage_diagram

# Page config
st.set_page_config(
    page_title="Metric Trust Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
import os
css_path = os.path.join(os.path.dirname(__file__), "style", "custom.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = load_system_data()

# Sidebar
st.sidebar.title("Filters")
st.sidebar.markdown("---")

metric_options = [
    "Supplier On-Time Delivery Rate",
    "Negotiated Savings",
    "Active Contract Value"
]

selected_metric = st.sidebar.radio(
    "Select Metric",
    metric_options,
    index=0
)

quarter_options = ["All", "Q1", "Q2", "Q3", "Q4"]
selected_quarter = st.sidebar.selectbox("Quarter", quarter_options, index=0)
quarter_filter = None if selected_quarter == "All" else selected_quarter

region_options = ["All", "Europe", "Asia", "Americas", "Other"]
selected_regions = st.sidebar.multiselect("Region", region_options, default=["All"])
region_filter = None if "All" in selected_regions or len(selected_regions) == 0 else selected_regions

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown(
    "This demo illustrates how different source systems compute the same metric differently, "
    "and how a semantic layer provides a single source of truth."
)

# Header
st.title("📊 Metric Trust Explorer")
st.markdown("### Why defining metrics once matters at enterprise scale")
st.markdown("---")

# Compute metrics
results = compute_metric_per_system(
    selected_metric,
    st.session_state.data,
    quarter_filter,
    region_filter
)

# Panel 1: The Problem
st.header("🔴 The Problem")
st.markdown(f"**Metric:** {selected_metric}")
st.markdown("Three source systems compute the same metric differently:")

col1, col2, col3 = st.columns(3)

# VGS Card
with col1:
    vgs_value = results.get("VGS")
    if vgs_value is not None:
        st.markdown(f'<div class="metric-card vgs-card">', unsafe_allow_html=True)
        st.markdown(f"**{selected_metric}**")
        st.markdown("### VGS System")
        st.markdown("**Supplier Governance**")
        st.metric("Value", f"{vgs_value:,.2f}" if isinstance(vgs_value, (int, float)) else str(vgs_value))

        if selected_metric == "Supplier On-Time Delivery Rate":
            st.caption("Excludes partial deliveries. Uses own delivery timestamps.")
        elif selected_metric == "Negotiated Savings":
            st.caption("Uses prior contract price. Extrapolates volume from contract value.")
        elif selected_metric == "Active Contract Value":
            st.caption("Includes amendments. Shows total contract value.")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-card na-card">', unsafe_allow_html=True)
        st.markdown("### VGS System")
        st.markdown("**N/A**")
        st.caption("This system does not track this metric.")
        st.markdown('</div>', unsafe_allow_html=True)

# VPC Card
with col2:
    vpc_value = results.get("VPC")
    if vpc_value is not None:
        st.markdown(f'<div class="metric-card vpc-card">', unsafe_allow_html=True)
        st.markdown(f"**{selected_metric}**")
        st.markdown("### VPC System")
        st.markdown("**Price/Cost Management**")
        st.metric("Value", f"{vpc_value:,.2f}" if isinstance(vpc_value, (int, float)) else str(vpc_value))

        if selected_metric == "Supplier On-Time Delivery Rate":
            st.caption("N/A - VPC does not track delivery performance.")
        elif selected_metric == "Negotiated Savings":
            st.caption("Uses list price as baseline. Inflated savings calculation.")
        elif selected_metric == "Active Contract Value":
            st.caption("Original value only. Does not include amendments.")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-card na-card">', unsafe_allow_html=True)
        st.markdown("### VPC System")
        st.markdown("**N/A**")
        st.caption("This system does not track this metric.")
        st.markdown('</div>', unsafe_allow_html=True)

# SI+ Card
with col3:
    si_value = results.get("SI+")
    if si_value is not None:
        st.markdown(f'<div class="metric-card si-card">', unsafe_allow_html=True)
        st.markdown(f"**{selected_metric}**")
        st.markdown("### SI+ System")
        st.markdown("**Implementation Tracking**")
        st.metric("Value", f"{si_value:,.2f}" if isinstance(si_value, (int, float)) else str(si_value))

        if selected_metric == "Supplier On-Time Delivery Rate":
            st.caption("Counts partial deliveries as on-time. Uses own receipt timestamps.")
        elif selected_metric == "Negotiated Savings":
            st.caption("N/A - SI+ does not track savings.")
        elif selected_metric == "Active Contract Value":
            st.caption("Tracks committed spend, not contract value. Different concept.")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-card na-card">', unsafe_allow_html=True)
        st.markdown("### SI+ System")
        st.markdown("**N/A**")
        st.caption("This system does not track this metric.")
        st.markdown('</div>', unsafe_allow_html=True)

# Show delta
values = [v for v in [results.get("VGS"), results.get("VPC"), results.get("SI+")] if v is not None]
if len(values) > 1:
    max_val = max(values)
    min_val = min(values)
    if isinstance(max_val, (int, float)) and isinstance(min_val, (int, float)):
        if selected_metric == "Supplier On-Time Delivery Rate":
            delta_pct = abs(max_val - min_val)
            st.warning(f"⚠️ **These systems disagree by {delta_pct:.1f} percentage points.**")
        else:
            delta_pct = abs((max_val - min_val) / min_val * 100) if min_val > 0 else 0
            st.warning(f"⚠️ **These systems disagree by {delta_pct:.1f}%.**")

st.markdown("---")

# Panel 2: The Semantic Layer
st.header("✅ The Semantic Layer")
st.markdown("A governed metric definition provides a single source of truth:")

col_left, col_right = st.columns([1, 1])

with col_left:
    metric_def = get_metric_by_name(selected_metric)
    if metric_def:
        st.markdown(f'<div class="definition-card">', unsafe_allow_html=True)
        st.markdown(f"### {metric_def['name']}")
        st.markdown(f"**{metric_def['description']}**")
        st.markdown("---")
        st.markdown(f"**Formula:** `{metric_def['formula']}`")
        st.markdown(f"**Grain:** {metric_def['grain']}")
        st.markdown(f"**Time Logic:** {metric_def['time_logic']}")
        st.markdown(f"**Owner:** {metric_def['owner']}")

        st.markdown("**Inclusions:**")
        for inc in metric_def['inclusions']:
            st.markdown(f"- {inc}")

        st.markdown("**Exclusions:**")
        for exc in metric_def['exclusions']:
            st.markdown(f"- {exc}")

        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    governed_value = results.get("Governed")
    if governed_value is not None:
        st.markdown(f'<div class="governed-metric">', unsafe_allow_html=True)
        st.markdown("### Certified Value")
        if isinstance(governed_value, (int, float)):
            if selected_metric == "Supplier On-Time Delivery Rate":
                st.metric("Governed Metric", f"{governed_value:.2f}%", delta=None)
            else:
                st.metric("Governed Metric", f"${governed_value:,.2f}", delta=None)
        else:
            st.metric("Governed Metric", str(governed_value), delta=None)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### Lineage")
        lineage_diagram = create_lineage_diagram(selected_metric)
        st.graphviz_chart(lineage_diagram.source)

st.markdown("---")

# Panel 3: Why It Matters
st.header("💡 Why It Matters")
st.markdown("Different numbers lead to different decisions:")

# Simulate supplier flagging
if selected_metric == "Supplier On-Time Delivery Rate":
    threshold = 85.0  # Flag suppliers below 85% on-time rate

    vgs_flags = get_supplier_flags(selected_metric, st.session_state.data, threshold, quarter_filter, region_filter)

    # Simulate what each system would flag
    # For demo purposes, we'll use approximations
    if results.get("VGS") is not None and results.get("SI+") is not None:
        vgs_rate = results.get("VGS")
        si_rate = results.get("SI+")
        governed_rate = results.get("Governed")

        # Estimate flags based on rates (simplified)
        total_suppliers = 20
        vgs_flagged = int(total_suppliers * (1 - vgs_rate / 100)) if vgs_rate < threshold else 0
        si_flagged = int(total_suppliers * (1 - si_rate / 100)) if si_rate < threshold else 0
        governed_flagged = int(total_suppliers * (1 - governed_rate / 100)) if governed_rate and governed_rate < threshold else 0

        comparison_df = pd.DataFrame({
            "System": ["VGS", "SI+", "Semantic Layer"],
            "Suppliers Flagged": [vgs_flagged, si_flagged, governed_flagged],
            "Reasoning": [
                "Excludes partial deliveries → more strict → flags more suppliers",
                "Counts partials as on-time → more lenient → flags fewer suppliers",
                "Governed definition with documented exclusions → balanced, audit-ready"
            ]
        })

        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        st.markdown("""
        **Impact:**
        - Using VGS numbers: **12 suppliers** flagged for review (may include false positives)
        - Using SI+ numbers: **4 suppliers** flagged (may miss real issues)
        - Using semantic layer: **8 suppliers** flagged with documented reasoning for each inclusion/exclusion

        The semantic layer ensures decisions are based on consistent, traceable logic rather than which system a stakeholder happens to query.
        """)

elif selected_metric == "Negotiated Savings":
    st.markdown("""
    **Impact:**
    - Using VGS numbers: Savings appear lower (extrapolated volume, no current price data)
    - Using VPC numbers: Savings appear inflated (uses list price instead of prior contract price)
    - Using semantic layer: Accurate savings based on actual prior vs. current pricing

    In quarterly business reviews, conflicting savings numbers lead to debates about methodology rather than decisions about supplier performance. The semantic layer eliminates this friction.
    """)

elif selected_metric == "Active Contract Value":
    st.markdown("""
    **Impact:**
    - Using VGS numbers: Includes amendments → higher value (more accurate for financial planning)
    - Using VPC numbers: Original value only → lower value (misses contract changes)
    - Using SI+ numbers: Committed spend → different concept entirely (not comparable)

    Procurement directors need accurate contract values for budget planning. The semantic layer ensures they're looking at the same number whether they query VGS, VPC, or a procurement AI assistant.
    """)

st.markdown("---")

# Footer
st.markdown("""
<div class="footer">
<p><strong>Built by Cynthia Mengyuan Li</strong> | <a href="https://cynthialmy.github.io" target="_blank">Portfolio</a></p>
<p>This demo illustrates concepts from <a href="https://cynthialmy.github.io/2025/02/13/semantic-layer-bi-product.html" target="_blank">Building a Semantic-Layer-Driven BI Product</a></p>
</div>
""", unsafe_allow_html=True)
