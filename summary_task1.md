# Task 1: Per Diem Deep Dive

## Objective
Analyze cases with zero/minimal miles and receipts to isolate per diem rules. Test different day thresholds and rates from interviews.

## Analysis of Filtered Data
Found 0 cases with miles <= 10 and receipts <= $10. No data to analyze for per diem specifics under these strict criteria.

No specific per diem rates could be derived due to lack of matching cases under the current strict filter.

## Initial Hypotheses & Observations
- The data filtering seems to provide a good set of cases for per diem analysis.
- Comparison with current code's per diem tiers will be key.
- The 5-day bonus should also be checked within this filtered dataset.
- Next steps will involve comparing these 'apparent_daily_rate' values against the logic in `calculate_reimbursement.py` and making adjustments if discrepancies are found.

## Revised Analysis Approach (Attempt 2)
The initial filtering (miles <= 10 AND receipts <= 0) yielded 0 cases. Relaxing the filter.


### Filter: miles == 0 AND receipts == 0
Found 0 such cases.

### Filter: miles == 0 AND receipts == 0
Found 0 such cases.

### Filter: miles == 0 AND receipts == 0
Found 0 such cases.

### Filter: miles == 0 AND receipts == 0
Found 0 such cases.

### Filter: miles < 20 AND receipts < $20
Found 1 cases with miles < 20 and receipts < $20 and valid days.

--- Data (miles < 20, receipts < $20) ---
|   case_id |   trip_duration_days |   miles_traveled |   total_receipts_amount |   expected_output |   apparent_daily_rate_raw |   daily_rate_minus_mileage_est |
|----------:|---------------------:|-----------------:|------------------------:|------------------:|--------------------------:|-------------------------------:|
|         3 |                    2 |               13 |                    4.67 |            203.52 |                    101.76 |                          97.99 |


--- Median Apparent Daily Rates (Raw) by Trip Duration ---
|   trip_duration_days |   median |   count |
|---------------------:|---------:|--------:|
|                    2 |   101.76 |       1 |


--- Median Daily Rates (Output Minus Est. Mileage) by Trip Duration ---
|   trip_duration_days |   median |   count |
|---------------------:|---------:|--------:|
|                    2 |    97.99 |       1 |


--- Comparison with Current Code (using daily_rate_minus_mileage_est) ---
Category: 1-7 days
  Day 2: Median Rate (adj): $97.99 (Count: 1.0). Expected base rate (approx): $100
Category: 8-10 days
  No data for days in category: 8-10 days
Category: 11+ days
  No data for days in category: 11+ days

- No 5-day trips found in the v2 filtered set for bonus verification.

## Conclusions from Per Diem Analysis (Task 1)

The attempts to isolate pure per diem cases were challenging due to data sparsity:
- Filtering for `miles == 0 AND receipts == 0` yielded 0 cases.
- Filtering for `miles < 20 AND receipts < 0` yielded 1 relevant case.
  - This case (2 days, 13 miles, .67 receipts -> output 03.52) resulted in an adjusted daily rate of ~7.99.
  - This supports the current `calculate_reimbursement.py` logic of 00/day for short trips (1-7 days), considering minor impacts from low miles/receipts.

Given the limited direct evidence from isolated cases, especially for medium (8-10 days) and long (11+ days) trips:
- **Decision**: No changes will be made to the per diem logic in `calculate_reimbursement.py` *at this stage*.
- The existing tiered structure (00 for 1-7 days; 0/5 for 8-10 days; 0/0/5 for 11+ days based on conditions) will be retained as the working hypothesis.
- The 5-day +0 bonus also remains a strong hypothesis based on interviews and current code.
- The validity of these per diem rates will be indirectly tested when analyzing mileage and receipt components. If significant discrepancies arise there, per diem rates may be revisited.

Proceeding to Mileage Analysis (Task 2) with these assumed per diem baselines.
