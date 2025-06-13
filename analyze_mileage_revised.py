import json
import pandas as pd
import numpy as np

# --- Functions to simulate current calculate_reimbursement.py logic for Per Diem ---
def calculate_current_per_diem_total(days, miles, receipts):
    current_per_diem_rate = 0.0
    daily_receipts = receipts / days if days > 0 else 0
    if days >= 11:
        if daily_receipts < 30.0: current_per_diem_rate = 50.0
        elif daily_receipts < 75.0: current_per_diem_rate = 60.0
        else: current_per_diem_rate = 65.0
    elif days >= 8: # Trips 8-10 days
        if daily_receipts < 20.0:
            current_per_diem_rate = 60.0
        elif miles > 800 and daily_receipts > 20.0:
            current_per_diem_rate = 75.0
        # elif miles <= 800 and daily_receipts > 90: # This line from prompt seems less likely than general default
        #    current_per_diem_rate = 60.0
        else:
            current_per_diem_rate = 75.0
    else: # Trips 1-7 days
        current_per_diem_rate = 100.0
    per_diem_total = days * current_per_diem_rate
    if days == 5:
        per_diem_total += 50.0
    return per_diem_total

# --- Main analysis ---
with open('public_cases.json', 'r') as f:
    cases_data = json.load(f) # Renamed to avoid conflict

# Generate case_id
for i, case_obj in enumerate(cases_data):
    # case_obj['case_id'] = f"gen_id_{i}" # This was in prompt, but json_normalize handles original data better.
                                        # Instead, add index later if needed.
    pass


df = pd.json_normalize(cases_data)
df.columns = df.columns.str.replace('input.', '', regex=False)
# Add a case_id based on index for reference, as it's not in the source JSON
df.reset_index(inplace=True)
df.rename(columns={'index': 'case_id'}, inplace=True)


df['total_receipts_amount'] = df['total_receipts_amount'].astype(float)
df['miles_traveled'] = df['miles_traveled'].astype(float)
df['trip_duration_days'] = df['trip_duration_days'].astype(int)
df['expected_output'] = df['expected_output'].astype(float)

# Filter for receipts < $20.00 and non-zero miles
mileage_focus_cases = df[
    (df['total_receipts_amount'] < 20.00) & (df['miles_traveled'] > 0) & (df['trip_duration_days'] > 0)
].copy()

print(f"--- Found {len(mileage_focus_cases)} cases with receipts < $20.00, miles > 0 and days > 0 ---")

analysis_summary = []
analysis_summary.append("## Mileage Analysis with Receipts < $20.00")
analysis_summary.append(f"Found {len(mileage_focus_cases)} such cases.")

