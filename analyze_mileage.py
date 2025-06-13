import json
import pandas as pd
import numpy as np

# --- Functions to simulate current calculate_reimbursement.py logic for Per Diem ---
# This is crucial for subtracting the assumed per diem component accurately.
# WARNING: This is a simplified mirror and must be kept in sync with actual per diem logic if it changes.
def calculate_current_per_diem_total(days, miles, receipts):
    current_per_diem_rate = 0.0
    # Ensure days is not zero to prevent ZeroDivisionError for daily_receipts
    daily_receipts = receipts / days if days > 0 else 0

    if days >= 11: # "Very long" trips
        if daily_receipts < 30.0: current_per_diem_rate = 50.0
        elif daily_receipts < 75.0: current_per_diem_rate = 60.0
        else: current_per_diem_rate = 65.0
    elif days >= 8: # Trips 8-10 days
        # Adjusted logic based on current calculate_reimbursement.py
        if daily_receipts < 20.0: # This condition seems to take precedence for low receipts
            current_per_diem_rate = 60.0
        elif miles > 800 and daily_receipts > 20.0: # High effort bonus
            current_per_diem_rate = 75.0
        # elif miles <= 800 and daily_receipts > 90: # This was an error in prompt, likely meant for other conditions
        #    current_per_diem_rate = 60.0
        else: # Default for 8-10 days if not penalized and no high effort
            current_per_diem_rate = 75.0
    else: # Trips 1-7 days
        current_per_diem_rate = 100.0

    per_diem_total = days * current_per_diem_rate
    if days == 5:
        per_diem_total += 50.0 # 5-day bonus
    return per_diem_total

# --- Main analysis ---
with open('public_cases.json', 'r') as f:
    cases = json.load(f)
df = pd.json_normalize(cases)
df.columns = df.columns.str.replace('input.', '', regex=False)
# Add a case_id based on index for reference
df.reset_index(inplace=True)
df.rename(columns={'index': 'case_id'}, inplace=True)

df['total_receipts_amount'] = df['total_receipts_amount'].astype(float)
df['miles_traveled'] = df['miles_traveled'].astype(float)
df['trip_duration_days'] = df['trip_duration_days'].astype(int)
df['expected_output'] = df['expected_output'].astype(float)

# Filter for minimal receipts (e.g., <= $1.00, as $0 might be too restrictive)
# and non-zero miles and valid trip_duration_days
mileage_focus_cases = df[
    (df['total_receipts_amount'] <= 1.00) &
    (df['miles_traveled'] > 0) &
    (df['trip_duration_days'] > 0) # Ensure days > 0 for per diem calculation
].copy()

print(f"--- Found {len(mileage_focus_cases)} cases with receipts <= $1.00, miles > 0 and days > 0 ---")

analysis_summary = []
analysis_summary.append("## Mileage Analysis with Minimal Receipts (<= $1.00)")
analysis_summary.append(f"Found {len(mileage_focus_cases)} such cases.")

