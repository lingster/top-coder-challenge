import json
import pandas as pd
import numpy as np

# --- START: Logic from current calculate_reimbursement.py (scores 18464.00) ---
# This function should return the total calculated reimbursement AND whether HEB was applied + its amount
def calculate_reimbursement_and_identify_heb(days, miles, receipts_total):
    # Per Diem
    calculated_per_diem_total = 0.0
    daily_receipts_for_per_diem = receipts_total / float(days) if days > 0 else 0.0 # Ensure float
    if days >= 11:
        if daily_receipts_for_per_diem < 30.0: calculated_per_diem_total = days * 50.0
        elif daily_receipts_for_per_diem < 75.0: calculated_per_diem_total = days * 60.0
        else: calculated_per_diem_total = days * 65.0
    elif days >= 8: # 8-10 days
        if miles > 800 and daily_receipts_for_per_diem > 20.0: calculated_per_diem_total = days * 75.0
        elif miles <= 800 and daily_receipts_for_per_diem > 90.0: calculated_per_diem_total = days * 60.0
        elif daily_receipts_for_per_diem < 20.0: calculated_per_diem_total = days * 60.0
        else: calculated_per_diem_total = days * 75.0
    else: # 1-7 days
        calculated_per_diem_total = days * 100.0
    if days == 5: calculated_per_diem_total += 50.0

    # Mileage calculation
    calculated_mileage_reimbursement = 0.0
    if miles > 0:
        if miles <= 100: calculated_mileage_reimbursement = miles * 0.58
        else: calculated_mileage_reimbursement = (100 * 0.58) + ((miles - 100) * 0.50)

    miles_per_day = 0.0
    if days > 0 and miles > 0: miles_per_day = float(miles) / float(days) # Ensure float
    if miles_per_day > 0 and miles_per_day < 100: calculated_mileage_reimbursement += 50.0
    if miles_per_day >= 200 and miles_per_day < 225: calculated_mileage_reimbursement += 60.0
    if miles_per_day >= 300: calculated_mileage_reimbursement += 120.0

    # Receipt Reimbursement
    calculated_receipt_reimbursement = 0.0
    if receipts_total < 20.00 and days > 1: calculated_receipt_reimbursement = -25.0
    elif receipts_total <= 100: calculated_receipt_reimbursement = receipts_total * 0.30
    elif receipts_total <= 500: calculated_receipt_reimbursement = receipts_total * 0.60
    elif receipts_total <= 1000: calculated_receipt_reimbursement = receipts_total * 0.50
    elif receipts_total <= 1500: calculated_receipt_reimbursement = receipts_total * 0.45
    else: calculated_receipt_reimbursement = receipts_total * 0.35

    total_reimbursement_before_heb = calculated_per_diem_total + calculated_mileage_reimbursement + calculated_receipt_reimbursement

    # High Effort Bonus (existing)
    applied_heb_amount = 0.0
    gets_heb = False
    if days > 6 and days < 11 and miles > 800: # 7,8,9,10 days
        is_penalized_pd_for_high_effort_low_spend = (days >= 8 and daily_receipts_for_per_diem < 20.0 and miles > 800)
        if not is_penalized_pd_for_high_effort_low_spend:
             applied_heb_amount = 350.0
             gets_heb = True

    final_total_reimbursement = total_reimbursement_before_heb + applied_heb_amount
    return round(final_total_reimbursement,2), gets_heb, applied_heb_amount, round(miles_per_day,1)
# --- END: Logic from current calculate_reimbursement.py ---

with open('public_cases.json', 'r') as f:
    cases_data = json.load(f)

df = pd.json_normalize(cases_data)
df.columns = df.columns.str.replace('input.', '', regex=False)
df.reset_index(inplace=True) # Add index as a column
df.rename(columns={'index': 'case_id'}, inplace=True) # Rename index column to 'case_id'