if not mileage_focus_cases.empty:
    mileage_focus_cases['assumed_per_diem'] = mileage_focus_cases.apply(
        lambda row: calculate_current_per_diem_total(row['trip_duration_days'], row['miles_traveled'], row['total_receipts_amount']),
        axis=1
    )

    mileage_focus_cases['estimated_receipt_reimb'] = 0.0
    condition_penalty = (mileage_focus_cases['total_receipts_amount'] > 0) & \
                        (mileage_focus_cases['total_receipts_amount'] < 20) & \
                        (mileage_focus_cases['trip_duration_days'] > 1)
    mileage_focus_cases.loc[condition_penalty, 'estimated_receipt_reimb'] = -10.0

    mileage_focus_cases['approx_mileage_reimbursement'] = mileage_focus_cases['expected_output'] - \
                                                          mileage_focus_cases['assumed_per_diem'] - \
                                                          mileage_focus_cases['estimated_receipt_reimb']

    mileage_focus_cases['apparent_rate_per_mile'] = 0.0 # Initialize
    non_zero_miles_mask = mileage_focus_cases['miles_traveled'] != 0
    mileage_focus_cases.loc[non_zero_miles_mask, 'apparent_rate_per_mile'] = \
        (mileage_focus_cases.loc[non_zero_miles_mask, 'approx_mileage_reimbursement'] / mileage_focus_cases.loc[non_zero_miles_mask, 'miles_traveled']).round(3)


    mileage_focus_cases_filtered = mileage_focus_cases[
        (mileage_focus_cases['apparent_rate_per_mile'] >= 0) &
        (mileage_focus_cases['apparent_rate_per_mile'] < 2.0)
    ].copy()

    analysis_summary.append(f"Retained {len(mileage_focus_cases_filtered)} cases after filtering out negative or extreme apparent mileage rates (full count: {len(mileage_focus_cases)}).")
    analysis_summary.append("Cases with negative apparent rates might indicate other penalties or incorrect per diem assumptions for those specific cases.")

    if not mileage_focus_cases_filtered.empty:
        analysis_summary.append("\n--- Data (receipts < $20, miles > 0, filtered rates, first 20) ---")
        analysis_summary.append(mileage_focus_cases_filtered[['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'assumed_per_diem', 'estimated_receipt_reimb', 'approx_mileage_reimbursement', 'apparent_rate_per_mile']].sort_values(by='miles_traveled').head(20).to_markdown(index=False))

        analysis_summary.append("\n\n--- Tier Analysis (based on current code $0.58/$0.50) ---")
        under_100_miles = mileage_focus_cases_filtered[mileage_focus_cases_filtered['miles_traveled'] <= 100].copy()
        over_100_miles = mileage_focus_cases_filtered[mileage_focus_cases_filtered['miles_traveled'] > 100].copy()

        if not under_100_miles.empty:
            analysis_summary.append(f"For trips <= 100 miles (count: {len(under_100_miles)}):")
            analysis_summary.append(f"  Median apparent rate: ${under_100_miles['apparent_rate_per_mile'].median():.3f}")
            analysis_summary.append(f"  Mean apparent rate: ${under_100_miles['apparent_rate_per_mile'].mean():.3f}")
        else:
            analysis_summary.append("No cases found for <= 100 miles in filtered set.")

        if not over_100_miles.empty:
            analysis_summary.append(f"For trips > 100 miles (count: {len(over_100_miles)}):")
            analysis_summary.append(f"  Median apparent rate (overall): ${over_100_miles['apparent_rate_per_mile'].median():.3f}")
            analysis_summary.append(f"  Mean apparent rate (overall): ${over_100_miles['apparent_rate_per_mile'].mean():.3f}")

            over_100_miles.loc[:, 'rate_for_excess_miles'] = 0.0 # Initialize
            # Ensure (miles_traveled - 100) is not zero before division
            valid_excess_miles_mask = (over_100_miles['miles_traveled'] - 100) != 0
            over_100_miles.loc[valid_excess_miles_mask, 'rate_for_excess_miles'] = \
                ((over_100_miles.loc[valid_excess_miles_mask, 'approx_mileage_reimbursement'] - (100 * 0.58)) / \
                 (over_100_miles.loc[valid_excess_miles_mask, 'miles_traveled'] - 100)).round(3)

            sensible_excess_rates = over_100_miles[over_100_miles['rate_for_excess_miles'] >= 0].copy() # Use .copy() here
            if not sensible_excess_rates.empty:
                 analysis_summary.append(f"  Median rate for miles >100 (after first 100 at $0.58, filtered for sensible): ${sensible_excess_rates['rate_for_excess_miles'].median():.3f} (count: {len(sensible_excess_rates)})")
            else:
                analysis_summary.append("  No sensible data for median rate for miles >100 after adjustments.")
        else:
            analysis_summary.append("No cases found for > 100 miles in filtered set.")

        mileage_focus_cases_filtered_eff = mileage_focus_cases_filtered.copy() # Use already filtered DF
        if not mileage_focus_cases_filtered_eff.empty and mileage_focus_cases_filtered_eff['trip_duration_days'].gt(0).all(): # ensure days > 0
            mileage_focus_cases_filtered_eff.loc[:,'miles_per_day'] = (mileage_focus_cases_filtered_eff['miles_traveled'] / mileage_focus_cases_filtered_eff['trip_duration_days']).round(1)
            analysis_summary.append("\n\n--- Efficiency Analysis (Miles per Day vs. Apparent Rate) ---")

            bins = [0, 50, 100, 150, 175, 200, 225, 250, 300, np.inf]
            labels = ['0-49', '50-99', '100-149', '150-174', '175-199', '200-224', '225-249', '250-299', '300+']
            mileage_focus_cases_filtered_eff.loc[:,'mpd_bin'] = pd.cut(mileage_focus_cases_filtered_eff['miles_per_day'], bins=bins, labels=labels, right=False)
            analysis_summary.append("\nMedian apparent rate per mile by Miles-Per-Day bin:")
            # Ensure 'mpd_bin' is treated as categorical for groupby if it's not already
            mileage_focus_cases_filtered_eff['mpd_bin'] = mileage_focus_cases_filtered_eff['mpd_bin'].astype('category')
            analysis_summary.append(mileage_focus_cases_filtered_eff.groupby('mpd_bin', observed=False)['apparent_rate_per_mile'].agg(['median', 'count', 'mean']).to_markdown())
        else:
            analysis_summary.append("\nNo valid data for efficiency analysis (miles_per_day).")
    else:
        analysis_summary.append("\nNo cases with positive/non-extreme apparent mileage rates found.")
else:
    analysis_summary.append("\nNo cases found matching criteria (receipts < $20.00, miles > 0, days > 0).")

with open("summary_task2.md", "a") as f:
    f.write("\n".join(analysis_summary) + "\n")

print("Revised mileage analysis script finished. Results in summary_task2.md")
