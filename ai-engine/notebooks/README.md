# AI Engine - Jupyter Notebooks

This directory contains research, exploratory data analysis (EDA), prototype models, and experimentation notebooks for the **AI Autonomous Operations Intelligence Platform** (Dubai Facility & Property Management).

## Notebook Structure & Conventions

- `01_eda_asset_telemetry.ipynb`: Exploratory data analysis for HVAC, chillers, elevators, and facility assets.
- `02_predictive_maintenance_prototyping.ipynb`: Experiments with asset failure prediction models.
- `03_demand_forecasting_inventory.ipynb`: Time-series forecasting for spare parts and consumable demand.
- `04_risk_scoring_validation.ipynb`: Validation and sensitivity analysis of risk index algorithms.
- `05_recommendation_eval.ipynb`: Evaluation of AI-driven proactive work order and purchase recommendations.

## Guidelines
- Do not commit large dataset outputs inside notebooks.
- Store reusable logic in `src/` modules rather than copy-pasting code across notebooks.
