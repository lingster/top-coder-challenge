import json
import pandas as pd

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

df = pd.json_normalize(cases)
# Rename columns: 'input.trip_duration_days' becomes 'trip_duration_days', etc.
# 'case_id' and 'expected_output' remain as they are.
df.columns = df.columns.str.replace('input.', '', regex=False)

# Ensure correct data types
df['total_receipts_amount'] = df['total_receipts_amount'].astype(float)
df['miles_traveled'] = df['miles_traveled'].astype(float)
df['trip_duration_days'] = df['trip_duration_days'].astype(int)
df['expected_output'] = df['expected_output'].astype(float)

# Filter for low miles and low receipts
# Criteria: miles_traveled <= 10 and total_receipts_amount <= 10
per_diem_focus_cases = df[
    (df['miles_traveled'] <= 10) & (df['total_receipts_amount'] <= 10)
].copy()

# Avoid division by zero for days
per_diem_focus_cases_valid_days = per_diem_focus_cases[per_diem_focus_cases['trip_duration_days'] > 0].copy()

print("--- Per Diem Focus Cases (miles <= 10, receipts <= $10) ---")
print(f"Found {len(per_diem_focus_cases_valid_days)} such cases.")

analysis_summary = []
analysis_summary.append("## Analysis of Filtered Data")

