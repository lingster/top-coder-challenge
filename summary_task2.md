# Task 2: Mileage Deep Dive

## Objective
Analyze cases with zero/minimal receipts to isolate mileage rules, assuming current per diem logic is a reasonable baseline.

## Mileage Analysis with Minimal Receipts (<= $1.00)
Found 0 such cases.
No cases found matching criteria (receipts <= $1.00, miles > 0, and days > 0).

## Revised Mileage Analysis (Attempt 2)
Initial filter (receipts <= .00) yielded 0 cases. Relaxing filter to receipts < 0.00.

## Mileage Analysis with Receipts < $20.00
Found 17 such cases.
Retained 17 cases after filtering out negative or extreme apparent mileage rates (full count: 17).
Cases with negative apparent rates might indicate other penalties or incorrect per diem assumptions for those specific cases.

--- Data (receipts < $20, miles > 0, filtered rates, first 20) ---
|   case_id |   trip_duration_days |   miles_traveled |   total_receipts_amount |   expected_output |   assumed_per_diem |   estimated_receipt_reimb |   approx_mileage_reimbursement |   apparent_rate_per_mile |
|----------:|---------------------:|-----------------:|------------------------:|------------------:|-------------------:|--------------------------:|-------------------------------:|-------------------------:|
|         3 |                    2 |               13 |                    4.67 |            203.52 |                200 |                       -10 |                          13.52 |                    1.04  |
|         6 |                    3 |               41 |                    4.52 |            320.12 |                300 |                       -10 |                          30.12 |                    0.735 |
|         2 |                    1 |               47 |                   17.97 |            128.91 |                100 |                         0 |                          28.91 |                    0.615 |
|         1 |                    1 |               55 |                    3.6  |            126.06 |                100 |                         0 |                          26.06 |                    0.474 |
|        15 |                    1 |               58 |                    5.86 |            117.24 |                100 |                         0 |                          17.24 |                    0.297 |
|        17 |                    1 |               59 |                    8.31 |            120.65 |                100 |                         0 |                          20.65 |                    0.35  |
|         5 |                    1 |               76 |                   13.74 |            158.35 |                100 |                         0 |                          58.35 |                    0.768 |
|         4 |                    3 |               88 |                    5.78 |            380.37 |                300 |                       -10 |                          90.37 |                    1.027 |
|        18 |                    2 |               89 |                   13.85 |            234.2  |                200 |                       -10 |                          44.2  |                    0.497 |
|         0 |                    3 |               93 |                    1.42 |            364.51 |                300 |                       -10 |                          74.51 |                    0.801 |
|        16 |                    1 |              133 |                    8.34 |            179.06 |                100 |                         0 |                          79.06 |                    0.594 |
|        14 |                    1 |              141 |                   10.15 |            195.14 |                100 |                         0 |                          95.14 |                    0.675 |
|        19 |                    2 |              147 |                   17.43 |            325.56 |                200 |                       -10 |                         135.56 |                    0.922 |
|        13 |                    3 |              177 |                   18.73 |            430.86 |                300 |                       -10 |                         140.86 |                    0.796 |
|       925 |                    4 |              477 |                   18.97 |            631.5  |                400 |                       -10 |                         241.5  |                    0.506 |
|       707 |                    7 |              803 |                   12.75 |           1146.78 |                700 |                       -10 |                         456.78 |                    0.569 |
|       758 |                    1 |              893 |                   19.76 |            570.71 |                100 |                         0 |                         470.71 |                    0.527 |


--- Tier Analysis (based on current code $0.58/$0.50) ---
For trips <= 100 miles (count: 10):
  Median apparent rate: $0.675
  Mean apparent rate: $0.660
For trips > 100 miles (count: 7):
  Median apparent rate (overall): $0.594
  Mean apparent rate (overall): $0.656
  Median rate for miles >100 (after first 100 at $0.58, filtered for sensible): $0.638 (count: 7)


--- Efficiency Analysis (Miles per Day vs. Apparent Rate) ---

Median apparent rate per mile by Miles-Per-Day bin:
| mpd_bin   |   median |   count |       mean |
|:----------|---------:|--------:|-----------:|
| 0-49      |   0.768  |       6 |   0.785833 |
| 50-99     |   0.621  |       6 |   0.601167 |
| 100-149   |   0.5815 |       4 |   0.586    |
| 150-174   | nan      |       0 | nan        |
| 175-199   | nan      |       0 | nan        |
| 200-224   | nan      |       0 | nan        |
| 225-249   | nan      |       0 | nan        |
| 250-299   | nan      |       0 | nan        |
| 300+      |   0.527  |       1 |   0.527    |