if not mileage_focus_cases.empty:
    mileage_focus_cases['assumed_per_diem'] = mileage_focus_cases.apply(
        lambda row: calculate_current_per_diem_total(row['trip_duration_days'], row['miles_traveled'], row['total_receipts_amount']),
        axis=1
    )

    mileage_focus_cases['estimated_receipt_reimb'] = 0.0
    condition_penalty = (mileage_focus_cases['total_receipts_amount'] > 0) & (mileage_focus_cases['total_receipts_amount'] < 20) & (mileage_focus_cases['trip_duration_days'] > 1)
    mileage_focus_cases.loc[condition_penalty, 'estimated_receipt_reimb'] = -10.0

    mileage_focus_cases['approx_mileage_reimbursement'] = mileage_focus_cases['expected_output'] - mileage_focus_cases['assumed_per_diem'] - mileage_focus_cases['estimated_receipt_reimb']

    # Avoid division by zero for apparent_rate_per_mile if miles_traveled is somehow zero (though filtered)
    mileage_focus_cases['apparent_rate_per_mile'] = 0.0
    non_zero_miles_mask = mileage_focus_cases['miles_traveled'] != 0
    mileage_focus_cases.loc[non_zero_miles_mask, 'apparent_rate_per_mile'] = (mileage_focus_cases.loc[non_zero_miles_mask, 'approx_mileage_reimbursement'] / mileage_focus_cases.loc[non_zero_miles_mask, 'miles_traveled']).round(3)

    mileage_focus_cases_filtered = mileage_focus_cases[
        (mileage_focus_cases['apparent_rate_per_mile'] > 0) & (mileage_focus_cases['apparent_rate_per_mile'] < 2.0)
    ].copy()

    analysis_summary.append(f"Retained {len(mileage_focus_cases_filtered)} cases after filtering out 0, negative, or extreme apparent mileage rates (>$2.0/mile).")

    analysis_summary.append("\n--- Data (receipts <= $1, miles > 0, filtered rates) ---")
    # Using generated case_id for reference
    analysis_summary.append(mileage_focus_cases_filtered[['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'assumed_per_diem', 'estimated_receipt_reimb', 'approx_mileage_reimbursement', 'apparent_rate_per_mile']].sort_values(by='miles_traveled').head(20).to_markdown(index=False))

    analysis_summary.append("\n\n--- Tier Analysis (based on current code $0.58/$0.50) ---")
    under_100_miles = mileage_focus_cases_filtered[mileage_focus_cases_filtered['miles_traveled'] <= 100]
    over_100_miles = mileage_focus_cases_filtered[mileage_focus_cases_filtered['miles_traveled'] > 100].copy() # Use .copy()

    if not under_100_miles.empty:
        analysis_summary.append(f"For trips <= 100 miles (count: {len(under_100_miles)}):")
        analysis_summary.append(f"  Median apparent rate: ${under_100_miles['apparent_rate_per_mile'].median():.3f}")
        analysis_summary.append(f"  Mean apparent rate: ${under_100_miles['apparent_rate_per_mile'].mean():.3f}")
        analysis_summary.append(f"  Min/Max apparent rate: ${under_100_miles['apparent_rate_per_mile'].min():.3f} / ${under_100_miles['apparent_rate_per_mile'].max():.3f}")
    else:
        analysis_summary.append("No cases found for <= 100 miles in filtered set.")

    if not over_100_miles.empty:
        analysis_summary.append(f"For trips > 100 miles (count: {len(over_100_miles)}):")
        analysis_summary.append(f"  Median apparent rate: ${over_100_miles['apparent_rate_per_mile'].median():.3f}")
        analysis_summary.append(f"  Mean apparent rate: ${over_100_miles['apparent_rate_per_mile'].mean():.3f}")
        analysis_summary.append(f"  Min/Max apparent rate: ${over_100_miles['apparent_rate_per_mile'].min():.3f} / ${over_100_miles['apparent_rate_per_mile'].max():.3f}")

        # Calculate rate for excess miles only if (miles_traveled - 100) is not zero
        valid_excess_miles = over_100_miles['miles_traveled'] - 100 != 0
        over_100_miles.loc[valid_excess_miles, 'rate_for_excess_miles'] = ((over_100_miles.loc[valid_excess_miles, 'approx_mileage_reimbursement'] - (100 * 0.58)) / (over_100_miles.loc[valid_excess_miles, 'miles_traveled'] - 100)).round(3)
        if valid_excess_miles.any():
             analysis_summary.append(f"  Median rate for miles >100 (after first 100 at $0.58): ${over_100_miles.loc[valid_excess_miles, 'rate_for_excess_miles'].median():.3f}")
        else:
            analysis_summary.append("  No cases with miles significantly over 100 to calculate excess rate meaningfully.")
    else:
        analysis_summary.append("No cases found for > 100 miles in filtered set.")

    # Efficiency: miles_per_day
    # Ensure trip_duration_days is not zero before division
    valid_days_for_efficiency = mileage_focus_cases_filtered['trip_duration_days'] > 0
    mileage_focus_cases_filtered_eff = mileage_focus_cases_filtered[valid_days_for_efficiency].copy()
    if not mileage_focus_cases_filtered_eff.empty:
        mileage_focus_cases_filtered_eff['miles_per_day'] = (mileage_focus_cases_filtered_eff['miles_traveled'] / mileage_focus_cases_filtered_eff['trip_duration_days']).round(1)
        analysis_summary.append("\n\n--- Efficiency Analysis (Miles per Day vs. Apparent Rate) ---")
        analysis_summary.append(mileage_focus_cases_filtered_eff[['miles_per_day', 'apparent_rate_per_mile', 'trip_duration_days', 'miles_traveled']].sort_values(by='miles_per_day').head(20).to_markdown(index=False))

        bins = [0, 50, 100, 150, 200, 250, 300, np.inf]
        labels = ['0-50', '50-100', '100-150', '150-200', '200-250', '250-300', '300+']
        mileage_focus_cases_filtered_eff['mpd_bin'] = pd.cut(mileage_focus_cases_filtered_eff['miles_per_day'], bins=bins, labels=labels, right=False)
        analysis_summary.append("\nMedian apparent rate per mile by Miles-Per-Day bin:")
        analysis_summary.append(mileage_focus_cases_filtered_eff.groupby('mpd_bin')['apparent_rate_per_mile'].agg(['median', 'count']).to_markdown())
    else:
        analysis_summary.append("\nNo cases with valid trip_duration_days > 0 for efficiency analysis.")
else:
    analysis_summary.append("No cases found matching criteria (receipts <= $1.00, miles > 0, and days > 0).")

with open("summary_task2.md", "a") as f:
    f.write("\n".join(analysis_summary) + "\n")

print("Mileage analysis script finished. Results in summary_task2.md")
