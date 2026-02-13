"""Compute metrics per system and using governed definitions."""

import pandas as pd
from datetime import datetime, timedelta
from .loaders import load_system_data, get_metric_by_name


def compute_vgs_on_time_delivery(data, quarter=None, region=None):
    """VGS computes on-time delivery excluding partials."""
    vgs = data["vgs"].copy()
    
    # Apply filters
    if quarter:
        vgs = vgs[vgs["quarter"] == quarter]
    if region:
        vgs = vgs[vgs["region"].isin(region)]
    
    # VGS excludes partial deliveries
    vgs_filtered = vgs[
        (vgs["is_partial_delivery"] == False) &
        (vgs["force_majeure_flag"] == False)
    ].copy()
    
    # Check if delivery_date is within agreed window
    vgs_filtered.loc[:, "is_on_time"] = (
        (vgs_filtered["delivery_date"] >= vgs_filtered["agreed_window_start"]) &
        (vgs_filtered["delivery_date"] <= vgs_filtered["agreed_window_end"])
    )
    
    if len(vgs_filtered) == 0:
        return None
    
    on_time_rate = (vgs_filtered["is_on_time"].sum() / len(vgs_filtered)) * 100
    return round(on_time_rate, 2)


def compute_si_on_time_delivery(data, quarter=None, region=None):
    """SI+ computes on-time delivery including partials."""
    si = data["si"].copy()
    
    # Apply filters
    if quarter:
        si = si[si["quarter"] == quarter]
    if region:
        si = si[si["region"].isin(region)]
    
    # SI+ counts partials as on-time if received
    si_filtered = si[si["status"] == "RECEIVED"]
    
    if len(si_filtered) == 0:
        return None
    
    # SI+ considers it on-time if status is RECEIVED (includes partials)
    on_time_rate = (len(si_filtered) / len(si)) * 100
    return round(on_time_rate, 2)


def compute_governed_on_time_delivery(data, quarter=None, region=None):
    """Governed metric: SI+ timestamps + VGS windows, excluding partials."""
    vgs = data["vgs"].copy()
    si = data["si"].copy()
    
    # Apply filters
    if quarter:
        vgs = vgs[vgs["quarter"] == quarter]
        si = si[si["quarter"] == quarter]
    if region:
        vgs = vgs[vgs["region"].isin(region)]
        si = si[si["region"].isin(region)]
    
    # Merge SI+ receipt dates with VGS windows
    vgs_subset = vgs[["supplier_id", "agreed_window_start", "agreed_window_end", "is_partial_delivery", "force_majeure_flag"]].drop_duplicates(subset=["supplier_id"])
    merged = si.merge(
        vgs_subset,
        on="supplier_id",
        how="inner"
    )
    
    # Exclude partials and force majeure
    merged = merged[
        (merged["is_partial_delivery"] == False) &
        (merged["force_majeure_flag"] == False)
    ]
    
    # Check if actual_receipt_date is within agreed window
    merged = merged.copy()
    merged.loc[:, "is_on_time"] = (
        (merged["actual_receipt_date"] >= merged["agreed_window_start"]) &
        (merged["actual_receipt_date"] <= merged["agreed_window_end"])
    )
    
    if len(merged) == 0:
        return None
    
    on_time_rate = (merged["is_on_time"].sum() / len(merged)) * 100
    return round(on_time_rate, 2)


def compute_vgs_savings(data, quarter=None, region=None):
    """VGS computes savings using prior contract price (no volume data)."""
    vgs = data["vgs"].copy()
    
    # Apply filters
    if quarter:
        vgs = vgs[vgs["quarter"] == quarter]
    if region:
        vgs = vgs[vgs["region"].isin(region)]
    
    # VGS has prior price but no volume, so extrapolates
    vgs_filtered = vgs[vgs["prior_contract_price"].notna()]
    
    if len(vgs_filtered) == 0:
        return None
    
    # Estimate volume from contract value
    avg_unit_price = vgs_filtered["prior_contract_price"].mean()
    total_value = vgs_filtered["original_value"].sum()
    estimated_volume = total_value / avg_unit_price if avg_unit_price > 0 else 0
    
    # Assume 10% savings (VGS doesn't have current price)
    estimated_savings = vgs_filtered["prior_contract_price"].mean() * 0.1 * estimated_volume
    return round(estimated_savings, 2)


