import json
import pandas as pd

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)
df = pd.json_normalize(cases)
df.columns = df.columns.str.replace('input.', '', regex=False)
# Add a case_id based on index for reference if needed, though not strictly used by analysis
df.reset_index(inplace=True)
df.rename(columns={'index': 'case_id'}, inplace=True)

df['total_receipts_amount'] = df['total_receipts_amount'].astype(float)
df['miles_traveled'] = df['miles_traveled'].astype(float)
df['trip_duration_days'] = df['trip_duration_days'].astype(int)
df['expected_output'] = df['expected_output'].astype(float)


# --- Attempt 1: Strictest possible (zero miles, zero receipts) ---
per_diem_focus_cases_v1 = df[
    (df['miles_traveled'] == 0) & (df['total_receipts_amount'] == 0)
].copy()
print(f"--- Found {len(per_diem_focus_cases_v1)} cases with miles == 0 AND receipts == 0 ---")
with open("summary_task1.md", "a") as f:
    f.write("\n### Filter: miles == 0 AND receipts == 0\n")
    if not per_diem_focus_cases_v1.empty:
        if 'trip_duration_days' in per_diem_focus_cases_v1.columns and per_diem_focus_cases_v1['trip_duration_days'].gt(0).any():
            valid_days_v1 = per_diem_focus_cases_v1[per_diem_focus_cases_v1['trip_duration_days'] > 0].copy()
            if not valid_days_v1.empty:
                valid_days_v1.loc[:, 'apparent_daily_rate'] = valid_days_v1['expected_output'] / valid_days_v1['trip_duration_days']
                valid_days_v1.loc[:, 'apparent_daily_rate'] = valid_days_v1['apparent_daily_rate'].round(2)
                # Removed 'case_id' from here as it's not in source JSON, using df-generated one if needed for other things
                print(valid_days_v1[['trip_duration_days', 'expected_output', 'apparent_daily_rate']].head())
                f.write(f"Found {len(valid_days_v1)} such cases with valid days.\n")
                f.write(valid_days_v1[['trip_duration_days', 'apparent_daily_rate']].groupby('trip_duration_days')['apparent_daily_rate'].agg(['median', 'count']).to_markdown() + "\n")
            else:
                print("No valid trip_duration_days > 0 in v1 results after filtering.")
                f.write("Found 0 such cases with valid trip_duration_days > 0.\n")
        else:
            print("No trip_duration_days > 0 in v1 results or column missing.")
            f.write("Found 0 such cases with valid trip_duration_days > 0.\n")
    else:
        f.write("Found 0 such cases.\n")


# --- Attempt 2: Relaxed filter (miles < 20 and receipts < 20) ---
per_diem_focus_cases_v2 = df[
    (df['miles_traveled'] < 20) & (df['total_receipts_amount'] < 20)
].copy()
print(f"--- Found {len(per_diem_focus_cases_v2)} cases with miles < 20 AND receipts < $20 ---")

