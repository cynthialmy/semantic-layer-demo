"""Generate Graphviz lineage diagrams for metrics."""

from graphviz import Digraph


def create_lineage_diagram(metric_name):
    """Create a Graphviz DAG showing metric lineage."""
    dot = Digraph(comment=metric_name)
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    dot.attr('edge', fontname='Arial')
    
    if metric_name == "Supplier On-Time Delivery Rate":
        # Source systems
        dot.node('si', 'SI+ System\n(Receipt Timestamps)', fillcolor='#4ECDC4', fontcolor='white')
        dot.node('vgs', 'VGS System\n(Agreed Windows)', fillcolor='#4472C4', fontcolor='white')
        
        # Data fields
        dot.node('si_date', 'actual_receipt_date', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vgs_start', 'agreed_window_start', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vgs_end', 'agreed_window_end', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vgs_partial', 'is_partial_delivery', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vgs_fm', 'force_majeure_flag', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        
        # Transformation
        dot.node('merge', 'Merge by\nsupplier_id', fillcolor='#F4A261', fontcolor='white')
        dot.node('filter', 'Filter:\nExclude partials\nExclude force majeure', fillcolor='#F4A261', fontcolor='white')
        dot.node('calc', 'Calculate:\nOn-Time Rate', fillcolor='#2A9D8F', fontcolor='white')
        
        # Output
        dot.node('metric', 'Governed Metric\nOn-Time Delivery Rate', fillcolor='#27AE60', fontcolor='white', shape='ellipse')
        
        # Edges
        dot.edge('si', 'si_date')
        dot.edge('vgs', 'vgs_start')
        dot.edge('vgs', 'vgs_end')
        dot.edge('vgs', 'vgs_partial')
        dot.edge('vgs', 'vgs_fm')
        dot.edge('si_date', 'merge')
        dot.edge('vgs_start', 'merge')
        dot.edge('vgs_end', 'merge')
        dot.edge('merge', 'filter')
        dot.edge('vgs_partial', 'filter')
        dot.edge('vgs_fm', 'filter')
        dot.edge('filter', 'calc')
        dot.edge('calc', 'metric')
        
    elif metric_name == "Negotiated Savings":
        # Source systems
        dot.node('vgs', 'VGS System\n(Prior Contract Price)', fillcolor='#4472C4', fontcolor='white')
        dot.node('vpc', 'VPC System\n(Current Price & Volume)', fillcolor='#F39C12', fontcolor='white')
        
        # Data fields
        dot.node('vgs_price', 'prior_contract_price', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vpc_price', 'unit_price', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vpc_vol', 'volume', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        
        # Transformation
        dot.node('merge', 'Merge by\nsupplier_id', fillcolor='#F4A261', fontcolor='white')
        dot.node('filter', 'Filter:\nValid prices\nVolume > 0', fillcolor='#F4A261', fontcolor='white')
        dot.node('calc', 'Calculate:\n(prior_price - current_price) × volume', fillcolor='#2A9D8F', fontcolor='white')
        
        # Output
        dot.node('metric', 'Governed Metric\nNegotiated Savings', fillcolor='#27AE60', fontcolor='white', shape='ellipse')
        
        # Edges
        dot.edge('vgs', 'vgs_price')
        dot.edge('vpc', 'vpc_price')
        dot.edge('vpc', 'vpc_vol')
        dot.edge('vgs_price', 'merge')
        dot.edge('vpc_price', 'merge')
        dot.edge('vpc_vol', 'merge')
        dot.edge('merge', 'filter')
        dot.edge('filter', 'calc')
        dot.edge('calc', 'metric')
        
    elif metric_name == "Active Contract Value":
        # Source system
        dot.node('vgs', 'VGS System\n(Contract Data)', fillcolor='#4472C4', fontcolor='white')
        
        # Data fields
        dot.node('vgs_start', 'contract_start', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vgs_end', 'contract_end', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vgs_orig', 'original_value', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        dot.node('vgs_amend', 'amendment_value', fillcolor='#E8F4F8', fontcolor='#2C3E50')
        
        # Transformation
        dot.node('filter', 'Filter:\nActive contracts only\n(contract_end >= today)', fillcolor='#F4A261', fontcolor='white')
        dot.node('calc', 'Calculate:\noriginal_value + amendment_value', fillcolor='#2A9D8F', fontcolor='white')
        dot.node('agg', 'Aggregate:\nSum by contract', fillcolor='#2A9D8F', fontcolor='white')
        
        # Output
        dot.node('metric', 'Governed Metric\nActive Contract Value', fillcolor='#27AE60', fontcolor='white', shape='ellipse')
        
        # Edges
        dot.edge('vgs', 'vgs_start')
        dot.edge('vgs', 'vgs_end')
        dot.edge('vgs', 'vgs_orig')
        dot.edge('vgs', 'vgs_amend')
        dot.edge('vgs_start', 'filter')
        dot.edge('vgs_end', 'filter')
        dot.edge('filter', 'calc')
        dot.edge('vgs_orig', 'calc')
        dot.edge('vgs_amend', 'calc')
        dot.edge('calc', 'agg')
        dot.edge('agg', 'metric')
    
    return dot
