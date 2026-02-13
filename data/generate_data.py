"""
Generate synthetic procurement data for three source systems (VGS, VPC, SI+)
with deliberate discrepancies to illustrate semantic layer challenges.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# Constants
SUPPLIERS = [
    {"id": f"SUP{i:03d}", "name": f"Supplier {chr(65 + (i % 26))}{i}", "region": ["Europe", "Asia", "Americas", "Other"][i % 4]}
    for i in range(1, 21)
]

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
QUARTER_DATES = {
    "Q1": (datetime(2025, 1, 1), datetime(2025, 3, 31)),
    "Q2": (datetime(2025, 4, 1), datetime(2025, 6, 30)),
    "Q3": (datetime(2025, 7, 1), datetime(2025, 9, 30)),
    "Q4": (datetime(2025, 10, 1), datetime(2025, 12, 31)),
}


def generate_vgs_data():
    """Generate VGS (Supplier Governance) data"""
    records = []
    
    for supplier in SUPPLIERS:
        # Each supplier has 1-3 contracts
        num_contracts = random.randint(1, 3)
        
        for c in range(num_contracts):
            contract_id = f"VGS-{supplier['id']}-{c+1:02d}"
            contract_start = datetime(2024, random.randint(1, 12), random.randint(1, 28))
            contract_end = datetime(2025, random.randint(7, 12), random.randint(1, 28))
            
            original_value = random.uniform(500000, 5000000)
            amendment_value = random.uniform(0, original_value * 0.3)  # 0-30% amendment
            prior_contract_price = random.uniform(100, 500)  # Unit price from prior contract
            
            # Generate delivery events across quarters
            for quarter in QUARTERS:
                q_start, q_end = QUARTER_DATES[quarter]
                num_deliveries = random.randint(2, 8)
                
                for d in range(num_deliveries):
                    delivery_date = q_start + timedelta(days=random.randint(0, (q_end - q_start).days))
                    agreed_window_start = delivery_date - timedelta(days=random.randint(0, 5))
                    agreed_window_end = delivery_date + timedelta(days=random.randint(0, 3))
                    
                    # VGS excludes partial deliveries from on-time count
                    is_partial = random.random() < 0.15  # 15% partial deliveries
                    force_majeure = random.random() < 0.05  # 5% force majeure
                    
                    records.append({
                        "supplier_id": supplier["id"],
                        "supplier_name": supplier["name"],
                        "region": supplier["region"],
                        "contract_id": contract_id,
                        "contract_start": contract_start.strftime("%Y-%m-%d"),
                        "contract_end": contract_end.strftime("%Y-%m-%d"),
                        "original_value": round(original_value, 2),
                        "amendment_value": round(amendment_value, 2),
                        "prior_contract_price": round(prior_contract_price, 2),
                        "delivery_date": delivery_date.strftime("%Y-%m-%d"),
                        "agreed_window_start": agreed_window_start.strftime("%Y-%m-%d"),
                        "agreed_window_end": agreed_window_end.strftime("%Y-%m-%d"),
                        "is_partial_delivery": is_partial,
                        "force_majeure_flag": force_majeure,
                        "quarter": quarter,
                    })
    
    df = pd.DataFrame(records)
    df.to_csv("data/system_vgs.csv", index=False)
    print(f"Generated VGS data: {len(df)} records")
    return df


def generate_vpc_data():
    """Generate VPC (Price/Cost Management) data"""
    records = []
    
    for supplier in SUPPLIERS:
        # Each supplier has contracts in VPC
        num_contracts = random.randint(1, 2)
        
        for c in range(num_contracts):
            contract_id = f"VPC-{supplier['id']}-{c+1:02d}"
            original_contract_value = random.uniform(500000, 5000000)
            
            # VPC uses list price as baseline (inflated)
            list_price = random.uniform(150, 600)
            unit_price = list_price * random.uniform(0.7, 0.95)  # 5-30% discount from list
            negotiated_discount_pct = (1 - unit_price / list_price) * 100
            
            for quarter in QUARTERS:
                volume = random.uniform(1000, 10000)
                
                records.append({
                    "supplier_id": supplier["id"],
                    "supplier_name": supplier["name"],
                    "region": supplier["region"],
                    "contract_id": contract_id,
                    "original_contract_value": round(original_contract_value, 2),
                    "unit_price": round(unit_price, 2),
                    "list_price": round(list_price, 2),
                    "volume": round(volume, 0),
                    "negotiated_discount_pct": round(negotiated_discount_pct, 2),
                    "quarter": quarter,
                })
    
    df = pd.DataFrame(records)
    df.to_csv("data/system_vpc.csv", index=False)
    print(f"Generated VPC data: {len(df)} records")
    return df


def generate_si_data():
    """Generate SI+ (Implementation Tracking) data"""
    records = []
    
    for supplier in SUPPLIERS:
        for quarter in QUARTERS:
            q_start, q_end = QUARTER_DATES[quarter]
            num_deliveries = random.randint(3, 10)
            
            for d in range(num_deliveries):
                delivery_id = f"SI-{supplier['id']}-{quarter}-{d+1:03d}"
                scheduled_date = q_start + timedelta(days=random.randint(0, (q_end - q_start).days))
                
                # SI+ counts partial deliveries as on-time if received
                is_partial = random.random() < 0.15
                # Actual receipt can be early, on-time, or late
                days_offset = random.randint(-2, 5)
                actual_receipt_date = scheduled_date + timedelta(days=days_offset)
                
                # Status based on receipt timing
                if actual_receipt_date <= scheduled_date + timedelta(days=1):
                    status = "RECEIVED"
                elif actual_receipt_date <= scheduled_date + timedelta(days=3):
                    status = "LATE"
                else:
                    status = "DELAYED"
                
                committed_spend = random.uniform(50000, 500000)
                
                records.append({
                    "supplier_id": supplier["id"],
                    "supplier_name": supplier["name"],
                    "region": supplier["region"],
                    "delivery_id": delivery_id,
                    "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
                    "actual_receipt_date": actual_receipt_date.strftime("%Y-%m-%d"),
                    "status": status,
                    "is_partial": is_partial,
                    "committed_spend": round(committed_spend, 2),
                    "quarter": quarter,
                })
    
    df = pd.DataFrame(records)
    df.to_csv("data/system_si.csv", index=False)
    print(f"Generated SI+ data: {len(df)} records")
    return df


if __name__ == "__main__":
    print("Generating synthetic procurement data...")
    generate_vgs_data()
    generate_vpc_data()
    generate_si_data()
    print("Data generation complete!")
