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
st.markdown("Three source systems compute the same metric differently:")

col1, col2, col3 = st.columns(3)

# VGS Card
with col1:
    vgs_value = results.get("VGS")
    if vgs_value is not None:
        caption_text = ""
        if selected_metric == "Supplier On-Time Delivery Rate":
            caption_text = "Excludes partial deliveries. Uses own delivery timestamps."
        elif selected_metric == "Negotiated Savings":
            caption_text = "Uses prior contract price. Extrapolates volume from contract value."
        elif selected_metric == "Active Contract Value":
            caption_text = "Includes amendments. Shows total contract value."
        
        value_str = f"{vgs_value:,.2f}" if isinstance(vgs_value, (int, float)) else str(vgs_value)
        if selected_metric == "Supplier On-Time Delivery Rate":
            value_display = f"{value_str}%"
        else:
            value_display = f"${value_str}"
        
        card_html = f'''
        <div class="metric-card vgs-card">
            <h3>VGS System</h3>
            <p><strong>Supplier Governance</strong></p>
            <div style="font-size: 2rem; font-weight: 700; margin: 1rem 0;">{value_display}</div>
            <p style="font-size: 0.9rem; color: #999; margin-top: 0.5rem;">{caption_text}</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        card_html = '''
        <div class="metric-card na-card">
            <h3>VGS System</h3>
            <p><strong>N/A</strong></p>
            <p style="font-size: 0.9rem; color: #999;">This system does not track this metric.</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)

# VPC Card
with col2:
    vpc_value = results.get("VPC")
    if vpc_value is not None:
        caption_text = ""
        if selected_metric == "Supplier On-Time Delivery Rate":
            caption_text = "N/A - VPC does not track delivery performance."
        elif selected_metric == "Negotiated Savings":
            caption_text = "Uses list price as baseline. Inflated savings calculation."
        elif selected_metric == "Active Contract Value":
            caption_text = "Original value only. Does not include amendments."
        
        value_str = f"{vpc_value:,.2f}" if isinstance(vpc_value, (int, float)) else str(vpc_value)
        if selected_metric == "Supplier On-Time Delivery Rate":
            value_display = f"{value_str}%"
        else:
            value_display = f"${value_str}"
        
        card_html = f'''
        <div class="metric-card vpc-card">
            <h3>VPC System</h3>
            <p><strong>Price/Cost Management</strong></p>
            <div style="font-size: 2rem; font-weight: 700; margin: 1rem 0;">{value_display}</div>
            <p style="font-size: 0.9rem; color: #999; margin-top: 0.5rem;">{caption_text}</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        card_html = '''
        <div class="metric-card na-card">
            <h3>VPC System</h3>
            <p><strong>N/A</strong></p>
            <p style="font-size: 0.9rem; color: #999;">This system does not track this metric.</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)

# SI+ Card
with col3:
    si_value = results.get("SI+")
    if si_value is not None:
        caption_text = ""
        if selected_metric == "Supplier On-Time Delivery Rate":
            caption_text = "Counts partial deliveries as on-time. Uses own receipt timestamps."
        elif selected_metric == "Negotiated Savings":
            caption_text = "N/A - SI+ does not track savings."
        elif selected_metric == "Active Contract Value":
            caption_text = "Tracks committed spend, not contract value. Different concept."
        
        value_str = f"{si_value:,.2f}" if isinstance(si_value, (int, float)) else str(si_value)
        if selected_metric == "Supplier On-Time Delivery Rate":
            value_display = f"{value_str}%"
        else:
            value_display = f"${value_str}"
        
        card_html = f'''
        <div class="metric-card si-card">
            <h3>SI+ System</h3>
            <p><strong>Implementation Tracking</strong></p>
            <div style="font-size: 2rem; font-weight: 700; margin: 1rem 0;">{value_display}</div>
            <p style="font-size: 0.9rem; color: #999; margin-top: 0.5rem;">{caption_text}</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        card_html = '''
        <div class="metric-card na-card">
            <h3>SI+ System</h3>
            <p><strong>N/A</strong></p>
            <p style="font-size: 0.9rem; color: #999;">This system does not track this metric.</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)

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
        inclusions_html = "".join([f"<li>{inc}</li>" for inc in metric_def['inclusions']])
        exclusions_html = "".join([f"<li>{exc}</li>" for exc in metric_def['exclusions']])
        
        definition_html = f'''
        <div class="definition-card">
            <h3>{metric_def['name']}</h3>
            <p><strong>{metric_def['description']}</strong></p>
            <hr style="border: 1px solid #444; margin: 1rem 0;">
            <p><strong>Formula:</strong> <code>{metric_def['formula']}</code></p>
            <p><strong>Grain:</strong> {metric_def['grain']}</p>
            <p><strong>Time Logic:</strong> {metric_def['time_logic']}</p>
            <p><strong>Owner:</strong> {metric_def['owner']}</p>
            <p><strong>Inclusions:</strong></p>
            <ul>{inclusions_html}</ul>
            <p><strong>Exclusions:</strong></p>
            <ul>{exclusions_html}</ul>
        </div>
        '''
        st.markdown(definition_html, unsafe_allow_html=True)

with col_right:
    governed_value = results.get("Governed")
    if governed_value is not None:
        if isinstance(governed_value, (int, float)):
            if selected_metric == "Supplier On-Time Delivery Rate":
                value_display = f"{governed_value:.2f}%"
            else:
                value_display = f"${governed_value:,.2f}"
        else:
            value_display = str(governed_value)
        
        governed_html = f'''
        <div class="governed-metric">
            <h3>Certified Value</h3>
            <p style="font-size: 0.9rem; color: #999; margin-bottom: 0.5rem;">Governed Metric</p>
            <div style="font-size: 2.5rem; font-weight: 700; color: #27AE60; margin: 1rem 0;">{value_display}</div>
        </div>
        '''
        st.markdown(governed_html, unsafe_allow_html=True)

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
