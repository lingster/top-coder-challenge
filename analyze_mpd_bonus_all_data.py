import json
import pandas as pd
import numpy as np

# --- Functions to simulate current calculate_reimbursement.py logic ---
def get_current_script_logistics(days, miles, receipts_total):
    # Per Diem
    current_per_diem_rate = 0.0
    daily_receipts = receipts_total / days if days > 0 else 0.0 # Ensure float division
    if days >= 11:
        if daily_receipts < 30.0: current_per_diem_rate = 50.0
        elif daily_receipts < 75.0: current_per_diem_rate = 60.0
        else: current_per_diem_rate = 65.0
    elif days >= 8: # Trips 8-10 days
        if daily_receipts < 20.0:
            current_per_diem_rate = 60.0
        elif miles > 800 and daily_receipts > 20.0: # Needs to be strictly > 20
            current_per_diem_rate = 75.0
        else:
            current_per_diem_rate = 75.0
    else: # Trips 1-7 days
        current_per_diem_rate = 100.0

    calculated_per_diem_total = days * current_per_diem_rate
    if days == 5:
        calculated_per_diem_total += 50.0

    # Baseline Mileage (0.58/0.50)
    calculated_mileage_reimbursement = 0.0
    if miles > 0: # Ensure miles is positive
        if miles <= 100:
            calculated_mileage_reimbursement = miles * 0.58
        else:
            calculated_mileage_reimbursement = (100 * 0.58) + ((miles - 100) * 0.50)

    # Receipt Reimbursement
    calculated_receipt_reimbursement = 0.0
    if receipts_total < 20.00 and days > 1: # strictly < 20
        calculated_receipt_reimbursement = -10.0
    elif receipts_total <= 500:
        calculated_receipt_reimbursement = receipts_total * 0.60
    elif receipts_total <= 1000:
        calculated_receipt_reimbursement = receipts_total * 0.50
    elif receipts_total <= 1500:
        calculated_receipt_reimbursement = receipts_total * 0.40
    else: # > $1500
        calculated_receipt_reimbursement = receipts_total * 0.30

    # High Effort Bonus (existing)
    calculated_high_effort_bonus = 0.0
    if days > 6 and days < 11 and miles > 800: # days 7,8,9,10
        # Bonus is NOT applied if (days is 8,9,10 AND daily_receipts < 20 AND miles > 800)
        is_penalized_per_diem_for_high_effort_low_spend = (days >= 8 and daily_receipts < 20.0 and miles > 800)
        if not is_penalized_per_diem_for_high_effort_low_spend:
             calculated_high_effort_bonus = 350.0

    return round(calculated_per_diem_total,2), round(calculated_mileage_reimbursement,2), round(calculated_receipt_reimbursement,2), round(calculated_high_effort_bonus,2)

# --- Main analysis ---
with open('public_cases.json', 'r') as f:
    cases_data = json.load(f)

df = pd.json_normalize(cases_data)
df.columns = df.columns.str.replace('input.', '', regex=False)
df.reset_index(inplace=True)
df.rename(columns={'index': 'case_id'}, inplace=True)


df['total_receipts_amount'] = df['total_receipts_amount'].astype(float)
df['miles_traveled'] = df['miles_traveled'].astype(float)
df['trip_duration_days'] = df['trip_duration_days'].astype(int)
df['expected_output'] = df['expected_output'].astype(float)
df = df[df['trip_duration_days'] > 0].copy() # Ensure valid days for calculations and use .copy()

# Calculate all components from current script logic
script_calcs = df.apply(
    lambda row: get_current_script_logistics(row['trip_duration_days'], row['miles_traveled'], row['total_receipts_amount']),
    axis=1, result_type='expand'
)
df[['calc_per_diem', 'calc_mileage', 'calc_receipts', 'calc_he_bonus']] = script_calcs

df['script_total_sans_mileage'] = df['calc_per_diem'] + df['calc_receipts'] + df['calc_he_bonus']
df['data_driven_mileage_comp'] = df['expected_output'] - df['script_total_sans_mileage']
df['unexplained_mileage_diff'] = df['data_driven_mileage_comp'] - df['calc_mileage']
df['miles_per_day'] = (df['miles_traveled'] / df['trip_duration_days']).round(1)

