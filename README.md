# Metric Trust Explorer

A semantic layer demo that illustrates why defining metrics once matters at enterprise scale.

## Overview

This Streamlit app demonstrates how different source systems (VGS, VPC, SI+) compute the same procurement metrics differently, and how a governed semantic layer provides a single source of truth.

## Features

- **Three conflicting source systems**: Each system computes metrics with different logic, filters, and data sources
- **Governed metric definitions**: YAML-based metric definitions that serve as the semantic layer
- **Visual lineage**: Graphviz diagrams showing how metrics are computed from source systems
- **Business impact simulation**: Demonstrates how metric inconsistencies lead to different business decisions

## Metrics Demonstrated

1. **Supplier On-Time Delivery Rate**: Shows how VGS excludes partial deliveries while SI+ counts them, leading to different percentages
2. **Negotiated Savings**: Illustrates how VGS uses prior contract price while VPC uses list price, producing inflated savings
3. **Active Contract Value**: Demonstrates how VGS includes amendments while VPC shows original value only

## Installation

```bash
# Clone the repository
git clone https://github.com/cynthialmy/semantic-layer-demo.git
cd semantic-layer-demo

# Install dependencies
pip install -r requirements.txt

# Note: On some systems, you may need to install Graphviz system library:
# macOS: brew install graphviz
# Ubuntu/Debian: sudo apt-get install graphviz
# Windows: Download from https://graphviz.org/download/

# Generate synthetic data
python3 data/generate_data.py

# Run the app
streamlit run app.py
```

## Project Structure

```
semantic-layer-demo/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/
│   ├── generate_data.py   # Script to generate synthetic data
│   ├── system_vgs.csv     # VGS system data
│   ├── system_vpc.csv     # VPC system data
│   └── system_si.csv      # SI+ system data
├── metrics/
│   └── definitions.yml     # Governed metric definitions
├── engine/
│   ├── loaders.py         # Data and YAML loading
│   ├── compute.py         # Metric computation logic
│   └── lineage.py         # Graphviz lineage generation
├── style/
│   └── custom.css         # Custom styling
└── .streamlit/
    └── config.toml        # Streamlit theme configuration
```

## Deployment

Deploy to Streamlit Community Cloud:

1. Push to GitHub repository `cynthialmy/semantic-layer-demo`
2. Connect to Streamlit Cloud
3. Set the main file path to `app.py`
4. The app will automatically install dependencies from `requirements.txt`

## Related Content

This demo accompanies the blog post: [Building a Semantic-Layer-Driven BI Product](https://cynthialmy.github.io/2025/02/13/semantic-layer-bi-product.html)

## License

MIT License
