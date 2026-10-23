import os
import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, CrostonSBA, AutoETS

print(">>> Step 1: Architecting transactional ledger profiles...")
np.random.seed(101)
date_timeline = pd.date_range(start="2024-11-01", periods=104, freq="W")

# PROFILE A: High-Volume Seasonal
seasonal_pattern = 1200 + (np.sin(np.linspace(0, 20, 104)) * 400) + np.random.normal(0, 60, 104)
data_seasonal = pd.DataFrame({
    'unique_id': 'PHARMA_SKU_SEASONAL_OTC_FAST',
    'ds': date_timeline,
    'y': np.clip(seasonal_pattern, 0, None)
})

# PROFILE B: Low-Volume Erratic
intermittent_base = np.zeros(104)
random_spike_weeks = np.random.choice(np.arange(104), size=14, replace=False)
intermittent_base[random_spike_weeks] = np.random.randint(10, 35, size=14)
data_intermittent = pd.DataFrame({
    'unique_id': 'PHARMA_SKU_HIGHVAL_ONCOLOGY_ERRATIC',
    'ds': date_timeline,
    'y': intermittent_base
})

master_raw_erp = pd.concat([data_seasonal, data_intermittent], ignore_index=True)
master_raw_erp['unique_id'] = master_raw_erp['unique_id'].astype(str)
master_raw_erp['ds'] = pd.to_datetime(master_raw_erp['ds'])
master_raw_erp['y'] = pd.to_numeric(master_raw_erp['y'], errors='coerce').fillna(0.0)

print(">>> Step 2: Activating local concurrent processing array...")
algorithmic_suite = [
    AutoARIMA(season_length=52),
    CrostonSBA(),
    AutoETS(season_length=52)
]
sf_processor = StatsForecast(models=algorithmic_suite, freq='W', n_jobs=-1)

print(">>> Step 3: Generating mathematical forecasts entirely offline...")
computed_forecast_matrix = sf_processor.forecast(df=master_raw_erp, h=4).reset_index()

print(">>> Step 4: Applying operational safety guards and profile selection...")
model_targets = ['AutoARIMA', 'CrostonSBA', 'AutoETS']
for column in model_targets:
    computed_forecast_matrix[column] = computed_forecast_matrix[column].clip(lower=0.0)

consolidated_procurement_array = []
for product_sku in computed_forecast_matrix['unique_id'].unique():
    sku_block = computed_forecast_matrix[computed_forecast_matrix['unique_id'] == product_sku].copy()
    if "ONCOLOGY" in product_sku:
        sku_block['TARGET_PROJECTION'] = sku_block['CrostonSBA']
        sku_block['APPLIED_LOGIC_RULE'] = 'CrostonSBA (Intermittent Stock Protocol)'
    else:
        sku_block['TARGET_PROJECTION'] = sku_block['AutoARIMA']
        sku_block['APPLIED_LOGIC_RULE'] = 'AutoARIMA (High-Velocity Seasonality Protocol)'
    consolidated_procurement_array.append(sku_block)

final_actionable_blueprint = pd.concat(consolidated_procurement_array, ignore_index=True)
final_actionable_blueprint['FINAL_SUGGESTED_ORDER_QUANTITY'] = np.ceil(final_actionable_blueprint['TARGET_PROJECTION']).astype(int)

output_excel_destination = "local_pharma_replenishment_plan.xlsx"
final_actionable_blueprint.to_excel(output_excel_destination, index=False)

print(f"\n>>> SUCCESS! File generated: '{os.path.abspath(output_excel_destination)}'\n")
print(final_actionable_blueprint[['unique_id', 'ds', 'FINAL_SUGGESTED_ORDER_QUANTITY', 'APPLIED_LOGIC_RULE']].head(6))