def compute_vpc_savings(data, quarter=None, region=None):
    """VPC computes savings using list price as baseline (inflated)."""
    vpc = data["vpc"].copy()
    
    # Apply filters
    if quarter:
        vpc = vpc[vpc["quarter"] == quarter]
    if region:
        vpc = vpc[vpc["region"].isin(region)]
    
    # VPC uses list price as baseline
    vpc = vpc.copy()
    vpc.loc[:, "savings"] = (vpc["list_price"] - vpc["unit_price"]) * vpc["volume"]
    total_savings = vpc["savings"].sum()
    
    return round(total_savings, 2) if not pd.isna(total_savings) else None


def compute_governed_savings(data, quarter=None, region=None):
    """Governed metric: VGS prior price - VPC current price * VPC volume."""
    vgs = data["vgs"].copy()
    vpc = data["vpc"].copy()
    
    # Apply filters
    if quarter:
        vgs = vgs[vgs["quarter"] == quarter]
        vpc = vpc[vpc["quarter"] == quarter]
    if region:
        vgs = vgs[vgs["region"].isin(region)]
        vpc = vpc[vpc["region"].isin(region)]
    
    # Merge VGS prior price with VPC current price and volume
    vgs_subset = vgs[["supplier_id", "prior_contract_price"]].drop_duplicates(subset=["supplier_id"])
    merged = vpc.merge(
        vgs_subset,
        on="supplier_id",
        how="inner"
    )
    
    # Filter valid records
    merged = merged[
        (merged["prior_contract_price"].notna()) &
        (merged["volume"] > 0) &
        (merged["prior_contract_price"] > merged["unit_price"])
    ]
    
    if len(merged) == 0:
        return None
    
    merged = merged.copy()
    merged.loc[:, "savings"] = (merged["prior_contract_price"] - merged["unit_price"]) * merged["volume"]
    total_savings = merged["savings"].sum()
    
    return round(total_savings, 2) if not pd.isna(total_savings) else None


def compute_vgs_contract_value(data, quarter=None, region=None):
    """VGS includes amendments in contract value."""
    vgs = data["vgs"].copy()
    
    # Apply filters
    if quarter:
        vgs = vgs[vgs["quarter"] == quarter]
    if region:
        vgs = vgs[vgs["region"].isin(region)]
    
    # Filter active contracts
    today = datetime.now()
    vgs_filtered = vgs[
        (pd.to_datetime(vgs["contract_end"]) >= today) &
        (pd.to_datetime(vgs["contract_start"]) <= today)
    ]
    
    if len(vgs_filtered) == 0:
        return None
    
    # VGS includes amendments
    total_value = (vgs_filtered["original_value"] + vgs_filtered["amendment_value"]).sum()
    return round(total_value, 2)


def compute_vpc_contract_value(data, quarter=None, region=None):
    """VPC shows original value only (no amendments)."""
    vpc = data["vpc"].copy()
    
    # Apply filters
    if quarter:
        vpc = vpc[vpc["quarter"] == quarter]
    if region:
        vpc = vpc[vpc["region"].isin(region)]
    
    # VPC only has original value
    total_value = vpc["original_contract_value"].sum()
    return round(total_value, 2) if not pd.isna(total_value) else None


def compute_si_contract_value(data, quarter=None, region=None):
    """SI+ tracks committed spend (different concept)."""
    si = data["si"].copy()
    
    # Apply filters
    if quarter:
        si = si[si["quarter"] == quarter]
    if region:
        si = si[si["region"].isin(region)]
    
    # SI+ tracks committed spend, not contract value
    total_spend = si["committed_spend"].sum()
    return round(total_spend, 2) if not pd.isna(total_spend) else None


