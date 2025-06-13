import json
import pandas as pd
import numpy as np

# --- Functions to simulate current calculate_reimbursement.py logic (Score 19803.00) ---
def get_current_script_components(days, miles, receipts_total):
    calculated_per_diem_total = 0.0
    daily_receipts_for_per_diem = receipts_total / float(days) if days > 0 else 0.0
    if days >= 11:
        if daily_receipts_for_per_diem < 30.0: calculated_per_diem_total = days * 50.0
        elif daily_receipts_for_per_diem < 75.0: calculated_per_diem_total = days * 60.0
        else: calculated_per_diem_total = days * 65.0
    elif days >= 8:
        if miles > 800 and daily_receipts_for_per_diem > 20.0: calculated_per_diem_total = days * 75.0
        elif miles <= 800 and daily_receipts_for_per_diem > 90.0: calculated_per_diem_total = days * 60.0
        elif daily_receipts_for_per_diem < 20.0: calculated_per_diem_total = days * 60.0
        else: calculated_per_diem_total = days * 75.0
    else: # 1-7 days
        calculated_per_diem_total = days * 100.0
    if days == 5: calculated_per_diem_total += 50.0

    calculated_mileage_reimbursement = 0.0
    if miles > 0:
        if miles <= 100: calculated_mileage_reimbursement = miles * 0.58
        else: calculated_mileage_reimbursement = (100 * 0.58) + ((miles - 100) * 0.50)

    miles_per_day = 0.0
    if days > 0 and miles > 0: miles_per_day = float(miles) / float(days)
    if miles_per_day > 0 and miles_per_day < 100: calculated_mileage_reimbursement += 50.0
    if miles_per_day >= 200 and miles_per_day < 225: calculated_mileage_reimbursement += 60.0
    if miles_per_day >= 300: calculated_mileage_reimbursement += 120.0

    calculated_high_effort_bonus = 0.0
    if days > 6 and days < 11 and miles > 800:
        is_penalized_pd = (days >= 8 and daily_receipts_for_per_diem < 20.0 and miles > 800)
        if not is_penalized_pd: calculated_high_effort_bonus = 350.0

    script_receipt_reimbursement = 0.0
    if receipts_total < 20.00 and days > 1: script_receipt_reimbursement = -10.0
    elif receipts_total <= 500: script_receipt_reimbursement = receipts_total * 0.60
    elif receipts_total <= 1000: script_receipt_reimbursement = receipts_total * 0.50
    elif receipts_total <= 1500: script_receipt_reimbursement = receipts_total * 0.40
    else: script_receipt_reimbursement = receipts_total * 0.30

    return round(calculated_per_diem_total,2), round(calculated_mileage_reimbursement,2), round(calculated_high_effort_bonus,2), round(script_receipt_reimbursement,2)

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
df = df[df['trip_duration_days'] > 0].copy()

receipt_focus_cases = df[df['miles_traveled'] <= 100].copy()
receipt_focus_cases = receipt_focus_cases[receipt_focus_cases['total_receipts_amount'] > 0].copy()