analysis_summary_v2 = []
if not per_diem_focus_cases_v2.empty and 'trip_duration_days' in per_diem_focus_cases_v2.columns and per_diem_focus_cases_v2['trip_duration_days'].gt(0).any():
    per_diem_focus_cases_valid_days_v2 = per_diem_focus_cases_v2[per_diem_focus_cases_v2['trip_duration_days'] > 0].copy()

    if not per_diem_focus_cases_valid_days_v2.empty:
        per_diem_focus_cases_valid_days_v2.loc[:, 'mileage_est'] = per_diem_focus_cases_valid_days_v2['miles_traveled'] * 0.58
        per_diem_focus_cases_valid_days_v2.loc[:, 'apparent_daily_rate_raw'] = (per_diem_focus_cases_valid_days_v2['expected_output'] / per_diem_focus_cases_valid_days_v2['trip_duration_days']).round(2)
        per_diem_focus_cases_valid_days_v2.loc[:, 'output_minus_mileage_est'] = per_diem_focus_cases_valid_days_v2['expected_output'] - per_diem_focus_cases_valid_days_v2['mileage_est']
        per_diem_focus_cases_valid_days_v2.loc[:, 'daily_rate_minus_mileage_est'] = (per_diem_focus_cases_valid_days_v2['output_minus_mileage_est'] / per_diem_focus_cases_valid_days_v2['trip_duration_days']).round(2)

        per_diem_focus_cases_valid_days_v2 = per_diem_focus_cases_valid_days_v2.sort_values(by='trip_duration_days')

        analysis_summary_v2.append(f"Found {len(per_diem_focus_cases_valid_days_v2)} cases with miles < 20 and receipts < $20 and valid days.")
        analysis_summary_v2.append("\n--- Data (miles < 20, receipts < $20) ---")
        # Removed 'case_id' from here, added df-generated 'case_id' for reference
        analysis_summary_v2.append(per_diem_focus_cases_valid_days_v2[['case_id','trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'apparent_daily_rate_raw', 'daily_rate_minus_mileage_est']].head(20).to_markdown(index=False))

        analysis_summary_v2.append("\n\n--- Median Apparent Daily Rates (Raw) by Trip Duration ---")
        median_rates_raw_v2 = per_diem_focus_cases_valid_days_v2.groupby('trip_duration_days')['apparent_daily_rate_raw'].agg(['median', 'count'])
        analysis_summary_v2.append(median_rates_raw_v2.to_markdown())

        analysis_summary_v2.append("\n\n--- Median Daily Rates (Output Minus Est. Mileage) by Trip Duration ---")
        median_rates_adj_v2 = per_diem_focus_cases_valid_days_v2.groupby('trip_duration_days')['daily_rate_minus_mileage_est'].agg(['median', 'count'])
        analysis_summary_v2.append(median_rates_adj_v2.to_markdown())

        analysis_summary_v2.append("\n\n--- Comparison with Current Code (using daily_rate_minus_mileage_est) ---")
        for days_cat, rate_expected_map in [
            ("1-7 days", {1:100, 2:100, 3:100, 4:100, 5:100, 6:100, 7:100}),
            ("8-10 days", {8:60, 9:60, 10:60}),
            ("11+ days", {11:50, 12:50, 13:50, 14:50, 15:50})
        ]:
            analysis_summary_v2.append(f"Category: {days_cat}")
            category_data = median_rates_adj_v2[median_rates_adj_v2.index.isin(rate_expected_map.keys())]
            if not category_data.empty:
                for day, data_row in category_data.iterrows():
                    expected_rate = rate_expected_map.get(day, "N/A")
                    analysis_summary_v2.append(f"  Day {day}: Median Rate (adj): ${data_row['median']:.2f} (Count: {data_row['count']}). Expected base rate (approx): ${expected_rate}")
            else:
                analysis_summary_v2.append(f"  No data for days in category: {days_cat}")

        five_day_trips_v2 = per_diem_focus_cases_valid_days_v2[per_diem_focus_cases_valid_days_v2['trip_duration_days'] == 5].copy()
        if not five_day_trips_v2.empty:
            five_day_trips_v2.loc[:, 'total_per_diem_est_from_adj_rate'] = five_day_trips_v2['daily_rate_minus_mileage_est'] * 5
            five_day_trips_v2.loc[:, 'apparent_total_bonus'] = five_day_trips_v2['total_per_diem_est_from_adj_rate'] - (100 * 5)
            median_bonus_5_day_v2 = five_day_trips_v2['apparent_total_bonus'].median()
            analysis_summary_v2.append(f"\n- For 5-day trips (count: {len(five_day_trips_v2)} in v2 filter), median apparent total bonus over $100/day base (using adj. rate): ${median_bonus_5_day_v2:.2f}.")
            if abs(median_bonus_5_day_v2 - 50) < 20:
                analysis_summary_v2.append("  - This is broadly consistent with the +$50 bonus.")
            else:
                analysis_summary_v2.append(f"  - This differs significantly from the +$50 bonus. Median bonus: ${median_bonus_5_day_v2:.2f}")
        else:
            analysis_summary_v2.append("\n- No 5-day trips found in the v2 filtered set for bonus verification.")
    else:
        analysis_summary_v2.append(f"Found {len(per_diem_focus_cases_valid_days_v2)} cases with miles < 20 and receipts < $20 but 0 with valid trip_duration_days > 0.")

else:
    analysis_summary_v2.append(f"Found 0 cases with miles < 20 and receipts < $20.")

with open("summary_task1.md", "a") as f:
    f.write("\n### Filter: miles < 20 AND receipts < $20\n")
    f.write("\n".join(analysis_summary_v2) + "\n")

print("Revised analysis complete. Results appended to summary_task1.md")