analysis_summary = []
analysis_summary.append(f"Analyzed {len(df)} trips from public_cases.json (after ensuring days > 0).")

df_filtered_for_analysis = df[df['miles_traveled'] > 0].copy()
df_filtered_for_analysis = df_filtered_for_analysis[
    (df_filtered_for_analysis['unexplained_mileage_diff'] > -500) & (df_filtered_for_analysis['unexplained_mileage_diff'] < 500)
].copy() # Use .copy()
analysis_summary.append(f"Retained {len(df_filtered_for_analysis)} trips after filtering zero-mile trips and extreme unexplained_mileage_diff outliers (between -$500 and +$500).")


if not df_filtered_for_analysis.empty:
    analysis_summary.append("\n--- Unexplained Mileage Difference by Miles/Day Bin ---")
    bins = [0, 100, 150, 175, 200, 225, 250, 300, np.inf]
    labels = ['0-99', '100-149', '150-174', '175-199 (Sweet Spot Lower)', '200-224 (Sweet Spot Upper)', '225-249 (Post Sweet Spot)', '250-299', '300+']
    df_filtered_for_analysis.loc[:, 'mpd_bin'] = pd.cut(df_filtered_for_analysis['miles_per_day'], bins=bins, labels=labels, right=False) # Use .loc for assignment

    # Convert mpd_bin to category before groupby, include observed=False
    df_filtered_for_analysis.loc[:, 'mpd_bin'] = df_filtered_for_analysis['mpd_bin'].astype('category')
    grouped_analysis = df_filtered_for_analysis.groupby('mpd_bin', observed=False)['unexplained_mileage_diff'].agg(['median', 'mean', 'count', 'min', 'max']).reset_index()
    analysis_summary.append(grouped_analysis.to_markdown(index=False))

    analysis_summary.append("\n--- Overall Statistics for Unexplained Mileage Difference (Filtered) ---")
    analysis_summary.append(f"Median: ${df_filtered_for_analysis['unexplained_mileage_diff'].median():.2f}")
    analysis_summary.append(f"Mean: ${df_filtered_for_analysis['unexplained_mileage_diff'].mean():.2f}")
    analysis_summary.append(f"Std Dev: ${df_filtered_for_analysis['unexplained_mileage_diff'].std():.2f}")

    sweet_spot_data = df_filtered_for_analysis[
        df_filtered_for_analysis['mpd_bin'].isin(['175-199 (Sweet Spot Lower)', '200-224 (Sweet Spot Upper)'])
    ].copy() # Use .copy()
    if not sweet_spot_data.empty:
        analysis_summary.append("\n--- Context for Sweet Spot Bins (175-224 miles/day) ---")
        analysis_summary.append(f"Number of cases in sweet spot bins: {len(sweet_spot_data)}")
        analysis_summary.append(f"Median 'calc_mileage' (baseline $0.58/$0.50) in sweet spot: ${sweet_spot_data['calc_mileage'].median():.2f}")
        analysis_summary.append(f"Median 'unexplained_mileage_diff' in sweet spot: ${sweet_spot_data['unexplained_mileage_diff'].median():.2f}")

        sweet_spot_data_for_ratio = sweet_spot_data[sweet_spot_data['calc_mileage'].notna() & (sweet_spot_data['calc_mileage'] != 0)].copy() # Avoid division by zero/NaN
        if not sweet_spot_data_for_ratio.empty:
            sweet_spot_data_for_ratio.loc[:, 'unexplained_as_pct_of_calc'] = \
                (sweet_spot_data_for_ratio['unexplained_mileage_diff'] / sweet_spot_data_for_ratio['calc_mileage']) * 100
            analysis_summary.append(f"Median 'unexplained_mileage_diff' as % of 'calc_mileage' in sweet spot: {sweet_spot_data_for_ratio['unexplained_as_pct_of_calc'].median():.2f}%")
        else:
            analysis_summary.append("No valid data (non-zero calc_mileage) in sweet spot for percentage calculation.")

else:
    analysis_summary.append("\nNo data available for binned analysis after filtering.")

with open("summary_task2.md", "a") as f:
    f.write("\n".join(analysis_summary) + "\n")

print("Broader efficiency bonus analysis script finished. Results in summary_task2.md")