analysis_summary = []
analysis_summary.append(f"## Receipt Analysis (Miles <= 100, Receipts > 0)")
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
        lambda x: (x['data_driven_receipt_comp'] / x['total_receipts_amount']) if x['total_receipts_amount'] != 0 else 0, axis=1
    ).round(3)
    receipt_focus_cases.loc[:, 'script_receipt_rate'] = receipt_focus_cases.apply(
        lambda x: (x['calc_script_receipt_reimb'] / x['total_receipts_amount']) if x['total_receipts_amount'] != 0 else 0, axis=1
    ).round(3)

    # Moved 'ends_49_99' column creation earlier
    receipt_focus_cases.loc[:, 'ends_49_99'] = receipt_focus_cases['total_receipts_amount'].apply(lambda x: True if f"{x:.2f}".endswith('.49') or f"{x:.2f}".endswith('.99') else False)

    analysis_summary.append("\n--- Comparison of Data-Driven vs. Script Receipt Component (Sorted by Receipts, first 30) ---")
    analysis_summary.append(receipt_focus_cases[['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount',
                                                 'calc_script_receipt_reimb', 'data_driven_receipt_comp',
                                                 'script_receipt_rate', 'data_driven_receipt_rate', 'ends_49_99' # Added for inspection
                                                 ]].sort_values(by='total_receipts_amount').head(30).to_markdown(index=False))

    analysis_summary.append("\n\n--- Diminishing Returns Check (Data-Driven Receipt Rate vs. Total Receipts) ---")
    bins = [0, 20, 50, 100, 200, 500, 1000, 1500, 2000, np.inf]
    labels = ['0-19.99', '20-49.99', '50-99.99', '100-199.99', '200-499.99', '500-999.99', '1000-1499.99', '1500-1999.99', '2000+']
    receipt_focus_cases.loc[:, 'receipt_bin'] = pd.cut(receipt_focus_cases['total_receipts_amount'], bins=bins, labels=labels, right=False)

    sane_rates = receipt_focus_cases[ (receipt_focus_cases['data_driven_receipt_rate'] <= 2) & (receipt_focus_cases['data_driven_receipt_rate'] >= -1) ].copy()

    if not sane_rates.empty:
        sane_rates.loc[:, 'receipt_bin'] = sane_rates['receipt_bin'].astype('category')
        diminishing_analysis = sane_rates.groupby('receipt_bin', observed=False)['data_driven_receipt_rate'].agg(['median', 'mean', 'count']).reset_index()
        analysis_summary.append(diminishing_analysis.to_markdown(index=False))
        analysis_summary.append(f"Overall median data-driven receipt rate (sane rates): {sane_rates['data_driven_receipt_rate'].median():.3f}")
        analysis_summary.append(f"Overall mean data-driven receipt rate (sane rates): {sane_rates['data_driven_receipt_rate'].mean():.3f}")
    else:
        analysis_summary.append("No 'sane_rates' data for binned diminishing returns analysis.")

    analysis_summary.append("\n\n--- Low Amount Penalty Check (-$10 for receipts > 0 & < $20 and days > 1) ---")
    penalty_candidates = receipt_focus_cases[
        (receipt_focus_cases['total_receipts_amount'] > 0) &
        (receipt_focus_cases['total_receipts_amount'] < 20) &
        (receipt_focus_cases['trip_duration_days'] > 1)
    ].copy()
    analysis_summary.append(f"Found {len(penalty_candidates)} cases potentially subject to -$10 penalty by script logic.")
    if not penalty_candidates.empty:
        analysis_summary.append("Data for these cases (script vs data-driven receipt component):")
        analysis_summary.append(penalty_candidates[['case_id', 'trip_duration_days', 'total_receipts_amount', 'calc_script_receipt_reimb', 'data_driven_receipt_comp']].head().to_markdown(index=False))
        analysis_summary.append(f"Median data_driven_receipt_comp for these penalty candidates: {penalty_candidates['data_driven_receipt_comp'].median():.2f}")

    analysis_summary.append("\n\n--- Rounding Bug Check (.49 or .99 endings) ---")
    # sane_rates now includes 'ends_49_99' because it was added to receipt_focus_cases before sane_rates was defined
    cases_ending_49_99_sane = sane_rates[sane_rates['ends_49_99'] == True]
    cases_not_ending_49_99_sane = sane_rates[sane_rates['ends_49_99'] == False]

    cases_ending_49_99_all = receipt_focus_cases[receipt_focus_cases['ends_49_99'] == True]
    cases_not_ending_49_99_all = receipt_focus_cases[receipt_focus_cases['ends_49_99'] == False]

    if not cases_ending_49_99_sane.empty:
        analysis_summary.append(f"Median data-driven rate for receipts ending .49/.99 (sane rates, count {len(cases_ending_49_99_sane)}): {cases_ending_49_99_sane['data_driven_receipt_rate'].median():.3f}")
    else:
        analysis_summary.append("No 'sane_rate' cases found with receipts ending .49/.99.")
    if not cases_not_ending_49_99_sane.empty:
        analysis_summary.append(f"Median data-driven rate for receipts NOT ending .49/.99 (sane rates, count {len(cases_not_ending_49_99_sane)}): {cases_not_ending_49_99_sane['data_driven_receipt_rate'].median():.3f}")
    else:
        analysis_summary.append("No 'sane_rate' cases found with receipts NOT ending .49/.99.")

    if not cases_ending_49_99_all.empty:
        analysis_summary.append(f"Median data_driven_receipt_comp for receipts ending .49/.99 (all focused, count {len(cases_ending_49_99_all)}): ${cases_ending_49_99_all['data_driven_receipt_comp'].median():.2f}")
    else:
        analysis_summary.append("No cases found with receipts ending .49/.99 in the focused set.")
    if not cases_not_ending_49_99_all.empty:
        analysis_summary.append(f"Median data_driven_receipt_comp for receipts NOT ending .49/.99 (all focused, count {len(cases_not_ending_49_99_all)}): ${cases_not_ending_49_99_all['data_driven_receipt_comp'].median():.2f}")
    else:
        analysis_summary.append("No cases found with receipts NOT ending .49/.99 in the focused set.")

else:
    analysis_summary.append("\nNo cases found matching criteria (miles <= 100, receipts > 0).")

with open("summary_task3.md", "a") as f:
    f.write("\n".join(analysis_summary) + "\n")

print("Broader receipt analysis script finished. Results in summary_task3.md")
