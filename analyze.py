# analyze.py
# Key finding: km_since_service (r=0.40), avg_daily_km (r=0.25), and load_factor (r=0.22) are
# the only factors that separate cars that broke down from those that did not. Total odometer
# mileage (r=0.002) and age (r=-0.001) are near-zero predictors — high-mileage or older cars
# are NOT more likely to break down; cars that are overdue AND driven hard AND heavily loaded are.

import pandas as pd

# ── 1. Load ────────────────────────────────────────────────────────────────────
df = pd.read_csv("fleet_history.csv")

# ── 2. Compare group means (broke_down=1 vs broke_down=0) ─────────────────────
numeric_cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

group_means = df.groupby("broke_down")[numeric_cols].mean()

print("=" * 65)
print("Group means: stable cars (0) vs cars that broke down (1)")
print("=" * 65)
print(group_means.T.rename(columns={0: "stable", 1: "broke_down"}).to_string(float_format="%.2f"))

corr = (
    df.corr(numeric_only=True)["broke_down"]
    .drop("broke_down")
    .sort_values(key=abs, ascending=False)
)
print()
print("Pearson correlation with broke_down (absolute value, descending):")
for col, val in corr.items():
    marker = "  <-- predictive" if abs(val) >= 0.20 else "  (near-zero, NOT a driver)"
    print(f"  {col:<22} {val:+.4f}{marker}")

print()
print("Conclusion: km_since_service, avg_daily_km, and load_factor are the")
print("only meaningful predictors. Odometer total and age are irrelevant.")

# ── 3. Normalised risk score (0–100) ──────────────────────────────────────────
# Each of the three predictive columns is min-max scaled to [0, 1], then the
# weighted sum is rescaled to [0, 100].
# Weights reflect relative correlation strength: 0.40 : 0.25 : 0.22 ≈ 4 : 2.5 : 2
WEIGHTS = {
    "km_since_service": 4.0,
    "avg_daily_km":     2.5,
    "load_factor":      2.0,
}

scored = df.copy()

for col, weight in WEIGHTS.items():
    col_min = scored[col].min()
    col_max = scored[col].max()
    scored[f"{col}_norm"] = (scored[col] - col_min) / (col_max - col_min)

total_weight = sum(WEIGHTS.values())
scored["risk_score"] = (
    sum(scored[f"{col}_norm"] * w for col, w in WEIGHTS.items()) / total_weight * 100
)

# ── 4. Top-10 highest-risk vehicles ───────────────────────────────────────────
top10 = (
    scored[["car_id", "km_since_service", "avg_daily_km", "load_factor", "broke_down", "risk_score"]]
    .sort_values("risk_score", ascending=False)
    .head(10)
    .reset_index(drop=True)
)
top10.index += 1   # rank from 1

print()
print("=" * 65)
print("Top 10 highest-risk vehicles")
print("=" * 65)
print(
    f"{'#':<4} {'car_id':<12} {'km_since_svc':>13} {'avg_daily_km':>13}"
    f" {'load':>6} {'actual':>7} {'risk':>7}"
)
print("-" * 65)
for rank, row in top10.iterrows():
    actual = "BROKE" if row["broke_down"] == 1 else "ok"
    print(
        f"{rank:<4} {row['car_id']:<12} {row['km_since_service']:>13,.0f}"
        f" {row['avg_daily_km']:>13,.0f}"
        f" {row['load_factor']:>6.2f}"
        f" {actual:>7}"
        f" {row['risk_score']:>6.1f}%"
    )

# ── 5. Summary ─────────────────────────────────────────────────────────────────
print()
print("=" * 65)
print("Summary")
print("=" * 65)
total = len(scored)
high_risk = scored[scored["risk_score"] >= 70]
breakdown_rate_high = high_risk["broke_down"].mean() * 100
breakdown_rate_all  = scored["broke_down"].mean() * 100
print(f"Fleet size                : {total} cars")
print(f"Overall breakdown rate    : {breakdown_rate_all:.1f}%")
print(f"Cars with risk score >= 70 : {len(high_risk)} cars")
print(f"Breakdown rate in that group: {breakdown_rate_high:.1f}%")
print()
print("The 80% km-wear rule flags cars AFTER they are nearly worn.")
print("This risk score flags overdue + heavily used cars BEFORE they hit 80%.")
