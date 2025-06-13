import json
import pandas as pd
import numpy as np

# --- Function to calculate BASELINE mileage reimbursement from current script (0.58/0.50) ---
def calculate_baseline_mileage_reimbursement(miles):
    if miles <= 0:
        return 0.0
    if miles <= 100:
        return round(miles * 0.58, 2)
    else:
        return round((100 * 0.58) + ((miles - 100) * 0.50), 2)

# --- Function to calculate per diem (consistent with previous analyses) ---
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
        else:
            current_per_diem_rate = 75.0
    else: # Trips 1-7 days
        current_per_diem_rate = 100.0
    per_diem_total = days * current_per_diem_rate
    if days == 5:
        per_diem_total += 50.0
    return round(per_diem_total, 2)

# --- Main analysis ---
with open('public_cases.json', 'r') as f:
    cases_data = json.load(f)

# df = pd.json_normalize(cases_data) # Original line from prompt
# Replaced Case ID generation from prompt with reset_index approach
df = pd.json_normalize(cases_data)
df.columns = df.columns.str.replace('input.', '', regex=False)
df.reset_index(inplace=True) # Add index as a column
df.rename(columns={'index': 'case_id'}, inplace=True) # Rename index column to 'case_id'


df['total_receipts_amount'] = df['total_receipts_amount'].astype(float)
df['miles_traveled'] = df['miles_traveled'].astype(float)
df['trip_duration_days'] = df['trip_duration_days'].astype(int)
df['expected_output'] = df['expected_output'].astype(float)

# Filter for receipts < $20.00 and non-zero miles (same as previous successful filter)
mileage_focus_cases = df[
    (df['total_receipts_amount'] < 20.00) & (df['miles_traveled'] > 0) & (df['trip_duration_days'] > 0)
].copy()

