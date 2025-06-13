import json
import pandas as pd
import numpy as np

# --- Function to calculate BASELINE mileage reimbursement (0.58/0.50) ---
def calculate_baseline_mileage_reimbursement(miles):
    if miles <= 0: return 0.0
    if miles <= 100: return round(miles * 0.58, 2)
    else: return round((100 * 0.58) + ((miles - 100) * 0.50), 2)

# --- Function to calculate per diem (consistent) ---
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

# --- Function to check if existing High Effort Bonus applies ---
# daily_receipts_for_bonus_check is total_receipts / days
def check_high_effort_bonus(days, miles, daily_receipts_for_bonus_check):
    bonus_amount = 0.0
    if days > 6 and days < 11 and miles > 800: # Primary condition: days 7,8,9,10 & miles > 800
        # Secondary condition: Bonus is NOT applied if (days is 8,9,10 AND daily_receipts < 20 AND miles > 800)
        if not (days >= 8 and daily_receipts_for_bonus_check < 20.0 and miles > 800):
             bonus_amount = 350.0
    return bonus_amount


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

    mileage_focus_cases.loc[:, 'data_driven_mileage_reimbursement_plus_any_other_bonus'] = \
        mileage_focus_cases['expected_output'] - \
        mileage_focus_cases['assumed_per_diem'] - \
        mileage_focus_cases['estimated_receipt_reimb']

    mileage_focus_cases.loc[:, 'baseline_calc_mileage_reimbursement'] = \
        mileage_focus_cases['miles_traveled'].apply(calculate_baseline_mileage_reimbursement)

    mileage_focus_cases.loc[:, 'daily_receipts_val'] = \
        mileage_focus_cases['total_receipts_amount'] / mileage_focus_cases['trip_duration_days']

    mileage_focus_cases.loc[:, 'gets_high_effort_bonus'] = mileage_focus_cases.apply(
        lambda row: check_high_effort_bonus(row['trip_duration_days'], row['miles_traveled'], row['daily_receipts_val']), axis=1
    )

    mileage_focus_cases.loc[:, 'potential_bonus_or_error_BEFORE_HE_adj'] = \
        mileage_focus_cases['data_driven_mileage_reimbursement_plus_any_other_bonus'] - \
        mileage_focus_cases['baseline_calc_mileage_reimbursement']

    mileage_focus_cases.loc[:, 'potential_bonus_or_error_AFTER_HE_adj'] = \
        mileage_focus_cases['potential_bonus_or_error_BEFORE_HE_adj'] - mileage_focus_cases['gets_high_effort_bonus']

    mileage_focus_cases.loc[:, 'miles_per_day'] = \
        (mileage_focus_cases['miles_traveled'] / mileage_focus_cases['trip_duration_days']).round(1)

    analysis_summary.append(f"Analyzed {len(mileage_focus_cases)} cases (receipts < $20).")
    analysis_summary.append("\n--- Effect of Existing High Effort Bonus ---")
    analysis_summary.append(mileage_focus_cases[['case_id', 'trip_duration_days', 'miles_traveled', 'miles_per_day',
                                                 'total_receipts_amount', 'daily_receipts_val',
                                                 'baseline_calc_mileage_reimbursement',
                                                 'data_driven_mileage_reimbursement_plus_any_other_bonus',
                                                 'potential_bonus_or_error_BEFORE_HE_adj',
                                                 'gets_high_effort_bonus',
                                                 'potential_bonus_or_error_AFTER_HE_adj'
                                                 ]].sort_values(by=['gets_high_effort_bonus', 'miles_traveled'], ascending=[False, True]).to_markdown(index=False)) # Sort to see bonus cases first

    cases_getting_HE_bonus = mileage_focus_cases[mileage_focus_cases['gets_high_effort_bonus'] > 0]
    analysis_summary.append(f"\nNumber of cases in this set that get the High Effort Bonus: {len(cases_getting_HE_bonus)}")

    analysis_summary.append("\n\n--- Statistics for 'Potential Bonus/Error AFTER HE Adjustment' ---")
    analysis_summary.append(f"Median: ${mileage_focus_cases['potential_bonus_or_error_AFTER_HE_adj'].median():.2f}")
    analysis_summary.append(f"Mean: ${mileage_focus_cases['potential_bonus_or_error_AFTER_HE_adj'].mean():.2f}")
    analysis_summary.append(f"Min: ${mileage_focus_cases['potential_bonus_or_error_AFTER_HE_adj'].min():.2f}")
    analysis_summary.append(f"Max: ${mileage_focus_cases['potential_bonus_or_error_AFTER_HE_adj'].max():.2f}")

    mileage_focus_cases.loc[:,'mileage_reimb_post_HE_bonus_accounted'] = mileage_focus_cases['baseline_calc_mileage_reimbursement'] + mileage_focus_cases['potential_bonus_or_error_AFTER_HE_adj']

    # Calculate apparent rate only for rows where miles_traveled > 0 to avoid division by zero or inf
    valid_miles_mask = mileage_focus_cases['miles_traveled'] > 0
    mileage_focus_cases_valid_miles = mileage_focus_cases[valid_miles_mask].copy() # Use .copy()

    if not mileage_focus_cases_valid_miles.empty:
        mileage_focus_cases_valid_miles.loc[:,'apparent_rate_post_HE_bonus_accounted'] = \
            mileage_focus_cases_valid_miles['mileage_reimb_post_HE_bonus_accounted'] / mileage_focus_cases_valid_miles['miles_traveled']

        valid_rates_post_HE = mileage_focus_cases_valid_miles[mileage_focus_cases_valid_miles['mileage_reimb_post_HE_bonus_accounted'] >=0]['apparent_rate_post_HE_bonus_accounted']
        if not valid_rates_post_HE.empty:
            analysis_summary.append(f"Median Apparent Rate (after accounting for existing HE bonus, on valid rates): ${valid_rates_post_HE.median():.3f}")
        else:
            analysis_summary.append("No valid apparent rates (>=0) after HE bonus adjustment for median calculation.")
    else:
        analysis_summary.append("No cases with miles_traveled > 0 to calculate apparent rate after HE bonus.")

else:
    analysis_summary.append("\nNo cases found matching criteria (receipts < $20.00, miles > 0, days > 0).")

with open("summary_task2.md", "a") as f:
    f.write("\n".join(analysis_summary) + "\n")

print("Analysis of existing High Effort Bonus effect script finished. Results in summary_task2.md")
