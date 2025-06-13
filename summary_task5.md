# Task 5: High Effort Bonus Analysis

## Objective
Analyze the effectiveness of the current High Effort Bonus (HEB) and see if refinement is needed, considering interview input. Current script score: 18464.00.
The 5-Day bonus (Task 4) is assumed correct as implemented.

## High Effort Bonus (HEB) Analysis
Found 101 cases that trigger the current HEB (+$350.00).
Error analysis for cases GETTING HEB:
  Median unexplained_error: $-334.73
  Mean unexplained_error: $-315.73
  Std Dev unexplained_error: $210.41
  Min/Max error: $-676.79 / $280.04
  Cases with largest errors (top 5 positive, bottom 5 negative):
|   case_id |   trip_duration_days |   miles_traveled |   total_receipts_amount |   expected_output |   script_calculated_output |   unexplained_error |
|----------:|---------------------:|-----------------:|------------------------:|------------------:|---------------------------:|--------------------:|
|       512 |                    8 |             1025 |                 1031.33 |           2214.64 |                    1934.6  |              280.04 |
|       148 |                    7 |             1006 |                 1181.33 |           2279.82 |                    2092.6  |              187.22 |
|       813 |                    8 |              829 |                 1147.89 |           2004.34 |                    1889.05 |              115.29 |
|       668 |                    7 |             1033 |                 1013.03 |           2119.83 |                    2030.36 |               89.47 |
|       750 |                    8 |             1134 |                 1049.84 |           2073.13 |                    1997.43 |               75.7  |
|   case_id |   trip_duration_days |   miles_traveled |   total_receipts_amount |   expected_output |   script_calculated_output |   unexplained_error |
|----------:|---------------------:|-----------------:|------------------------:|------------------:|---------------------------:|--------------------:|
|       652 |                    9 |             1063 |                 2497.79 |           1761.94 |                    2438.73 |             -676.79 |
|       783 |                    9 |             1097 |                 2330.2  |           1728.07 |                    2397.07 |             -669    |
|       354 |                   10 |              860 |                 2380.76 |           1759.97 |                    2421.27 |             -661.3  |
|       265 |                   10 |              976 |                 2166.02 |           1775.03 |                    2404.11 |             -629.08 |
|       353 |                   10 |              888 |                  298.68 |           1171.54 |                    1781.21 |             -609.67 |

--- Analysis of Kevin's MPD Sweet Spot (175-225 mpd) NOT getting HEB ---
Found 46 cases in MPD sweet spot (175-225) that DO NOT get HEB.
Error analysis for MPD sweet spot cases WITHOUT HEB:
  Median unexplained_error: $-49.73
  Mean unexplained_error: $-65.47
  Top 5 largest positive errors (potential for more bonus):
|   case_id |   trip_duration_days |   miles_traveled |   mpd |   total_receipts_amount |   expected_output |   script_calculated_output |   unexplained_error |
|----------:|---------------------:|-----------------:|------:|------------------------:|------------------:|---------------------------:|--------------------:|
|       699 |                    2 |              370 | 185   |                 1554.5  |           1311.23 |                     937.08 |              374.15 |
|       394 |                    2 |              423 | 211.5 |                 1639.17 |           1367.64 |                    1053.21 |              314.43 |
|        79 |                    3 |              624 | 208   |                 1160.92 |           1459.34 |                    1202.41 |              256.93 |
|       886 |                    4 |              764 | 191   |                 1417.94 |           1682.1  |                    1428.07 |              254.03 |
|       895 |                    3 |              560 | 186.7 |                 1664.15 |           1419.48 |                    1170.45 |              249.03 |

--- Overall Unexplained Error Distribution (all cases) ---
Overall median unexplained_error: $-37.63
Overall mean unexplained_error: $-57.85

## High Effort Bonus (HEB) Amount Adjustment

Script score 18464.00. Analysis showed cases receiving the +$350.0 HEB had a median 'unexplained_error' of -$334.73 (i.e., overpaid).
Hypothesis: The HEB amount of $350.0 is too high.

Implemented in `calculate_reimbursement.py`:
- Changed High Effort Bonus from $350.0 to $50.0.
(Conditions for applying HEB remain unchanged: days 7-10, miles > 800, and not already penalized on per diem for low receipts in high effort scenario).

### Evaluation Results After This Change:
- **Score**: 16817.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 1
- **Average error**: $167.17

Score improved from previous 18464.00.