## Mileage Rate Adjustment (Attempt 1)

Based on the analysis of 17 cases with receipts < 0:
- Median apparent rate for <=100 miles was ~-bash.675.
- Median apparent rate for >100 miles (excess portion) was ~-bash.638.

Changed mileage rates in `calculate_reimbursement.py`:
- From -bash.58 to 0.68 for the first 100 miles.
- From -bash.50 to 0.64 for miles over 100.

### Evaluation Results After Change:
- **Score**: 21139.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 5
- **Average error**: $210.39

Score (21139.00) did NOT improve or match baseline (20408.00).

## Reverting Mileage Rate Adjustment

The mileage rate changes (-bash.68/-bash.64) worsened the score to 21139.00.
Reverted `calculate_reimbursement.py` to the version scoring 20408.00.
The simple tier adjustment was not effective, suggesting a more complex mileage calculation or interaction with other factors.
Next, will investigate Kevin's 'efficiency bonus' (miles per day) hypothesis.

## Mileage Efficiency Bonus Analysis (Kevin's Hypothesis)

Analyzing the 17 filtered cases (receipts < 0) for a potential efficiency bonus based on miles/day.
Retained 17 cases (out of 17) with non-negative data-driven mileage reimbursement for bonus analysis.

--- Potential Bonus Analysis (Data-Driven Reimb vs. Baseline 0.58/0.50 Reimb) ---
|   case_id |   trip_duration_days |   miles_traveled |   miles_per_day |   data_driven_mileage_reimbursement |   baseline_calc_mileage_reimbursement |   potential_bonus_or_error |
|----------:|---------------------:|-----------------:|----------------:|------------------------------------:|--------------------------------------:|---------------------------:|
|         3 |                    2 |               13 |             6.5 |                               13.52 |                                  7.54 |                       5.98 |
|         6 |                    3 |               41 |            13.7 |                               30.12 |                                 23.78 |                       6.34 |
|         4 |                    3 |               88 |            29.3 |                               90.37 |                                 51.04 |                      39.33 |
|         0 |                    3 |               93 |            31   |                               74.51 |                                 53.94 |                      20.57 |
|        18 |                    2 |               89 |            44.5 |                               44.2  |                                 51.62 |                      -7.42 |
|         2 |                    1 |               47 |            47   |                               28.91 |                                 27.26 |                       1.65 |
|         1 |                    1 |               55 |            55   |                               26.06 |                                 31.9  |                      -5.84 |
|        15 |                    1 |               58 |            58   |                               17.24 |                                 33.64 |                     -16.4  |
|        17 |                    1 |               59 |            59   |                               20.65 |                                 34.22 |                     -13.57 |
|        13 |                    3 |              177 |            59   |                              140.86 |                                 96.5  |                      44.36 |
|        19 |                    2 |              147 |            73.5 |                              135.56 |                                 81.5  |                      54.06 |
|         5 |                    1 |               76 |            76   |                               58.35 |                                 44.08 |                      14.27 |
|       707 |                    7 |              803 |           114.7 |                              456.78 |                                409.5  |                      47.28 |
|       925 |                    4 |              477 |           119.2 |                              241.5  |                                246.5  |                      -5    |
|        16 |                    1 |              133 |           133   |                               79.06 |                                 74.5  |                       4.56 |
|        14 |                    1 |              141 |           141   |                               95.14 |                                 78.5  |                      16.64 |
|       758 |                    1 |              893 |           893   |                              470.71 |                                454.5  |                      16.21 |


--- Bonus/Error Statistics by Miles-Per-Day ---
No cases found in the 175-225 miles/day sweet spot.
Outside Sweet Spot - Count: 17
  Median Potential Bonus/Error: $6.34
  Mean Potential Bonus/Error: $13.12
Outside Sweet Spot - Median Apparent Rate: $0.615

## Mileage Analysis: Interaction with Existing High Effort Bonus

Investigating if the existing High Effort Bonus (days 7-10, >800 miles, +50) explains the 'potential_bonus_or_error' in the 17 low-receipt cases.
Analyzed 17 cases (receipts < $20).

