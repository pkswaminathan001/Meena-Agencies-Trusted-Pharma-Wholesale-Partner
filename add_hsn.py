import pandas as pd

# HSN codes for pharma (as of Sept 2025)
HSN_MAP = {
    "Paracetamol": ("3004", "5"),
    "Amoxicillin": ("3004", "5"),
    "Ibuprofen": ("3004", "5"),
    "Metformin": ("3004", "5"),
    "Atorvastatin": ("3004", "5"),
    "Omeprazole": ("3004", "5"),
    "Cetirizine": ("3004", "5"),
    "Azithromycin": ("3004", "5"),
    "Cough Syrup": ("3004", "5"),
    "Insulin": ("3004", "5"),
    "Salbutamol": ("3004", "5"),
    "ORS Powder": ("3004", "5"),
}

df = pd.read_csv("inventory.csv")

# Add HSN columns if missing
if "hsn_code" not in df.columns:
    def get_hsn(name):
        for key, (hsn, rate) in HSN_MAP.items():
            if key.lower() in name.lower():
                return hsn
        return "3004"
    df["hsn_code"] = df["medicine_name"].apply(get_hsn)

if "gst_rate" not in df.columns:
    df["gst_rate"] = 5

df.to_csv("inventory.csv", index=False)
print(f"✅ Added HSN codes to {len(df)} medicines")
print(f"   Sample: {df[['medicine_name', 'hsn_code', 'gst_rate']].head(3).to_string()}")