df['total_receipts_amount'] = df['total_receipts_amount'].astype(float)
df['miles_traveled'] = df['miles_traveled'].astype(float)
df['trip_duration_days'] = df['trip_duration_days'].astype(int)
df['expected_output'] = df['expected_output'].astype(float)
df = df[df['trip_duration_days'] > 0].copy() # Use .copy()

# Calculate script output and HEB status for all cases
script_outputs = df.apply(
    lambda row: calculate_reimbursement_and_identify_heb(row['trip_duration_days'], row['miles_traveled'], row['total_receipts_amount']),
    axis=1, result_type='expand'
)
df[['script_calculated_output', 'gets_heb', 'applied_heb_amount', 'mpd']] = script_outputs
df['unexplained_error'] = df['expected_output'] - df['script_calculated_output']

analysis_summary = []
analysis_summary.append("## High Effort Bonus (HEB) Analysis")

heb_cases = df[df['gets_heb'] == True].copy() # Use .copy()
analysis_summary.append(f"Found {len(heb_cases)} cases that trigger the current HEB (+${heb_cases['applied_heb_amount'].iloc[0] if not heb_cases.empty else 350:.2f}).")
if not heb_cases.empty:
    analysis_summary.append("Error analysis for cases GETTING HEB:")
    analysis_summary.append(f"  Median unexplained_error: ${heb_cases['unexplained_error'].median():.2f}")
    analysis_summary.append(f"  Mean unexplained_error: ${heb_cases['unexplained_error'].mean():.2f}")
    analysis_summary.append(f"  Std Dev unexplained_error: ${heb_cases['unexplained_error'].std():.2f}")
    analysis_summary.append(f"  Min/Max error: ${heb_cases['unexplained_error'].min():.2f} / ${heb_cases['unexplained_error'].max():.2f}")
    analysis_summary.append("  Cases with largest errors (top 5 positive, bottom 5 negative):")
    analysis_summary.append(heb_cases.sort_values(by='unexplained_error', ascending=False)[['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'script_calculated_output', 'unexplained_error']].head().to_markdown(index=False))
    analysis_summary.append(heb_cases.sort_values(by='unexplained_error', ascending=True)[['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'script_calculated_output', 'unexplained_error']].head().to_markdown(index=False))

analysis_summary.append("\n--- Analysis of Kevin's MPD Sweet Spot (175-225 mpd) NOT getting HEB ---")
sweet_spot_no_heb = df[
    (df['mpd'] >= 175) & (df['mpd'] <= 225) & (df['gets_heb'] == False)
].copy() # Use .copy()
analysis_summary.append(f"Found {len(sweet_spot_no_heb)} cases in MPD sweet spot (175-225) that DO NOT get HEB.")
if not sweet_spot_no_heb.empty:
    analysis_summary.append("Error analysis for MPD sweet spot cases WITHOUT HEB:")
    analysis_summary.append(f"  Median unexplained_error: ${sweet_spot_no_heb['unexplained_error'].median():.2f}")
    analysis_summary.append(f"  Mean unexplained_error: ${sweet_spot_no_heb['unexplained_error'].mean():.2f}")
    analysis_summary.append("  Top 5 largest positive errors (potential for more bonus):")
    analysis_summary.append(sweet_spot_no_heb.sort_values(by='unexplained_error', ascending=False)[['case_id', 'trip_duration_days', 'miles_traveled', 'mpd', 'total_receipts_amount', 'expected_output', 'script_calculated_output', 'unexplained_error']].head().to_markdown(index=False))

# Overall error distribution
analysis_summary.append("\n--- Overall Unexplained Error Distribution (all cases) ---")
analysis_summary.append(f"Overall median unexplained_error: ${df['unexplained_error'].median():.2f}")
analysis_summary.append(f"Overall mean unexplained_error: ${df['unexplained_error'].mean():.2f}")

with open("summary_task5.md", "a") as f:
    f.write("\n".join(analysis_summary) + "\n")

print("HEB analysis script finished. Results in summary_task5.md")