--- Effect of Existing High Effort Bonus ---
|   case_id |   trip_duration_days |   miles_traveled |   miles_per_day |   total_receipts_amount |   daily_receipts_val |   baseline_calc_mileage_reimbursement |   data_driven_mileage_reimbursement_plus_any_other_bonus |   potential_bonus_or_error_BEFORE_HE_adj |   gets_high_effort_bonus |   potential_bonus_or_error_AFTER_HE_adj |
|----------:|---------------------:|-----------------:|----------------:|------------------------:|---------------------:|--------------------------------------:|---------------------------------------------------------:|-----------------------------------------:|-------------------------:|----------------------------------------:|
|       707 |                    7 |              803 |           114.7 |                   12.75 |             1.82143  |                                409.5  |                                                   456.78 |                                    47.28 |                      350 |                                 -302.72 |
|         3 |                    2 |               13 |             6.5 |                    4.67 |             2.335    |                                  7.54 |                                                    13.52 |                                     5.98 |                        0 |                                    5.98 |
|         6 |                    3 |               41 |            13.7 |                    4.52 |             1.50667  |                                 23.78 |                                                    30.12 |                                     6.34 |                        0 |                                    6.34 |
|         2 |                    1 |               47 |            47   |                   17.97 |            17.97     |                                 27.26 |                                                    28.91 |                                     1.65 |                        0 |                                    1.65 |
|         1 |                    1 |               55 |            55   |                    3.6  |             3.6      |                                 31.9  |                                                    26.06 |                                    -5.84 |                        0 |                                   -5.84 |
|        15 |                    1 |               58 |            58   |                    5.86 |             5.86     |                                 33.64 |                                                    17.24 |                                   -16.4  |                        0 |                                  -16.4  |
|        17 |                    1 |               59 |            59   |                    8.31 |             8.31     |                                 34.22 |                                                    20.65 |                                   -13.57 |                        0 |                                  -13.57 |
|         5 |                    1 |               76 |            76   |                   13.74 |            13.74     |                                 44.08 |                                                    58.35 |                                    14.27 |                        0 |                                   14.27 |
|         4 |                    3 |               88 |            29.3 |                    5.78 |             1.92667  |                                 51.04 |                                                    90.37 |                                    39.33 |                        0 |                                   39.33 |
|        18 |                    2 |               89 |            44.5 |                   13.85 |             6.925    |                                 51.62 |                                                    44.2  |                                    -7.42 |                        0 |                                   -7.42 |
|         0 |                    3 |               93 |            31   |                    1.42 |             0.473333 |                                 53.94 |                                                    74.51 |                                    20.57 |                        0 |                                   20.57 |
|        16 |                    1 |              133 |           133   |                    8.34 |             8.34     |                                 74.5  |                                                    79.06 |                                     4.56 |                        0 |                                    4.56 |
|        14 |                    1 |              141 |           141   |                   10.15 |            10.15     |                                 78.5  |                                                    95.14 |                                    16.64 |                        0 |                                   16.64 |
|        19 |                    2 |              147 |            73.5 |                   17.43 |             8.715    |                                 81.5  |                                                   135.56 |                                    54.06 |                        0 |                                   54.06 |
|        13 |                    3 |              177 |            59   |                   18.73 |             6.24333  |                                 96.5  |                                                   140.86 |                                    44.36 |                        0 |                                   44.36 |
|       925 |                    4 |              477 |           119.2 |                   18.97 |             4.7425   |                                246.5  |                                                   241.5  |                                    -5    |                        0 |                                   -5    |
|       758 |                    1 |              893 |           893   |                   19.76 |            19.76     |                                454.5  |                                                   470.71 |                                    16.21 |                        0 |                                   16.21 |

Number of cases in this set that get the High Effort Bonus: 1


--- Statistics for 'Potential Bonus/Error AFTER HE Adjustment' ---
Median: $5.98
Mean: $-7.47
Min: $-302.72
Max: $54.06
Median Apparent Rate (after accounting for existing HE bonus, on valid rates): $0.615

## Mileage Rate Adjustment (Attempt 2 - Targeted)

Previous global rate changes worsened score. Existing High Effort Bonus did not fully explain discrepancies in the 17 low-receipt cases.
Hypothesis: Rate for miles > 100 (0.50) is too low, while rate for <=100 miles (0.58) is okay.
Median apparent rate for excess miles (over 100) in low-receipt sample was ~-bash.638.

Changed mileage rates in `calculate_reimbursement.py`:
- Rate for first 100 miles: 0.58 (no change).
- Rate for miles > 100: 0.60 (changed from 0.50).

### Evaluation Results After Change:
- **Score**: 20679.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $205.79

Score (20679.00) did NOT improve or match baseline (20408.00).

## Reverting Targeted Mileage Rate Adjustment