analysis_summary = []
if not mileage_focus_cases.empty:
    mileage_focus_cases.loc[:, 'assumed_per_diem'] = mileage_focus_cases.apply(
        lambda row: calculate_current_per_diem_total(row['trip_duration_days'], row['miles_traveled'], row['total_receipts_amount']), axis=1
    )

    mileage_focus_cases.loc[:, 'estimated_receipt_reimb'] = 0.0
    condition_penalty = (mileage_focus_cases['total_receipts_amount'] > 0) & \
                        (mileage_focus_cases['total_receipts_amount'] < 20) & \
                        (mileage_focus_cases['trip_duration_days'] > 1)
    mileage_focus_cases.loc[condition_penalty, 'estimated_receipt_reimb'] = -10.0

    mileage_focus_cases.loc[:, 'data_driven_mileage_reimbursement'] = mileage_focus_cases['expected_output'] - \
                                                               mileage_focus_cases['assumed_per_diem'] - \
                                                               mileage_focus_cases['estimated_receipt_reimb']

    mileage_focus_cases.loc[:, 'baseline_calc_mileage_reimbursement'] = mileage_focus_cases['miles_traveled'].apply(calculate_baseline_mileage_reimbursement)

    mileage_focus_cases.loc[:, 'potential_bonus_or_error'] = mileage_focus_cases['data_driven_mileage_reimbursement'] - mileage_focus_cases['baseline_calc_mileage_reimbursement']

    mileage_focus_cases.loc[:, 'miles_per_day'] = (mileage_focus_cases['miles_traveled'] / mileage_focus_cases['trip_duration_days']).round(1)

    mileage_focus_cases_for_bonus = mileage_focus_cases[mileage_focus_cases['data_driven_mileage_reimbursement'] >= 0].copy() # Ensure .copy()
    analysis_summary.append(f"Retained {len(mileage_focus_cases_for_bonus)} cases (out of {len(mileage_focus_cases)}) with non-negative data-driven mileage reimbursement for bonus analysis.")

    if not mileage_focus_cases_for_bonus.empty:
        analysis_summary.append("\n--- Potential Bonus Analysis (Data-Driven Reimb vs. Baseline 0.58/0.50 Reimb) ---")
        analysis_summary.append(mileage_focus_cases_for_bonus[['case_id', 'trip_duration_days', 'miles_traveled', 'miles_per_day', 'data_driven_mileage_reimbursement', 'baseline_calc_mileage_reimbursement', 'potential_bonus_or_error']].sort_values(by='miles_per_day').to_markdown(index=False))

        sweet_spot_cases = mileage_focus_cases_for_bonus[
            (mileage_focus_cases_for_bonus['miles_per_day'] >= 175) & (mileage_focus_cases_for_bonus['miles_per_day'] <= 225)
        ].copy() # Ensure .copy()
        outside_sweet_spot_cases = mileage_focus_cases_for_bonus[
            (mileage_focus_cases_for_bonus['miles_per_day'] < 175) | (mileage_focus_cases_for_bonus['miles_per_day'] > 225)
        ].copy() # Ensure .copy()

        analysis_summary.append("\n\n--- Bonus/Error Statistics by Miles-Per-Day ---")
        if not sweet_spot_cases.empty:
            analysis_summary.append(f"Sweet Spot (175-225 miles/day) - Count: {len(sweet_spot_cases)}")
            analysis_summary.append(f"  Median Potential Bonus/Error: ${sweet_spot_cases['potential_bonus_or_error'].median():.2f}")
            analysis_summary.append(f"  Mean Potential Bonus/Error: ${sweet_spot_cases['potential_bonus_or_error'].mean():.2f}")
            analysis_summary.append(f"  Min/Max Potential Bonus/Error: ${sweet_spot_cases['potential_bonus_or_error'].min():.2f} / ${sweet_spot_cases['potential_bonus_or_error'].max():.2f}")
        else:
            analysis_summary.append("No cases found in the 175-225 miles/day sweet spot.")

        if not outside_sweet_spot_cases.empty:
            analysis_summary.append(f"Outside Sweet Spot - Count: {len(outside_sweet_spot_cases)}")
            analysis_summary.append(f"  Median Potential Bonus/Error: ${outside_sweet_spot_cases['potential_bonus_or_error'].median():.2f}")
            analysis_summary.append(f"  Mean Potential Bonus/Error: ${outside_sweet_spot_cases['potential_bonus_or_error'].mean():.2f}")
        else:
            analysis_summary.append("No cases found outside the sweet spot (all were inside, or no cases total).")

        if not sweet_spot_cases.empty: # Check again before trying to use it
            sweet_spot_cases.loc[:, 'apparent_rate'] = sweet_spot_cases['data_driven_mileage_reimbursement'] / sweet_spot_cases['miles_traveled']
            analysis_summary.append(f"Sweet Spot (175-225 miles/day) - Median Apparent Rate: ${sweet_spot_cases['apparent_rate'].median():.3f}")

        if not outside_sweet_spot_cases.empty: # Check again
            # Ensure miles_traveled is not zero for this division
            outside_sweet_spot_cases_safe = outside_sweet_spot_cases[outside_sweet_spot_cases['miles_traveled'] > 0].copy()
            if not outside_sweet_spot_cases_safe.empty:
                outside_sweet_spot_cases_safe.loc[:, 'apparent_rate'] = outside_sweet_spot_cases_safe['data_driven_mileage_reimbursement'] / outside_sweet_spot_cases_safe['miles_traveled']
                analysis_summary.append(f"Outside Sweet Spot - Median Apparent Rate: ${outside_sweet_spot_cases_safe['apparent_rate'].median():.3f}")
            else:
                analysis_summary.append("Outside Sweet Spot - No cases with miles_traveled > 0 for rate calculation.")


    else:
        analysis_summary.append("\nNo valid cases for bonus analysis after filtering for non-negative data-driven mileage reimbursement.")
else:
    analysis_summary.append("\nNo cases found matching criteria (receipts < $20.00, miles > 0, days > 0) for efficiency bonus analysis.")

with open("summary_task2.md", "a") as f:
    f.write("\n".join(analysis_summary) + "\n")

print("Efficiency bonus analysis script finished. Results in summary_task2.md")
