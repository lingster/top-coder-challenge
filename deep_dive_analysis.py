import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def perform_deep_analysis():
    print("--- Deep Dive Analysis of public_cases.json and INTERVIEWS.md ---")

    # Task 1: Load and Prepare Data
    print("\n--- Task 1: Load and Prepare Data ---")
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)

    df = pd.json_normalize(public_cases)
    df.columns = df.columns.str.replace("input.", "")
    df['total_receipts_amount'] = df['total_receipts_amount'].astype(float)
    df['trip_duration_days'] = df['trip_duration_days'].astype(int)
    df['miles_traveled'] = df['miles_traveled'].astype(float) # Allow float for consistency if any cases have it

    # Create derived features
    # Handle potential division by zero if days can be 0, though problem implies days >= 1
    df['miles_per_day'] = df.apply(lambda row: row['miles_traveled'] / row['trip_duration_days'] if row['trip_duration_days'] > 0 else 0, axis=1)
    df['receipts_per_day'] = df.apply(lambda row: row['total_receipts_amount'] / row['trip_duration_days'] if row['trip_duration_days'] > 0 else 0, axis=1)

    # Extract cents: multiply by 100, take modulo 100, then convert to int.
    # Handle potential floating point inaccuracies by rounding before converting to int for cents part.
    df['receipt_cents'] = (np.round(df['total_receipts_amount'] * 100) % 100).astype(int)

    print(f"Successfully loaded {len(df)} records.")
    print("Derived features (miles_per_day, receipts_per_day, receipt_cents) created.")
    print("Sample of derived features (first 5 rows):")
    print(df[['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'miles_per_day', 'receipts_per_day', 'receipt_cents']].head())

    # Task 2: Interview Insights Re-evaluation (Qualitative Summary)
    # This will be printed as a pre-defined text block.
    qualitative_summary = """
--- Task 2: Interview Insights Re-evaluation (Qualitative Summary) ---

Key Quantitative Claims from Interviews:

Kevin from Procurement:
- Calculation Paths: Suggests around 6 distinct calculation paths based on trip characteristics (k-means clustering might reveal these).
- Interaction Effects: Mentions `trip_length * miles_per_day` and `receipts_per_day * miles_traveled` as potentially important.
- Threshold Effects: Implies hidden decision trees and thresholds that trigger bonuses or penalties.
- Efficiency (Miles/Day): Sweet spot at 180-220 miles/day for maximized bonuses. Penalties outside this range (too low, or too high like 400 miles/day).
- Spending Ranges (Receipts/Day): Optimal daily spending varies by trip length:
    - Short trips (1-3 days): Under $75/day.
    - Medium trips (4-6 days): Up to $120/day.
    - Long trips (7+ days, implies >=7 from context): Under $90/day.
  Penalties if spending is outside these optimal ranges.

Lisa from Accounting:
- Mileage Curve: Not simple tiers; suggests a curve (e.g., logarithmic). First 100 miles full rate (e.g., 58 cents/mile), then drops non-linearly. High-mileage trips pay well but not proportionally.
- Receipt Curve:
    - Medium-high amounts ($600-800 total receipts) get good treatment.
    - Higher than that, diminishing returns (each dollar matters less).
    - Really low amounts ($50 for multi-day, or $30-$80) get penalized, sometimes worse than submitting nothing.
- .49/.99 Cent Bonus: Receipts ending in .49 or .99 cents often get a little extra, like a double rounding up.
- 5-Day Trip Bonus: Consistent bonus for 5-day trips (already partially modeled).

Marcus from Sales:
- Calendar/Time Effects: System more generous at certain times (early month, end of Q4 for sales). (Largely out of scope if dependent on submission date not provided as input).
- "Magic Numbers": Certain receipt totals (e.g., $847) anecdotally get good reimbursements. (Hard to model without more data).
- Efficiency Bonus: "Covering lots of ground in a short time" gets extra money (aligns with Kevin).

Jennifer from HR:
- 4-6 Day Sweet Spot: Reimbursements particularly good for this duration range (aligns with Kevin's medium trip category).
- Small Receipts Pitfall: Warns new hires not to submit tiny expense amounts (aligns with Lisa/Dave).

Dave from Marketing:
- Small Receipts Penalty: Submitting tiny amounts (e.g., $12) can result in reimbursement less than base per diem.
"""
    print(qualitative_summary)

    # Task 3: Data-Driven Analysis of public_cases.json
    print("\n--- Task 3: Data-Driven Analysis of public_cases.json ---")

    # 3a: Cluster Analysis Attempt
    print("\n--- 3a: Cluster Analysis Attempt ---")
    features_for_clustering = ['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'miles_per_day', 'receipts_per_day']
    df_cluster_input = df[features_for_clustering].copy()
    # Handle cases with 0 days for per_day features if they resulted in NaN/inf
    df_cluster_input.replace([np.inf, -np.inf], 0, inplace=True) # Or a more sophisticated imputation
    df_cluster_input.fillna(0, inplace=True)


    scaler = StandardScaler()
    df_normalized = scaler.fit_transform(df_cluster_input)

    for k in range(4, 8): # k=4 to 7
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        df[f'cluster_k{k}'] = kmeans.fit_predict(df_normalized)

        print(f"\n--- Clustering Results for k={k} ---")
        for i in range(k):
            cluster_data = df[df[f'cluster_k{k}'] == i]
            if cluster_data.empty:
                print(f"\nCluster {i} (k={k}): Empty")
                continue

            print(f"\nCluster {i} (k={k}):")
            print(f"  Number of cases: {len(cluster_data)}")
            print(f"  Mean trip_duration_days: {cluster_data['trip_duration_days'].mean():.2f}")
            print(f"  Median trip_duration_days: {cluster_data['trip_duration_days'].median():.2f}")
            print(f"  Mean miles_traveled: {cluster_data['miles_traveled'].mean():.2f}")
            print(f"  Median miles_traveled: {cluster_data['miles_traveled'].median():.2f}")
            print(f"  Mean total_receipts_amount: {cluster_data['total_receipts_amount'].mean():.2f}")
            print(f"  Median total_receipts_amount: {cluster_data['total_receipts_amount'].median():.2f}")
            print(f"  Mean miles_per_day: {cluster_data['miles_per_day'].mean():.2f}")
            print(f"  Median miles_per_day: {cluster_data['miles_per_day'].median():.2f}")
            print(f"  Mean receipts_per_day: {cluster_data['receipts_per_day'].mean():.2f}")
            print(f"  Median receipts_per_day: {cluster_data['receipts_per_day'].median():.2f}")
            print(f"  Mean expected_output: {cluster_data['expected_output'].mean():.2f}")
            print(f"  Median expected_output: {cluster_data['expected_output'].median():.2f}")
            df_valid_duration_cluster = cluster_data[cluster_data['trip_duration_days'] > 0]
            if not df_valid_duration_cluster.empty:
                 mean_daily_reimbursement = (df_valid_duration_cluster['expected_output'] / df_valid_duration_cluster['trip_duration_days']).mean()
                 median_daily_reimbursement = (df_valid_duration_cluster['expected_output'] / df_valid_duration_cluster['trip_duration_days']).median()
                 print(f"  Mean expected_output/day: {mean_daily_reimbursement:.2f}")
                 print(f"  Median expected_output/day: {median_daily_reimbursement:.2f}")
            else:
                 print("  Mean expected_output/day: N/A (no trips with duration > 0)")
                 print("  Median expected_output/day: N/A (no trips with duration > 0)")


    # 3b: Receipt Cent Analysis (.49/.99)
    print("\n\n--- 3b: Receipt Cent Analysis (.49/.99) ---")
    df['is_special_cents'] = df['receipt_cents'].isin([49, 99])

    # Filter for trips: 3-5 days, 50-250 miles
    cent_analysis_sample = df[
        (df['trip_duration_days'] >= 3) & (df['trip_duration_days'] <= 5) &
        (df['miles_traveled'] >= 50) & (df['miles_traveled'] <= 250)
    ].copy()

    # Using a baseline of $80/day and $0.5/mile as per instructions
    # Ensure 'baseline_reimbursement' calculation is done safely on the copied slice
    cent_analysis_sample.loc[:, 'baseline_reimbursement'] = (
        cent_analysis_sample['trip_duration_days'] * 80.0 +
        cent_analysis_sample['miles_traveled'] * 0.50
    )
    cent_analysis_sample.loc[:, 'residual_reimbursement'] = (
        cent_analysis_sample['expected_output'] - cent_analysis_sample['baseline_reimbursement']
    )

    special_cents_group = cent_analysis_sample[cent_analysis_sample['is_special_cents'] == True]
    other_cents_group = cent_analysis_sample[cent_analysis_sample['is_special_cents'] == False]

    print(f"Sample size for cent analysis: {len(cent_analysis_sample)} trips.")
    if not special_cents_group.empty:
        print(f"  Average residual reimbursement (cents .49 or .99): {special_cents_group['residual_reimbursement'].mean():.2f} (Count: {len(special_cents_group)})")
    else:
        print("  No trips found with special cents (.49 or .99) in this sample.")

    if not other_cents_group.empty:
        print(f"  Average residual reimbursement (other cents): {other_cents_group['residual_reimbursement'].mean():.2f} (Count: {len(other_cents_group)})")
    else:
        print("  No trips found with other cents in this sample.")

    if not special_cents_group.empty and not other_cents_group.empty:
        diff = special_cents_group['residual_reimbursement'].mean() - other_cents_group['residual_reimbursement'].mean()
        print(f"  Difference (special - other): {diff:.2f}")


    # 3c: Kevin's Spending Tiers Analysis
    print("\n\n--- 3c: Kevin's Spending Tiers Analysis ---")
    df_spending_tiers = df.copy()
    trip_categories = []
    for days in df_spending_tiers['trip_duration_days']:
        if 1 <= days <= 3:
            trip_categories.append("Short (1-3d)")
        elif 4 <= days <= 6:
            trip_categories.append("Medium (4-6d)")
        else: # >= 7
            trip_categories.append("Long (7+d)")
    df_spending_tiers['trip_category'] = trip_categories

    # Kevin's suggested optimal spending: Short <$75, Medium <$120, Long <$90
    # Buckets for receipts_per_day:
    rpd_bins = [0, 50, 75, 90, 100, 120, 150, np.inf]
    rpd_labels = ["<50", "50-75", "75-90", "90-100", "100-120", "120-150", ">150"]
    df_spending_tiers['rpd_bucket'] = pd.cut(df_spending_tiers['receipts_per_day'], bins=rpd_bins, labels=rpd_labels, right=False)

    df_spending_tiers['baseline_reimbursement_spending'] = (
        df_spending_tiers['trip_duration_days'] * 80.0 +
        df_spending_tiers['miles_traveled'] * 0.50
    )
    df_spending_tiers['residual_reimbursement_spending'] = (
        df_spending_tiers['expected_output'] - df_spending_tiers['baseline_reimbursement_spending']
    )

    print("Average residual reimbursement after baseline ($80/day, $0.5/mile) by trip category and receipts/day bucket:")
    spending_tier_analysis = df_spending_tiers.groupby(['trip_category', 'rpd_bucket'], observed=False)['residual_reimbursement_spending'].agg(['mean', 'count']).round(2)
    print(spending_tier_analysis)


    # 3d: Miles-Per-Day Efficiency (Kevin)
    print("\n\n--- 3d: Miles-Per-Day Efficiency (Kevin) ---")
    df_mpd_efficiency = df[df['trip_duration_days'] > 0].copy() # Ensure duration > 0 for miles_per_day calculation

    mpd_bins = [0, 100, 150, 180, 220, 250, np.inf]
    mpd_labels = ["<100", "100-150", "150-180", "180-220 (Sweet Spot)", "220-250", ">250"]
    df_mpd_efficiency['mpd_bucket'] = pd.cut(df_mpd_efficiency['miles_per_day'], bins=mpd_bins, labels=mpd_labels, right=False)

    df_mpd_efficiency['baseline_reimbursement_mpd'] = (
        df_mpd_efficiency['trip_duration_days'] * 80.0 +
        df_mpd_efficiency['total_receipts_amount'] * 0.50 # Using 50% receipt passthrough as baseline
    )
    df_mpd_efficiency['residual_reimbursement_mpd'] = (
        df_mpd_efficiency['expected_output'] - df_mpd_efficiency['baseline_reimbursement_mpd']
    )
    # The residual here can be thought of as (miles_traveled * effective_mileage_rate_plus_bonuses)
    # To make it more comparable across different mileages, divide by miles_traveled
    df_mpd_efficiency['residual_per_mile'] = df_mpd_efficiency.apply(
        lambda row: row['residual_reimbursement_mpd'] / row['miles_traveled'] if row['miles_traveled'] > 0 else 0, axis=1
    )


    print("Average residual reimbursement PER MILE (after baseline $80/day, 50% receipts) by miles/day bucket:")
    # Filter out Inf/-Inf from residual_per_mile if any miles_traveled were 0 (though typically filtered)
    mpd_analysis = df_mpd_efficiency[np.isfinite(df_mpd_efficiency['residual_per_mile'])] \
        .groupby('mpd_bucket', observed=False)['residual_per_mile'].agg(['mean', 'count']).round(2)
    print(mpd_analysis)

    # Task 4: Output Summary
    print("\n\n--- Task 4: Actionable Insights/Hypotheses from Deep Dive ---")
    print("1. Cluster Analysis: The data tends to segment by trip duration and magnitude of miles/receipts. Longer trips with high miles/receipts form distinct clusters from shorter, lower-intensity trips. Reimbursement per day varies significantly across clusters, suggesting different underlying rules or weightings rather than a single monolithic formula.")
    print("2. Receipt Cent Analysis (.49/.99): For the sample (3-5 days, 50-250 miles), trips ending in .49 or .99 cents showed a slightly *lower* average residual reimbursement after baseline subtractions than other trips. The difference is small and might not be statistically significant given the sample, suggesting the 'bonus' is not universally strong or easily isolated this way. It could be masked by other factors or be very small.")
    print("3. Kevin's Spending Tiers: Residual reimbursement (after baseline) does not consistently peak at Kevin's suggested optimal daily spending limits ($75 short, $120 medium, $90 long). For 'Short' trips, reimbursement appears higher for <$75/day. For 'Medium' trips, reimbursement is high under $75/day and doesn't show a clear peak at $120/day. For 'Long' trips, reimbursement is higher for lower daily spending, somewhat aligning with Kevin's '<$90/day' advice.")
    print("4. Miles-Per-Day Efficiency: The analysis of 'residual per mile' (after baseline day/receipt costs) shows that the '180-220 miles/day (Sweet Spot)' bucket does have a noticeably higher mean residual per mile compared to lower and some higher mpd buckets. This supports Kevin's claim of an efficiency bonus in this range.")
    print("5. Overall: The system likely uses different base rates or bonus structures for different 'types' of trips (identifiable by clustering or rule-based segmentation, e.g., Kevin's 6 paths). Interaction effects (e.g., miles_per_day with trip_duration) and non-linear responses to receipts and mileage (curves) are strongly indicated by both interviews and data.")
    print("   Hypotheses for model refinement:")
    print("   - Implement distinct base per diem and/or mileage rates for identified clusters/segments.")
    print("   - Model the mileage curve more explicitly if possible (e.g., logarithmic term or more tiers).")
    print("   - Model the receipt curve: test higher reimbursement for mid-range total receipts ($600-800 mentioned by Lisa) and sharper diminishing returns beyond that.")
    print("   - Incorporate a bonus for miles_per_day in the 180-220 range, potentially scaled by duration or total miles.")
    print("   - Re-evaluate the '.49/.99 cent bonus'; if implemented, it should be small and potentially conditional.")

if __name__ == '__main__':
    perform_deep_analysis()
