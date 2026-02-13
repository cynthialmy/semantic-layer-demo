"""
Metric Trust Explorer - Semantic Layer Demo
Interactive companion to "Building a Semantic-Layer-Driven BI Product"
Shows how a governed semantic layer resolves metric inconsistencies across source systems.
"""

import streamlit as st
import pandas as pd
from engine.loaders import load_system_data, get_metric_by_name
from engine.compute import compute_metric_per_system, get_supplier_flags
from engine.lineage import create_lineage_diagram

# Page config
st.set_page_config(
    page_title="Metric Trust Explorer | Semantic Layer Demo",
    page_icon="🔍",
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

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sidebar-header">
    <div style="font-size: 1.4rem; font-weight: 700; margin-bottom: 0.25rem;">Metric Trust Explorer</div>
    <div style="font-size: 0.85rem; opacity: 0.7;">Semantic Layer Demo</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Guide
st.sidebar.markdown("#### How to read this demo")
st.sidebar.markdown(
    "Pick a procurement metric below. The demo shows how **three different source systems** "
    "compute that metric using different logic, then how a **governed semantic layer** "
    "resolves the inconsistency into a single certified answer."
)

st.sidebar.markdown("---")

# Metric selection with descriptions
metric_options = {
    "Supplier On-Time Delivery Rate": "Are suppliers delivering on time? VGS and SI+ disagree because they handle partial deliveries differently.",
    "Negotiated Savings": "How much did we save through negotiation? VGS and VPC use different price baselines.",
    "Active Contract Value": "What is the total value of active contracts? Systems disagree on whether to include amendments."
}

selected_metric = st.sidebar.radio(
    "Choose a procurement metric",
    list(metric_options.keys()),
    index=0,
    help="Each metric demonstrates a different type of inconsistency across source systems."
)

st.sidebar.markdown(
    f'<div class="sidebar-metric-hint">{metric_options[selected_metric]}</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# Filters
st.sidebar.markdown("#### Narrow the data")

quarter_options = ["All Quarters", "Q1", "Q2", "Q3", "Q4"]
selected_quarter = st.sidebar.selectbox("Quarter", quarter_options, index=0)
quarter_filter = None if selected_quarter == "All Quarters" else selected_quarter

region_options = ["All Regions", "Europe", "Asia", "Americas", "Other"]
selected_regions = st.sidebar.multiselect("Region", region_options, default=["All Regions"])
region_filter = None if "All Regions" in selected_regions or len(selected_regions) == 0 else selected_regions

st.sidebar.markdown("---")

# Context: What are these systems?
st.sidebar.markdown("#### The three source systems")
st.sidebar.markdown("""
**VGS** — Supplier Governance
Manages contracts, compliance, delivery agreements

**VPC** — Price & Cost Management
Tracks pricing, volumes, cost benchmarks

**SI+** — Implementation Tracking
Records delivery receipts, implementation status
""")

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<div class="sidebar-synthetic-notice">'
    'All data shown is <strong>synthetic</strong> — generated to illustrate metric inconsistencies. '
    'No real company data is used.'
    '</div>',
    unsafe_allow_html=True
)


# ──────────────────────────────────────────────
# Main content
# ──────────────────────────────────────────────

# Hero section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Metric Trust Explorer</h1>
    <p class="hero-subtitle">What happens when three systems define the same metric differently?</p>
    <p class="hero-description">
        This interactive demo accompanies
        <a href="https://cynthialmy.github.io/2026/02/13/semantic-layer-bi-product.html" target="_blank">Building a Semantic-Layer-Driven BI Product</a>.
        It shows how a <strong>semantic layer</strong> resolves metric inconsistencies
        by defining each metric once, with precise business logic, and computing a single certified answer.
    </p>
</div>
""", unsafe_allow_html=True)

# Synthetic data banner
st.markdown("""
<div class="synthetic-banner">
    All data in this demo is synthetic. The three source systems (VGS, VPC, SI+) and their
    procurement records are generated to illustrate how metric definitions diverge across
    real enterprise environments. No actual company data is used.
</div>
""", unsafe_allow_html=True)

# Step indicator
st.markdown("""
<div class="step-indicator">
    <div class="step-item">
        <div class="step-number step-problem">1</div>
        <div class="step-label">See the inconsistency</div>
    </div>
    <div class="step-arrow">→</div>
    <div class="step-item">
        <div class="step-number step-solution">2</div>
        <div class="step-label">See the governed definition</div>
    </div>
    <div class="step-arrow">→</div>
    <div class="step-item">
        <div class="step-number step-impact">3</div>
        <div class="step-label">See the business impact</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Compute metrics
results = compute_metric_per_system(
    selected_metric,
    st.session_state.data,
    quarter_filter,
    region_filter
)


# ──────────────────────────────────────────────
# Step 1: The Inconsistency
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="section-header">
    <span class="section-number problem-bg">1</span>
    <div>
        <h2 style="margin: 0;">The Inconsistency</h2>
        <p class="section-desc">Three source systems compute <strong>{metric}</strong> using different logic. Each number below is technically correct within its own system — but they tell conflicting stories.</p>
    </div>
</div>
""".format(metric=selected_metric), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# VGS Card
with col1:
    vgs_value = results.get("VGS")
    if vgs_value is not None:
        caption_text = ""
        methodology = ""
        if selected_metric == "Supplier On-Time Delivery Rate":
            methodology = "Excludes partial deliveries"
            caption_text = "Uses own delivery timestamps and agreed windows. Partial deliveries are excluded entirely."
        elif selected_metric == "Negotiated Savings":
            methodology = "Extrapolates volume from contracts"
            caption_text = "Has prior contract price but no volume data. Estimates volume from contract value, then assumes 10% savings."
        elif selected_metric == "Active Contract Value":
            methodology = "Includes amendments"
            caption_text = "Sums original contract value plus all amendments for active contracts."

        value_str = f"{vgs_value:,.2f}" if isinstance(vgs_value, (int, float)) else str(vgs_value)
        if selected_metric == "Supplier On-Time Delivery Rate":
            value_display = f"{value_str}%"
        else:
            value_display = f"${value_str}"

        card_html = f'''
        <div class="metric-card vgs-card">
            <div class="system-badge vgs-badge">VGS</div>
            <p class="system-role">Supplier Governance</p>
            <div class="metric-value">{value_display}</div>
            <div class="methodology-label">{methodology}</div>
            <p class="caption-text">{caption_text}</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        card_html = '''
        <div class="metric-card na-card">
            <div class="system-badge na-badge">VGS</div>
            <p class="system-role">Supplier Governance</p>
            <div class="metric-value na-value">N/A</div>
            <p class="caption-text">This system does not track this metric.</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)

# VPC Card
with col2:
    vpc_value = results.get("VPC")
    if vpc_value is not None:
        caption_text = ""
        methodology = ""
        if selected_metric == "Supplier On-Time Delivery Rate":
            methodology = "Does not track deliveries"
            caption_text = "VPC is a pricing system. It has no delivery performance data."
        elif selected_metric == "Negotiated Savings":
            methodology = "Uses list price as baseline"
            caption_text = "Compares current unit price against list price (not prior contract price). This inflates the savings number."
        elif selected_metric == "Active Contract Value":
            methodology = "Original value only"
            caption_text = "Stores the original contract value. Does not capture amendments or modifications."

        value_str = f"{vpc_value:,.2f}" if isinstance(vpc_value, (int, float)) else str(vpc_value)
        if selected_metric == "Supplier On-Time Delivery Rate":
            value_display = f"{value_str}%"
        else:
            value_display = f"${value_str}"

        card_html = f'''
        <div class="metric-card vpc-card">
            <div class="system-badge vpc-badge">VPC</div>
            <p class="system-role">Price & Cost Management</p>
            <div class="metric-value">{value_display}</div>
            <div class="methodology-label">{methodology}</div>
            <p class="caption-text">{caption_text}</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        card_html = '''
        <div class="metric-card na-card">
            <div class="system-badge na-badge">VPC</div>
            <p class="system-role">Price & Cost Management</p>
            <div class="metric-value na-value">N/A</div>
            <p class="caption-text">This system does not track this metric.</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)

# SI+ Card
with col3:
    si_value = results.get("SI+")
    if si_value is not None:
        caption_text = ""
        methodology = ""
        if selected_metric == "Supplier On-Time Delivery Rate":
            methodology = "Counts partial deliveries as on-time"
            caption_text = "Any delivery with status 'RECEIVED' counts as on-time, including partial deliveries. Uses own receipt timestamps."
        elif selected_metric == "Negotiated Savings":
            methodology = "Does not track savings"
            caption_text = "SI+ is an implementation tracking system. It has no pricing or savings data."
        elif selected_metric == "Active Contract Value":
            methodology = "Tracks committed spend instead"
            caption_text = "Records committed spend, not contract value. This is a fundamentally different concept."

        value_str = f"{si_value:,.2f}" if isinstance(si_value, (int, float)) else str(si_value)
        if selected_metric == "Supplier On-Time Delivery Rate":
            value_display = f"{value_str}%"
        else:
            value_display = f"${value_str}"

        card_html = f'''
        <div class="metric-card si-card">
            <div class="system-badge si-badge">SI+</div>
            <p class="system-role">Implementation Tracking</p>
            <div class="metric-value">{value_display}</div>
            <div class="methodology-label">{methodology}</div>
            <p class="caption-text">{caption_text}</p>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        card_html = '''
        <div class="metric-card na-card">
            <div class="system-badge na-badge">SI+</div>
            <p class="system-role">Implementation Tracking</p>
            <div class="metric-value na-value">N/A</div>
            <p class="caption-text">This system does not track this metric.</p>
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
            st.error(
                f"**Disagreement: {delta_pct:.1f} percentage points** — "
                f"A stakeholder querying VGS gets a different answer than one querying SI+. "
                f"Which number goes into the executive dashboard?"
            )
        else:
            delta_pct = abs((max_val - min_val) / min_val * 100) if min_val > 0 else 0
            st.error(
                f"**Disagreement: {delta_pct:.1f}%** — "
                f"Same metric, same time period, different answers. "
                f"Which system is right?"
            )


# ──────────────────────────────────────────────
# Step 2: The Governed Definition
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="section-header">
    <span class="section-number solution-bg">2</span>
    <div>
        <h2 style="margin: 0;">The Governed Definition</h2>
        <p class="section-desc">A semantic layer defines <strong>{metric}</strong> once — with a precise formula, documented inclusions/exclusions, and a single accountable owner. Every dashboard, report, and AI assistant queries this definition instead of raw tables.</p>
    </div>
</div>
""".format(metric=selected_metric), unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    metric_def = get_metric_by_name(selected_metric)
    if metric_def:
        inclusions_html = "".join([f"<li>{inc}</li>" for inc in metric_def['inclusions']])
        exclusions_html = "".join([f"<li>{exc}</li>" for exc in metric_def['exclusions']])

        # Show authoritative source mapping
        sources_html = ""
        if 'authoritative_source' in metric_def:
            sources_items = "".join([f"<li>{src}</li>" for src in metric_def['authoritative_source']])
            sources_html = f'<p><strong>Data Sources:</strong></p><ul class="source-list">{sources_items}</ul>'

        definition_html = f'''
        <div class="definition-card">
            <div class="definition-badge">Governed Metric Definition</div>
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
            {sources_html}
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
            <div class="governed-label">Single Certified Answer</div>
            <div class="governed-value">{value_display}</div>
            <p class="governed-explanation">
                This value is computed from the governed definition on the left.
                Every consumer — dashboards, reports, AI assistants — gets this same number.
            </p>
        </div>
        '''
        st.markdown(governed_html, unsafe_allow_html=True)

        st.markdown("#### Data Lineage")
        st.markdown(
            '<p style="font-size: 0.85rem; opacity: 0.7; margin-bottom: 0.5rem;">'
            'Trace exactly which fields from which systems feed into the certified metric.'
            '</p>',
            unsafe_allow_html=True
        )
        lineage_diagram = create_lineage_diagram(selected_metric)
        st.graphviz_chart(lineage_diagram.source)


# ──────────────────────────────────────────────
# Step 3: The Business Impact
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="section-header">
    <span class="section-number impact-bg">3</span>
    <div>
        <h2 style="margin: 0;">The Business Impact</h2>
        <p class="section-desc">Inconsistent metrics do not just produce different numbers. They produce different <em>decisions</em>. Here is what happens in practice when teams rely on different source systems.</p>
    </div>
</div>
""", unsafe_allow_html=True)

if selected_metric == "Supplier On-Time Delivery Rate":
    threshold = 85.0

    vgs_flags = get_supplier_flags(selected_metric, st.session_state.data, threshold, quarter_filter, region_filter)

    if results.get("VGS") is not None and results.get("SI+") is not None:
        vgs_rate = results.get("VGS")
        si_rate = results.get("SI+")
        governed_rate = results.get("Governed")

        total_suppliers = 20
        vgs_flagged = int(total_suppliers * (1 - vgs_rate / 100)) if vgs_rate < threshold else 0
        si_flagged = int(total_suppliers * (1 - si_rate / 100)) if si_rate < threshold else 0
        governed_flagged = int(total_suppliers * (1 - governed_rate / 100)) if governed_rate and governed_rate < threshold else 0

        st.markdown("##### Scenario: Which suppliers should be flagged for performance review?")
        st.markdown(f"Using an {threshold:.0f}% on-time threshold to flag underperforming suppliers:")

        comparison_df = pd.DataFrame({
            "Source": ["VGS (Supplier Governance)", "SI+ (Implementation Tracking)", "Semantic Layer (Governed)"],
            "Suppliers Flagged": [vgs_flagged, si_flagged, governed_flagged],
            "Why This Number Differs": [
                "Excludes partial deliveries → stricter standard → flags more suppliers",
                "Counts partials as on-time → lenient standard → flags fewer suppliers",
                "Documented exclusion rules → balanced, auditable, and consistent"
            ]
        })

        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        st.markdown("""
        **What goes wrong without a semantic layer:**
        - The procurement team uses VGS and flags **12 suppliers** for review
        - The logistics team uses SI+ and flags only **4 suppliers**
        - In the weekly operations review, they spend 30 minutes debating whose numbers are right instead of deciding which suppliers need intervention
        - The semantic layer resolves this: **8 suppliers** flagged with documented, auditable reasoning for each inclusion and exclusion
        """)

elif selected_metric == "Negotiated Savings":
    st.markdown("##### Scenario: Reporting savings to the CFO in a quarterly business review")

    col_impact1, col_impact2, col_impact3 = st.columns(3)

    with col_impact1:
        st.markdown("""
        <div class="impact-card">
            <div class="system-badge vgs-badge" style="display: inline-block;">VGS</div>
            <p><strong>Savings appear lower</strong></p>
            <p class="caption-text">VGS has prior contract prices but no volume data. It extrapolates volume from contract value and assumes a fixed savings percentage. The result is a rough estimate.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_impact2:
        st.markdown("""
        <div class="impact-card">
            <div class="system-badge vpc-badge" style="display: inline-block;">VPC</div>
            <p><strong>Savings appear inflated</strong></p>
            <p class="caption-text">VPC compares current unit price against list price (not prior contract price). Since list price is always higher, savings look larger than they actually are.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_impact3:
        st.markdown("""
        <div class="impact-card">
            <div class="system-badge governed-badge" style="display: inline-block;">Governed</div>
            <p><strong>Accurate savings</strong></p>
            <p class="caption-text">The semantic layer uses prior contract price from VGS, current price and volume from VPC, and applies documented inclusion/exclusion rules.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    **What goes wrong without a semantic layer:**
    - Procurement presents savings using VPC numbers (looks great)
    - Finance cross-checks against VGS numbers (looks modest)
    - The quarterly business review becomes a debate about methodology instead of a conversation about supplier strategy
    - The semantic layer produces one number that both teams can trace back to its exact definition and data sources
    """)

elif selected_metric == "Active Contract Value":
    st.markdown("##### Scenario: Budget planning for the next fiscal year")

    col_impact1, col_impact2, col_impact3 = st.columns(3)

    with col_impact1:
        st.markdown("""
        <div class="impact-card">
            <div class="system-badge vgs-badge" style="display: inline-block;">VGS</div>
            <p><strong>Higher value (includes amendments)</strong></p>
            <p class="caption-text">VGS tracks the full contract lifecycle including all amendments and modifications. This is more accurate for financial planning.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_impact2:
        st.markdown("""
        <div class="impact-card">
            <div class="system-badge vpc-badge" style="display: inline-block;">VPC</div>
            <p><strong>Lower value (original only)</strong></p>
            <p class="caption-text">VPC only stores the original contract value at time of creation. Any amendments or scope changes are invisible.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_impact3:
        st.markdown("""
        <div class="impact-card">
            <div class="system-badge si-badge" style="display: inline-block;">SI+</div>
            <p><strong>Different concept entirely</strong></p>
            <p class="caption-text">SI+ tracks committed spend, which is not the same as contract value. Comparing this number to VGS or VPC is misleading.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    **What goes wrong without a semantic layer:**
    - The procurement director uses VGS for budget planning (accurate but only they know why)
    - A new analyst queries VPC and reports a lower number to the CFO
    - SI+ data shows up in a logistics dashboard as "contract value" even though it is committed spend
    - The semantic layer defines "Active Contract Value" precisely: `original_value + amendments` for contracts where `contract_end >= today`, sourced from VGS
    """)


# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>
        <strong>Metric Trust Explorer</strong> — Interactive companion to
        <a href="https://cynthialmy.github.io/2025-02-13-semantic-layer-bi/" target="_blank">Building a Semantic-Layer-Driven BI Product</a>
    </p>
    <p>Built by <a href="https://cynthialmy.github.io" target="_blank">Cynthia Mengyuan Li</a> | Synthetic data modeled after enterprise procurement systems</p>
</div>
""", unsafe_allow_html=True)