The targeted mileage rate change (-bash.58/-bash.60) worsened the score to 20679.00.
Reverted `calculate_reimbursement.py` to the version scoring 20408.00.
Simple tier adjustments are not effective. The mileage calculation is likely more complex or influenced by other factors not yet modeled for the low-receipt subset.
Next: Broaden data analysis to search for Kevin's 'efficiency bonus' (miles per day) across a wider range of trips, not just very low receipt ones.

## Broader Analysis for Miles/Day Efficiency Bonus

Analyzing all trips to find an unexplained mileage component correlated with miles/day, especially Kevin's 175-225 mpd sweet spot.
This uses current script's logic for per diem, receipts, and existing high effort bonus as baseline.
Analyzed 1000 trips from public_cases.json (after ensuring days > 0).
Retained 976 trips after filtering zero-mile trips and extreme unexplained_mileage_diff outliers (between -$500 and +$500).

--- Unexplained Mileage Difference by Miles/Day Bin ---
| mpd_bin                    |   median |      mean |   count |     min |    max |
|:---------------------------|---------:|----------:|--------:|--------:|-------:|
| 0-99                       |   55.03  |  51.625   |     569 | -492.26 | 493.48 |
| 100-149                    |  -29.66  | -21.4328  |     151 | -460.78 | 441.49 |
| 150-174                    |   -6.75  |  -6.03283 |      46 | -471.58 | 387.37 |
| 175-199 (Sweet Spot Lower) |   11.955 |   3.493   |      20 | -406.93 | 451.88 |
| 200-224 (Sweet Spot Upper) |   67.76  |  43.4681  |      26 | -473.48 | 456.39 |
| 225-249 (Post Sweet Spot)  |   44.84  |  29.0763  |       8 | -175.85 | 286.77 |
| 250-299                    |   -7.4   |  -2.99447 |      38 | -320.05 | 392.26 |
| 300+                       |  122.89  |  79.0255  |     118 | -465.24 | 484    |

--- Overall Statistics for Unexplained Mileage Difference (Filtered) ---
Median: $39.59
Mean: $37.40
Std Dev: $217.46

--- Context for Sweet Spot Bins (175-224 miles/day) ---
Number of cases in sweet spot bins: 46
Median 'calc_mileage' (baseline $0.58/$0.50) in sweet spot: $453.25
Median 'unexplained_mileage_diff' in sweet spot: $36.43
Median 'unexplained_mileage_diff' as % of 'calc_mileage' in sweet spot: 9.51%

## MPD-Based Additive Bonus Implementation

Based on broader analysis, specific MPD bins showed positive unexplained mileage differences:
- 200-224 mpd: Median residual +7.76
- 300+ mpd: Median residual +22.89

Implemented additive bonuses in `calculate_reimbursement.py`:
- Added $60.0 for 200 <= miles_per_day < 225.
- Added $120.0 for miles_per_day >= 300.

### Evaluation Results After Adding MPD Bonuses:
- **Score**: 20258.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 4
- **Average error**: $201.58

Score improved from baseline (20408.00).

## MPD-Based Additive Bonus Implementation (Continued - Low MPD)

Previous MPD bonuses (200-224 mpd, 300+ mpd) improved score to 20258.00.
Analysis showed 0-99 mpd range had a median unexplained mileage difference of +5.03.

Implemented further additive bonus in `calculate_reimbursement.py`:
- Added $50.0 for 0 < miles_per_day < 100.
(Existing bonuses of $60 for 200-224 mpd and $120 for 300+ mpd remain.)

### Evaluation Results After Adding Low MPD Bonus:
- **Score**: 19803.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $197.03

Score improved from previous 20258.00.

## Mileage Calculation - Summary of Successful MPD Bonuses

After iterative additions of MPD-based bonuses, the current `calculate_reimbursement.py` includes:
- **Bonus 1:** +0.0 for 0 < miles_per_day < 100.
- **Bonus 2:** +0.0 for 200 <= miles_per_day < 225.
- **Bonus 3:** +20.0 for miles_per_day >= 300.

These changes have resulted in the following evaluation metrics:
- **Score**: 19803.00 (Improved from baseline 20408.00 and previous 20258.00)
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $197.03

### Future Considerations for Mileage:
The broader MPD analysis (before these bonuses were added) indicated that the following bins had negative median 'unexplained_mileage_diff':
- **100-149 mpd**
- **250-299 mpd**
This suggests that trips in these efficiency bands might not receive these bonuses, or might even have different base rate calculations or penalties.
This should be revisited if further error analysis points to issues with trips in these MPD ranges.
For now, the current set of MPD bonuses represents a significant improvement for the mileage component.