def compute_governed_contract_value(data, quarter=None, region=None):
    """Governed metric: VGS original + amendments for active contracts."""
    vgs = data["vgs"].copy()
    
    # Apply filters
    if quarter:
        vgs = vgs[vgs["quarter"] == quarter]
    if region:
        vgs = vgs[vgs["region"].isin(region)]
    
    # Filter active contracts
    today = datetime.now()
    vgs_filtered = vgs[
        (pd.to_datetime(vgs["contract_end"]) >= today) &
        (pd.to_datetime(vgs["contract_start"]) <= today)
    ]
    
    if len(vgs_filtered) == 0:
        return None
    
    # Sum original + amendments per contract (dedupe)
    contract_values = vgs_filtered.groupby("contract_id").agg({
        "original_value": "first",
        "amendment_value": "first"
    }).reset_index()
    
    contract_values["total_value"] = contract_values["original_value"] + contract_values["amendment_value"]
    total_value = contract_values["total_value"].sum()
    
    return round(total_value, 2)


def compute_metric_per_system(metric_name, data, quarter=None, region=None):
    """Compute a metric for each system."""
    results = {}
    
    if metric_name == "Supplier On-Time Delivery Rate":
        results["VGS"] = compute_vgs_on_time_delivery(data, quarter, region)
        results["SI+"] = compute_si_on_time_delivery(data, quarter, region)
        results["VPC"] = None  # VPC doesn't track delivery
        results["Governed"] = compute_governed_on_time_delivery(data, quarter, region)
        
    elif metric_name == "Negotiated Savings":
        results["VGS"] = compute_vgs_savings(data, quarter, region)
        results["VPC"] = compute_vpc_savings(data, quarter, region)
        results["SI+"] = None  # SI+ doesn't track savings
        results["Governed"] = compute_governed_savings(data, quarter, region)
        
    elif metric_name == "Active Contract Value":
        results["VGS"] = compute_vgs_contract_value(data, quarter, region)
        results["VPC"] = compute_vpc_contract_value(data, quarter, region)
        results["SI+"] = compute_si_contract_value(data, quarter, region)
        results["Governed"] = compute_governed_contract_value(data, quarter, region)
    
    return results


def get_supplier_flags(metric_name, data, threshold, quarter=None, region=None):
    """Get suppliers flagged for review based on metric threshold."""
    if metric_name == "Supplier On-Time Delivery Rate":
        # Compute per-supplier on-time rates using governed logic
        vgs = data["vgs"].copy()
        si = data["si"].copy()
        
        if quarter:
            vgs = vgs[vgs["quarter"] == quarter]
            si = si[si["quarter"] == quarter]
        if region:
            vgs = vgs[vgs["region"].isin(region)]
            si = si[si["region"].isin(region)]
        
        vgs_subset = vgs[["supplier_id", "agreed_window_start", "agreed_window_end", "is_partial_delivery", "force_majeure_flag"]].drop_duplicates(subset=["supplier_id"])
        merged = si.merge(
            vgs_subset,
            on="supplier_id",
            how="inner"
        )
        
        merged = merged[
            (merged["is_partial_delivery"] == False) &
            (merged["force_majeure_flag"] == False)
        ]
        
        merged = merged.copy()
        merged.loc[:, "is_on_time"] = (
            (merged["actual_receipt_date"] >= merged["agreed_window_start"]) &
            (merged["actual_receipt_date"] <= merged["agreed_window_end"])
        )
        
        supplier_rates = merged.groupby("supplier_id").agg({
            "is_on_time": ["sum", "count"]
        }).reset_index()
        supplier_rates.columns = ["supplier_id", "on_time_count", "total_count"]
        supplier_rates["rate"] = (supplier_rates["on_time_count"] / supplier_rates["total_count"]) * 100
        
        flagged = supplier_rates[supplier_rates["rate"] < threshold]
        return len(flagged)
    
    return 0