if not per_diem_focus_cases_valid_days.empty:
    per_diem_focus_cases_valid_days.loc[:, 'apparent_daily_rate'] = per_diem_focus_cases_valid_days['expected_output'] / per_diem_focus_cases_valid_days['trip_duration_days']
    per_diem_focus_cases_valid_days.loc[:, 'apparent_daily_rate'] = per_diem_focus_cases_valid_days['apparent_daily_rate'].round(2)

    # Sort by days for easier analysis
    per_diem_focus_cases_valid_days = per_diem_focus_cases_valid_days.sort_values(by='trip_duration_days')

    # Ensure columns exist before trying to print them, especially if the dataframe could be empty or have unexpected columns
    columns_to_print = ['case_id', 'trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'apparent_daily_rate']
    existing_columns_to_print = [col for col in columns_to_print if col in per_diem_focus_cases_valid_days.columns]
    print(per_diem_focus_cases_valid_days[existing_columns_to_print])

    # Group by trip_duration_days and look at common apparent_daily_rate
    print("\n--- Apparent Daily Rates by Trip Duration (Median) ---")
    median_rates = per_diem_focus_cases_valid_days.groupby('trip_duration_days')['apparent_daily_rate'].median()
    print(median_rates)

    analysis_summary.append(f"Found {len(per_diem_focus_cases_valid_days)} cases with miles <= 10 and receipts <= $10.")

    short_trips_1_7 = per_diem_focus_cases_valid_days[per_diem_focus_cases_valid_days['trip_duration_days'] <= 7]
    if not short_trips_1_7.empty:
        median_rate_1_7 = short_trips_1_7['apparent_daily_rate'].median()
        analysis_summary.append(f"- For trips 1-7 days (count: {len(short_trips_1_7)}), median apparent daily rate: ${median_rate_1_7:.2f}.")
        if abs(median_rate_1_7 - 100) < 5: # Allow some variance
            analysis_summary.append("  - This aligns reasonably with the current $100/day for short trips.")
        else:
            analysis_summary.append(f"  - This differs from the current $100/day. Median: ${median_rate_1_7:.2f}")
    else:
        analysis_summary.append("- No trips of 1-7 days found in the filtered set.")

    medium_trips_8_10 = per_diem_focus_cases_valid_days[
        (per_diem_focus_cases_valid_days['trip_duration_days'] >= 8) & (per_diem_focus_cases_valid_days['trip_duration_days'] <= 10)
    ]
    if not medium_trips_8_10.empty:
        median_rate_8_10 = medium_trips_8_10['apparent_daily_rate'].median()
        analysis_summary.append(f"- For trips 8-10 days (count: {len(medium_trips_8_10)}), median apparent daily rate: ${median_rate_8_10:.2f}.")
        if abs(median_rate_8_10 - 60) < 5 :
             analysis_summary.append("  - This aligns reasonably with the current $60/day (low receipt/miles condition).")
        elif abs(median_rate_8_10 - 75) < 5 :
             analysis_summary.append("  - This aligns reasonably with the current $75/day (default/high effort condition).")
        else:
            analysis_summary.append(f"  - This differs from current rates ($60 or $75). Median: ${median_rate_8_10:.2f}")
    else:
        analysis_summary.append("- No trips of 8-10 days found in the filtered set.")

    long_trips_11_plus = per_diem_focus_cases_valid_days[per_diem_focus_cases_valid_days['trip_duration_days'] >= 11]
    if not long_trips_11_plus.empty:
        median_rate_11_plus = long_trips_11_plus['apparent_daily_rate'].median()
        analysis_summary.append(f"- For trips 11+ days (count: {len(long_trips_11_plus)}), median apparent daily rate: ${median_rate_11_plus:.2f}.")
        if abs(median_rate_11_plus - 50) < 5 :
            analysis_summary.append("  - This aligns reasonably with the current $50/day (very low daily receipts condition).")
        elif abs(median_rate_11_plus - 60) < 5 :
            analysis_summary.append("  - This aligns reasonably with the current $60/day (low-mid daily receipts condition).")
        else:
            analysis_summary.append(f"  - This differs from current rates ($50, $60, $65). Median: ${median_rate_11_plus:.2f}")
    else:
        analysis_summary.append("- No trips of 11+ days found in the filtered set.")

    five_day_trips = per_diem_focus_cases_valid_days[per_diem_focus_cases_valid_days['trip_duration_days'] == 5].copy()
    if not five_day_trips.empty:
        # Assuming $100/day base for 5-day trips from current logic for comparison
        five_day_trips.loc[:, 'expected_without_bonus_approx'] = 5 * 100
        five_day_trips.loc[:, 'apparent_bonus'] = five_day_trips['expected_output'] - five_day_trips['expected_without_bonus_approx']
        median_bonus_5_day = five_day_trips['apparent_bonus'].median()
        analysis_summary.append(f"- For 5-day trips (count: {len(five_day_trips)}), median apparent bonus over $100/day base: ${median_bonus_5_day:.2f}.")
        if abs(median_bonus_5_day - 50) < 10: # Allow variance
            analysis_summary.append("  - This is consistent with the +$50 bonus for 5-day trips.")
        else:
            analysis_summary.append(f"  - This differs from the +$50 bonus. Median bonus: ${median_bonus_5_day:.2f}")
    else:
        analysis_summary.append("- No 5-day trips found in the filtered set for bonus verification.")

    with open("summary_task1.md", "a") as f:
        f.write("\n".join(analysis_summary) + "\n")
        f.write("\n--- Raw Filtered Data (first 20) ---\n")
        # Check if df is not empty before calling to_markdown
        if not per_diem_focus_cases_valid_days.empty:
            f.write(per_diem_focus_cases_valid_days[existing_columns_to_print].head(20).to_markdown(index=False))
            f.write("\n")
        f.write("\n--- Median Apparent Daily Rates by Trip Duration ---\n")
        # Check if median_rates is not empty before calling to_markdown
        if not median_rates.empty:
            f.write(median_rates.to_markdown())
            f.write("\n")

else: # if per_diem_focus_cases_valid_days is empty
    analysis_summary.append(f"Found {len(per_diem_focus_cases_valid_days)} cases with miles <= 10 and receipts <= $10. No data to analyze for per diem specifics under these strict criteria.")
    with open("summary_task1.md", "a") as f:
        f.write("\n".join(analysis_summary) + "\n")
        f.write("\nNo specific per diem rates could be derived due to lack of matching cases under the current strict filter.\n")

print("Analysis complete. Results appended to summary_task1.md")
