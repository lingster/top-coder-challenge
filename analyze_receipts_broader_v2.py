import json
import pandas as pd
import numpy as np

# --- START: Logic from current calculate_reimbursement.py (that scores 18464.00) ---
def get_current_script_components(days, miles, receipts): # receipts is the original input name
    # Per Diem
    calculated_per_diem_total = 0.0
    # daily_receipts is used for per diem rate determination logic
    daily_receipts_for_per_diem = receipts / float(days) if days > 0 else 0.0 # Ensure float
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

    if days == 5: # 5-day bonus
        calculated_per_diem_total += 50.0

    # Mileage calculation (including MPD bonuses)
    calculated_mileage_reimbursement = 0.0
    if miles > 0: # Calculate base mileage only if miles were traveled
        if miles <= 100:
            calculated_mileage_reimbursement = miles * 0.58
        else:
            calculated_mileage_reimbursement = (100 * 0.58) + ((miles - 100) * 0.50)

    miles_per_day = 0.0
    if days > 0 and miles > 0: # miles > 0 condition for MPD bonuses
        miles_per_day = float(miles) / float(days) # Ensure float

    # MPD bonuses
    if miles_per_day > 0 and miles_per_day < 100:
        calculated_mileage_reimbursement += 50.0
    if miles_per_day >= 200 and miles_per_day < 225:
        calculated_mileage_reimbursement += 60.0
    if miles_per_day >= 300:
        calculated_mileage_reimbursement += 120.0

    # High Effort Bonus
    calculated_high_effort_bonus = 0.0
    if days > 6 and days < 11 and miles > 800:
        is_penalized_pd_for_high_effort_low_spend = (days >= 8 and daily_receipts_for_per_diem < 20.0 and miles > 800)
        if not is_penalized_pd_for_high_effort_low_spend:
             calculated_high_effort_bonus = 350.0

    # Current Script's Receipt Logic (for baseline comparison if needed)
    script_receipt_reimbursement = 0.0
    if receipts < 20.00 and days > 1:
        script_receipt_reimbursement = -25.0 # Current best penalty
    elif receipts <= 100: # New tier
        script_receipt_reimbursement = receipts * 0.30
    elif receipts <= 500: # This tier is now $100.01 - $500
        script_receipt_reimbursement = receipts * 0.60
    elif receipts <= 1000:
        script_receipt_reimbursement = receipts * 0.50
    elif receipts <= 1500: # Rate changed to 0.45
        script_receipt_reimbursement = receipts * 0.45
    else: # > $1500, rate changed to 0.35
        script_receipt_reimbursement = receipts * 0.35

    return round(calculated_per_diem_total,2), round(calculated_mileage_reimbursement,2), round(calculated_high_effort_bonus,2), round(script_receipt_reimbursement, 2)
# --- END: Logic from current calculate_reimbursement.py ---

# --- Main analysis (similar to analyze_receipts_broader.py) ---
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

receipt_focus_cases = df[df['miles_traveled'] <= 100].copy()
receipt_focus_cases = receipt_focus_cases[receipt_focus_cases['total_receipts_amount'] >= 0].copy() # Include zero receipts

analysis_summary = []
analysis_summary.append(f"Re-evaluating with script scoring 18464.00. Filter: Miles <= 100.")
analysis_summary.append(f"Found {len(receipt_focus_cases)} cases matching criteria.")

if not receipt_focus_cases.empty:
    script_calcs = receipt_focus_cases.apply(
        lambda row: get_current_script_components(row['trip_duration_days'], row['miles_traveled'], row['total_receipts_amount']),
        axis=1, result_type='expand'
    )
    receipt_focus_cases[['calc_per_diem', 'calc_mileage_incl_mpd', 'calc_he_bonus', 'calc_script_receipt_reimb']] = script_calcs

    receipt_focus_cases.loc[:, 'data_driven_receipt_comp'] = receipt_focus_cases['expected_output'] - \
                                                      receipt_focus_cases['calc_per_diem'] - \
                                                      receipt_focus_cases['calc_mileage_incl_mpd'] - \
                                                      receipt_focus_cases['calc_he_bonus']

    receipt_focus_cases.loc[:, 'data_driven_receipt_rate'] = receipt_focus_cases.apply(
        lambda x: (x['data_driven_receipt_comp'] / x['total_receipts_amount']) if x['total_receipts_amount'] > 0 else 0, axis=1 # Check for > 0 before division
    ).round(3)

    analysis_summary.append("\n--- Data-Driven Receipt Component (Sorted by Receipts, first 30) ---")
    analysis_summary.append(receipt_focus_cases[['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount',
                                                 'calc_script_receipt_reimb', 'data_driven_receipt_comp'
                                                 ]].sort_values(by='total_receipts_amount').head(30).to_markdown(index=False))

    analysis_summary.append("\n\n--- Data-Driven Receipt Rate vs. Total Receipts (Binned) ---")
    rate_analysis_cases = receipt_focus_cases[receipt_focus_cases['total_receipts_amount'] > 0].copy()
    bins = [0, 20, 50, 100, 200, 500, 1000, 1500, 2000, np.inf]
    labels = ['(0)-19.99', '20-49.99', '50-99.99', '100-199.99', '200-499.99', '500-999.99', '1000-1499.99', '1500-1999.99', '2000+']
    if not rate_analysis_cases.empty:
        rate_analysis_cases.loc[:, 'receipt_bin'] = pd.cut(rate_analysis_cases['total_receipts_amount'], bins=bins, labels=labels, right=False)
        sane_rates = rate_analysis_cases[ (rate_analysis_cases['data_driven_receipt_rate'] <= 2) & (rate_analysis_cases['data_driven_receipt_rate'] >= -2) ].copy()

        if not sane_rates.empty: # Check if sane_rates has data
            sane_rates.loc[:, 'receipt_bin'] = sane_rates['receipt_bin'].astype('category')
            diminishing_analysis = sane_rates.groupby('receipt_bin', observed=False)['data_driven_receipt_rate'].agg(['median', 'mean', 'count']).reset_index()
            analysis_summary.append(diminishing_analysis.to_markdown(index=False))
        else:
            analysis_summary.append("No 'sane_rates' data available for binned diminishing returns analysis after filtering.")
    else:
        analysis_summary.append("No cases with receipts > 0 for rate analysis.")

    analysis_summary.append("\n\n--- Focus on Negative Data-Driven Receipt Components ---")
    negative_receipt_comp_cases = receipt_focus_cases[receipt_focus_cases['data_driven_receipt_comp'] < 0].copy() # Use .copy()
    analysis_summary.append(f"Found {len(negative_receipt_comp_cases)} cases where data_driven_receipt_comp is negative.")
    if not negative_receipt_comp_cases.empty:
        analysis_summary.append("Examples of negative data_driven_receipt_comp (first 10, sorted by magnitude):")
        analysis_summary.append(negative_receipt_comp_cases[['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'calc_per_diem', 'calc_mileage_incl_mpd', 'calc_he_bonus', 'expected_output', 'data_driven_receipt_comp']].sort_values(by='data_driven_receipt_comp').head(10).to_markdown(index=False))
        analysis_summary.append(f"Median 'data_driven_receipt_comp' for these negative cases: {negative_receipt_comp_cases['data_driven_receipt_comp'].median():.2f}")

else:
    analysis_summary.append("\nNo cases found matching criteria (miles <= 100).")

with open("summary_task3.md", "a") as f:
    f.write("\n".join(analysis_summary) + "\n")

print("Re-evaluation receipt analysis script finished. Results in summary_task3.md")
