import json
import pandas as pd
import numpy as np

def analyze_data():
    # Load the public cases data
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)

    # Convert to pandas DataFrame for easier analysis
    df = pd.json_normalize(public_cases)
    # Rename columns to remove "input." prefix
    df.columns = df.columns.str.replace("input.", "")
    df['total_receipts_amount'] = df['total_receipts_amount'].astype(float) # Ensure correct type

    print("--- Initial Data Analysis ---")

    # Task 1: Load and parse data (done)
    print(f"\nSuccessfully loaded {len(df)} records from public_cases.json")

    # Task 2: Descriptive statistics (done)
    print("\n--- Descriptive Statistics ---")
    for col in ['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output']:
        print(f"\nStatistics for {col}:")
        print(f"  Min: {df[col].min()}")
        print(f"  Max: {df[col].max()}")
        print(f"  Mean: {df[col].mean():.2f}")
        print(f"  Median: {df[col].median()}")
        print(f"  Std Dev: {df[col].std():.2f}")

    # Task 3: Group data by trip_duration_days (done)
    print("\n--- Analysis by Trip Duration (Averages) ---")
    duration_groups = df.groupby('trip_duration_days').agg(
        avg_expected_output=('expected_output', 'mean'),
        avg_miles_traveled=('miles_traveled', 'mean'),
        avg_total_receipts_amount=('total_receipts_amount', 'mean'),
        count_of_trips=('expected_output', 'count')
    ).reset_index()

    duration_groups['avg_expected_output'] = duration_groups['avg_expected_output'].round(2)
    duration_groups['avg_miles_traveled'] = duration_groups['avg_miles_traveled'].round(2)
    duration_groups['avg_total_receipts_amount'] = duration_groups['avg_total_receipts_amount'].round(2)
    print(duration_groups)

    # Task 4: Analyze mileage (done, with caveats about sample size for low-receipt)
    print("\n--- Mileage Analysis ---")
    low_receipt_trips = df[(df['total_receipts_amount'] < 10) & (df['miles_traveled'] > 0)].copy()
    print(f"\nFound {len(low_receipt_trips)} trips with receipts < $10 and miles > 0 for mileage analysis.")

    assumed_per_diem_for_mileage_analysis = 100 # From Lisa's interview as a base

    if not low_receipt_trips.empty:
        potential_per_diems = [50, 75, assumed_per_diem_for_mileage_analysis, 120]
        print("\nCalculating mileage rate with potential per diems (for low-receipt trips):")
        for ppd_val in potential_per_diems:
            # Ensure miles_traveled is not zero before division
            valid_mileage_trips = low_receipt_trips[low_receipt_trips['miles_traveled'] > 0]
            if not valid_mileage_trips.empty:
                mileage_rate_series = (valid_mileage_trips['expected_output'] - (valid_mileage_trips['trip_duration_days'] * ppd_val)) / valid_mileage_trips['miles_traveled']
                min_rate_str = f"{mileage_rate_series.min():.2f}" if not mileage_rate_series.empty else "N/A"
                max_rate_str = f"{mileage_rate_series.max():.2f}" if not mileage_rate_series.empty else "N/A"
                mean_rate_str = f"{mileage_rate_series.mean():.2f}" if not mileage_rate_series.empty else "N/A"
                median_rate_str = f"{mileage_rate_series.median():.2f}" if not mileage_rate_series.empty else "N/A"
                std_dev_rate_str = f"{mileage_rate_series.std():.2f}" if not mileage_rate_series.empty else "N/A"
            else:
                min_rate_str = max_rate_str = mean_rate_str = median_rate_str = std_dev_rate_str = "N/A (no valid trips)"

            print(f"\n  Potential Per Diem: ${ppd_val}")
            print(f"    Min mileage rate: {min_rate_str}")
            print(f"    Max mileage rate: {max_rate_str}")
            print(f"    Mean mileage rate: {mean_rate_str}")
            print(f"    Median mileage rate: {median_rate_str}")
            print(f"    Std Dev mileage rate: {std_dev_rate_str}")

        # Calculations for 'per_mile_reimbursement' using the assumed PPD
        low_receipt_trips_for_display = low_receipt_trips[low_receipt_trips['miles_traveled'] > 0].copy()
        low_receipt_trips_for_display.loc[:, 'per_diem_cost'] = low_receipt_trips_for_display['trip_duration_days'] * assumed_per_diem_for_mileage_analysis
        low_receipt_trips_for_display.loc[:, 'mileage_component'] = low_receipt_trips_for_display['expected_output'] - low_receipt_trips_for_display['per_diem_cost']
        low_receipt_trips_for_display.loc[:, 'per_mile_reimbursement'] = low_receipt_trips_for_display['mileage_component'] / low_receipt_trips_for_display['miles_traveled']

        print(f"\n--- Mileage Reimbursement per Mile (assuming ${assumed_per_diem_for_mileage_analysis}/day per diem for low-receipt trips) ---")
        mileage_analysis_display = low_receipt_trips_for_display[['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'per_mile_reimbursement']].sort_values(by='miles_traveled')

        print(mileage_analysis_display.head(10)) # Will show all 8 if that's the case
        if len(mileage_analysis_display) > 10: # Only print ... if more than 10
            print("...")
            print(mileage_analysis_display.tail(10))

    else:
        print("No trips found with receipts < $10 and miles > 0, parts of mileage analysis skipped.")

    # Tiered Mileage Rate Check (Lisa: ~0.58 for first 100 miles)
    # This part uses all trips to get a broader view, still very approximate
    print("\n--- Tiered Mileage Rate Check (using all trips, very approximate) ---")
    df_for_tiered_check = df[df['miles_traveled'] > 0].copy() # Avoid division by zero
    df_for_tiered_check.loc[:, 'mileage_component_approx'] = df_for_tiered_check['expected_output'] - (df_for_tiered_check['trip_duration_days'] * assumed_per_diem_for_mileage_analysis)
    df_for_tiered_check.loc[:, 'per_mile_reimbursement_approx'] = df_for_tiered_check['mileage_component_approx'] / df_for_tiered_check['miles_traveled']

    # Filter out negative/zero reimbursement rates as they are likely not representative of mileage rate itself
    df_for_tiered_check_positive = df_for_tiered_check[df_for_tiered_check['per_mile_reimbursement_approx'] > 0]

    first_100_miles = df_for_tiered_check_positive[df_for_tiered_check_positive['miles_traveled'] <= 100]
    over_100_miles = df_for_tiered_check_positive[df_for_tiered_check_positive['miles_traveled'] > 100]

    if not first_100_miles.empty:
        print(f"\nApprox. avg per_mile_reimbursement for trips <= 100 miles (all trips, positive rate, assumed ${assumed_per_diem_for_mileage_analysis}/day): {first_100_miles['per_mile_reimbursement_approx'].mean():.2f}")
        print(f"Approx. median per_mile_reimbursement for trips <= 100 miles: {first_100_miles['per_mile_reimbursement_approx'].median():.2f}")
        print(f"Number of such trips: {len(first_100_miles)}")
    else:
        print("\nNo trips found with <= 100 miles under these conditions for tiered rate check.")

    if not over_100_miles.empty:
        print(f"\nApprox. avg per_mile_reimbursement for trips > 100 miles (all trips, positive rate, assumed ${assumed_per_diem_for_mileage_analysis}/day): {over_100_miles['per_mile_reimbursement_approx'].mean():.2f}")
        print(f"Approx. median per_mile_reimbursement for trips > 100 miles: {over_100_miles['per_mile_reimbursement_approx'].median():.2f}")
        print(f"Number of such trips: {len(over_100_miles)}")
    else:
        print("\nNo trips found with > 100 miles under these conditions for tiered rate check.")

    # Task 5: Analyze receipts
    print("\n\n--- Receipt Analysis ---")
    # 5a: Broaden filter: trips of 3-5 days, mileage < 100 miles.
    receipt_analysis_trips = df[
        (df['trip_duration_days'] >= 3) & (df['trip_duration_days'] <= 5) &
        (df['miles_traveled'] < 100) &
        (df['total_receipts_amount'] > 1) # Min $1 receipt to avoid noise from tiny receipts
    ].copy()
    print(f"\nFound {len(receipt_analysis_trips)} trips (3-5 days, <100 miles, receipts >$1) for receipt analysis.")

    if not receipt_analysis_trips.empty:
        assumed_per_diem_daily_rate = 100
        assumed_mileage_rate = 0.50 # Rough estimate. For <100 miles, this will be small.
                                     # Lisa mentioned 0.58 for first 100 miles. Let's try that.
        assumed_mileage_rate_receipt_calc = 0.58


        receipt_analysis_trips.loc[:, 'assumed_per_diem_total'] = receipt_analysis_trips['trip_duration_days'] * assumed_per_diem_daily_rate
        receipt_analysis_trips.loc[:, 'assumed_mileage_reimbursement'] = receipt_analysis_trips['miles_traveled'] * assumed_mileage_rate_receipt_calc
        receipt_analysis_trips.loc[:, 'receipt_component_reimbursed'] = receipt_analysis_trips['expected_output'] - receipt_analysis_trips['assumed_per_diem_total'] - receipt_analysis_trips['assumed_mileage_reimbursement']
        receipt_analysis_trips.loc[:, 'receipt_reimbursement_rate'] = receipt_analysis_trips.apply(
            lambda x: x['receipt_component_reimbursed'] / x['total_receipts_amount'] if x['total_receipts_amount'] > 0 else 0, axis=1
        )

        print("\nReceipt Reimbursement Rate Analysis (3-5 days, <100 miles trips):")
        # Filter for plausible rates (e.g., -0.5 to 1.5 for more tolerance in assumptions)
        plausible_rates = receipt_analysis_trips[
            (receipt_analysis_trips['receipt_reimbursement_rate'] >= -0.5) &
            (receipt_analysis_trips['receipt_reimbursement_rate'] <= 2.0) # Allow up to 200% if there are bonuses
        ].copy() # Use .copy() to avoid SettingWithCopyWarning

        print(plausible_rates[['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'receipt_component_reimbursed', 'receipt_reimbursement_rate']].sort_values(by='total_receipts_amount').head(10))
        if len(plausible_rates) > 10:
            print("...")
            print(plausible_rates[['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_output', 'receipt_component_reimbursed', 'receipt_reimbursement_rate']].sort_values(by='total_receipts_amount').tail(10))

        if not plausible_rates.empty:
            print(f"  Average receipt reimbursement rate: {plausible_rates['receipt_reimbursement_rate'].mean():.2%}")
            print(f"  Median receipt reimbursement rate: {plausible_rates['receipt_reimbursement_rate'].median():.2%}")
        else:
            print("  No trips with plausible receipt reimbursement rates found in this sample.")

        # 5c: Check for non-linear reimbursement (caps, diminishing returns - Lisa, Marcus)
        if not plausible_rates.empty:
            print("\n--- Diminishing Returns Check (Lisa & Marcus) ---")
            print("Showing receipt reimbursement rate vs total receipts amount (3-5 days, <100 miles, sorted by receipts):")
            print(plausible_rates[['total_receipts_amount', 'receipt_reimbursement_rate']].sort_values(by='total_receipts_amount'))
            median_receipt_amount_for_sample = plausible_rates['total_receipts_amount'].median()
            lower_half_receipts = plausible_rates[plausible_rates['total_receipts_amount'] < median_receipt_amount_for_sample]
            upper_half_receipts = plausible_rates[plausible_rates['total_receipts_amount'] >= median_receipt_amount_for_sample]
            if not lower_half_receipts.empty and not upper_half_receipts.empty:
                print(f"  Avg rate for receipts < median (${median_receipt_amount_for_sample:.2f}): {lower_half_receipts['receipt_reimbursement_rate'].mean():.2%}")
                print(f"  Avg rate for receipts >= median (${median_receipt_amount_for_sample:.2f}): {upper_half_receipts['receipt_reimbursement_rate'].mean():.2%}")
            elif not plausible_rates.empty : # Handle cases with few data points
                 print(f"  Overall avg rate for sample: {plausible_rates['receipt_reimbursement_rate'].mean():.2%}")


        # 5d: Check cases where total_receipts_amount ends in .49 or .99 (Lisa, Kevin "rounding bug")
        print("\n--- Rounding Bug Check (.49 or .99 cents) ---")
        # For the selected receipt_analysis_trips (3-5 days, <100 miles)
        if not receipt_analysis_trips.empty: # Check if the dataframe is not empty
            receipt_analysis_trips.loc[:,'receipt_ends_49_99'] = receipt_analysis_trips['total_receipts_amount'].apply(lambda x: True if f"{x:.2f}".endswith('.49') or f"{x:.2f}".endswith('.99') else False)

            special_ending_trips_filtered = receipt_analysis_trips[receipt_analysis_trips['receipt_ends_49_99']]
            other_ending_trips_filtered = receipt_analysis_trips[~receipt_analysis_trips['receipt_ends_49_99']]

            if not special_ending_trips_filtered.empty :
                 mean_rate_str_special = f"{special_ending_trips_filtered['receipt_reimbursement_rate'].mean():.2%}" if not special_ending_trips_filtered.empty else "N/A"
                 print(f"  Avg receipt reimbursement rate (3-5d, <100mi) for .49/.99 endings: {mean_rate_str_special} (Count: {len(special_ending_trips_filtered)})")
            else:
                print("  No 3-5d, <100mi trips with .49/.99 endings in this specific sample.")

            if not other_ending_trips_filtered.empty:
                 mean_rate_str_other = f"{other_ending_trips_filtered['receipt_reimbursement_rate'].mean():.2%}" if not other_ending_trips_filtered.empty else "N/A"
                 print(f"  Avg receipt reimbursement rate (3-5d, <100mi) for other endings: {mean_rate_str_other} (Count: {len(other_ending_trips_filtered)})")
            else:
                print("  No 3-5d, <100mi trips with other endings in this specific sample.")
        else:
            print("  Skipping .49/.99 check as no trips in the current sample for receipt analysis.")

    else:
        print("No trips found for detailed receipt analysis (3-5 days, <100 miles, receipts > $1).")

    # Task 6: Check for 5-day trip bonus (Lisa)
    print("\n\n--- 5-Day Trip Bonus Analysis (Lisa) ---")
    # To control for mileage and receipts, calculate a 'base reimbursement' and then a 'per diem equivalent'
    # Base per diem: $100/day. Mileage rate: $0.50/mile (very rough general estimate)
    # Receipt reimbursement: Assume 50% pass-through (very rough general estimate)

    df_bonus_check = df.copy()
    assumed_mileage_rate_overall = 0.50
    assumed_receipt_passthrough_overall = 0.50

    df_bonus_check['non_per_diem_reimbursement'] = (df_bonus_check['miles_traveled'] * assumed_mileage_rate_overall) + \
                                                 (df_bonus_check['total_receipts_amount'] * assumed_receipt_passthrough_overall)
    df_bonus_check['per_diem_equivalent_total'] = df_bonus_check['expected_output'] - df_bonus_check['non_per_diem_reimbursement']
    # Ensure trip_duration_days is not zero
    df_bonus_check_valid_duration = df_bonus_check[df_bonus_check['trip_duration_days'] > 0].copy()
    df_bonus_check_valid_duration.loc[:, 'per_diem_equivalent_daily'] = df_bonus_check_valid_duration['per_diem_equivalent_total'] / df_bonus_check_valid_duration['trip_duration_days']

    durations_to_compare = [4, 5, 6]
    print(f"Comparing 'Per Diem Equivalent Daily Rate' (assuming {assumed_mileage_rate_overall}/mile and {assumed_receipt_passthrough_overall*100}% receipt passthrough):")
    for dur in durations_to_compare:
        subset = df_bonus_check_valid_duration[df_bonus_check_valid_duration['trip_duration_days'] == dur]
        if not subset.empty:
            # Filter out extreme outliers for a more stable mean/median, e.g. negative or excessively high PPD equivalents
            subset_filtered = subset[(subset['per_diem_equivalent_daily'] > 0) & (subset['per_diem_equivalent_daily'] < 500)] # Arbitrary cap
            if not subset_filtered.empty:
                print(f"  {dur}-day trips: Avg daily per diem equiv: ${subset_filtered['per_diem_equivalent_daily'].mean():.2f}, Median: ${subset_filtered['per_diem_equivalent_daily'].median():.2f} (Count: {len(subset_filtered)})")
            else:
                print(f"  {dur}-day trips: No trips with per diem equiv between $0-$500 (Original count: {len(subset)})")

        else:
            print(f"  No {dur}-day trips found in the dataset.")

    # Task 7: Summarize key observations (will be done after all analyses are run)
    print("\n\n--- Summary of Observations (Preliminary) ---")
    print("1. Mileage rate seems complex and possibly tiered/curved. Low-receipt sample is too small.")
    print("   Initial broad check on all trips suggests very high per-mile values if only a simple $100/day per diem is assumed, indicating other factors or bonuses.")
    print("2. Receipt reimbursement analysis sample for 3-day trips was too small (2 trips). Broadened to 3-5 days, <100 miles.")
    print("   The calculated receipt reimbursement rate is highly sensitive to per diem & mileage assumptions.")
    print("3. 'Rounding bug' for .49/.99 receipt endings needs more nuanced comparison; simple average output is not conclusive.")
    print("4. 5-day trip bonus analysis is set up by calculating a 'per diem equivalent'.")
    print("\nFurther analysis needed to refine assumptions and confirm patterns.")


if __name__ == '__main__':
    analyze_data()
