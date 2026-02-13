"""Load CSV data and parse YAML metric definitions."""

import pandas as pd
import yaml
from pathlib import Path


def load_system_data():
    """Load all three source system CSVs."""
    base_path = Path(__file__).parent.parent
    
    vgs = pd.read_csv(base_path / "data" / "system_vgs.csv")
    vpc = pd.read_csv(base_path / "data" / "system_vpc.csv")
    si = pd.read_csv(base_path / "data" / "system_si.csv")
    
    # Convert date columns
    date_cols_vgs = ["contract_start", "contract_end", "delivery_date", "agreed_window_start", "agreed_window_end"]
    for col in date_cols_vgs:
        if col in vgs.columns:
            vgs[col] = pd.to_datetime(vgs[col], errors='coerce')
    
    date_cols_si = ["scheduled_date", "actual_receipt_date"]
    for col in date_cols_si:
        if col in si.columns:
            si[col] = pd.to_datetime(si[col], errors='coerce')
    
    # Convert boolean columns
    bool_cols_vgs = ["is_partial_delivery", "force_majeure_flag"]
    for col in bool_cols_vgs:
        if col in vgs.columns:
            vgs[col] = vgs[col].astype(bool)
    
    bool_cols_si = ["is_partial"]
    for col in bool_cols_si:
        if col in si.columns:
            si[col] = si[col].astype(bool)
    
    return {"vgs": vgs, "vpc": vpc, "si": si}


def load_metric_definitions():
    """Load and parse metric definitions from YAML."""
    base_path = Path(__file__).parent.parent
    yaml_path = base_path / "metrics" / "definitions.yml"
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    return {metric["name"]: metric for metric in data["metrics"]}


def get_metric_by_name(name):
    """Get a specific metric definition by name."""
    definitions = load_metric_definitions()
    return definitions.get(name)
