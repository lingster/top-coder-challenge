# Task 3: Receipt Processing Investigation

## Objective
Analyze cases with minimal miles to isolate receipt rules. Test for diminishing returns, caps, penalties, and the .49/.99 rounding bug.

## Initial Receipt Analysis (Miles <= 10, Receipts > 0)
Found 9 cases matching criteria.

--- Comparison of Data-Driven vs. Script Receipt Component (Sorted by Receipts, first 30) ---
|   case_id |   trip_duration_days |   total_receipts_amount |   calc_script_receipt_reimb |   data_driven_receipt_comp |   script_receipt_rate |   data_driven_receipt_rate |
|----------:|---------------------:|------------------------:|----------------------------:|---------------------------:|----------------------:|---------------------------:|
|       875 |                   13 |                   78.44 |                       47.06 |                       9.07 |                   0.6 |                      0.116 |
|       900 |                    4 |                  458.7  |                      275.22 |                       5.73 |                   0.6 |                      0.012 |
|       545 |                   10 |                  836.86 |                      418.43 |                     313.66 |                   0.5 |                      0.375 |
|       728 |                   10 |                 1094.06 |                      437.62 |                     708.18 |                   0.4 |                      0.647 |
|       434 |                   12 |                 1203.1  |                      481.24 |                     729.1  |                   0.4 |                      0.606 |
|       295 |                    4 |                 1262.73 |                      505.09 |                     805.61 |                   0.4 |                      0.638 |
|       597 |                   10 |                 1338.9  |                      535.56 |                     957.35 |                   0.4 |                      0.715 |
|       343 |                    8 |                 2075.6  |                      622.68 |                     888.06 |                   0.3 |                      0.428 |
|       263 |                    1 |                 2246.28 |                      673.88 |                     965    |                   0.3 |                      0.43  |


--- Diminishing Returns Check (Data-Driven Receipt Rate vs. Total Receipts) ---
| receipt_bin   |   median |     mean |   count |
|:--------------|---------:|---------:|--------:|
| 0-19.99       | nan      | nan      |       0 |
| 20-49.99      | nan      | nan      |       0 |
| 50-99.99      |   0.116  |   0.116  |       1 |
| 100-199.99    | nan      | nan      |       0 |
| 200-499.99    |   0.012  |   0.012  |       1 |
| 500-999.99    |   0.375  |   0.375  |       1 |
| 1000-1499.99  |   0.6425 |   0.6515 |       4 |
| 1500+         |   0.429  |   0.429  |       2 |
Overall median data-driven receipt rate (sane rates): 0.430
Overall mean data-driven receipt rate (sane rates): 0.441


--- Low Amount Penalty Check ---
Found 0 cases potentially subject to -$10 penalty by script logic.

## Receipt Analysis - Broader Filter (Miles <= 100)
Initial analysis with miles <= 10 yielded only 9 cases. Broadening filter to miles <= 100 for more data.


## Receipt Analysis - Broader Filter (Miles <= 100)
Initial analysis with miles <= 10 yielded only 9 cases. Broadening filter to miles <= 100 for more data.

## Receipt Analysis (Miles <= 100, Receipts > 0)
Found 93 cases matching criteria.

--- Comparison of Data-Driven vs. Script Receipt Component (Sorted by Receipts, first 30) ---
|   case_id |   trip_duration_days |   miles_traveled |   total_receipts_amount |   calc_script_receipt_reimb |   data_driven_receipt_comp |   script_receipt_rate |   data_driven_receipt_rate | ends_49_99   |
|----------:|---------------------:|-----------------:|------------------------:|----------------------------:|---------------------------:|----------------------:|---------------------------:|:-------------|
|         0 |                    3 |               93 |                    1.42 |                      -10    |                     -39.43 |                -7.042 |                    -27.768 | False        |
|         1 |                    1 |               55 |                    3.6  |                        2.16 |                     -55.84 |                 0.6   |                    -15.511 | False        |
|         6 |                    3 |               41 |                    4.52 |                      -10    |                     -53.66 |                -2.212 |                    -11.872 | False        |
|         3 |                    2 |               13 |                    4.67 |                      -10    |                     -54.02 |                -2.141 |                    -11.567 | False        |
|         4 |                    3 |               88 |                    5.78 |                      -10    |                     -20.67 |                -1.73  |                     -3.576 | False        |
|        15 |                    1 |               58 |                    5.86 |                        3.52 |                     -66.4  |                 0.601 |                    -11.331 | False        |
|        17 |                    1 |               59 |                    8.31 |                        4.99 |                     -63.57 |                 0.6   |                     -7.65  | False        |
|         5 |                    1 |               76 |                   13.74 |                        8.24 |                     -35.73 |                 0.6   |                     -2.6   | False        |
|        18 |                    2 |               89 |                   13.85 |                      -10    |                     -67.42 |                -0.722 |                     -4.868 | False        |
|         2 |                    1 |               47 |                   17.97 |                       10.78 |                     -48.35 |                 0.6   |                     -2.691 | False        |
|        12 |                    2 |               21 |                   20.04 |                       12.02 |                     -57.6  |                 0.6   |                     -2.874 | False        |
|        11 |                    3 |               80 |                   21.05 |                       12.63 |                     -29.53 |                 0.6   |                     -1.403 | False        |
|       759 |                   12 |               37 |                   52.65 |                       31.59 |                     117.55 |                 0.6   |                      2.233 | False        |
|       851 |                    5 |               14 |                   78.33 |                       47    |                    -201.42 |                 0.6   |                     -2.571 | False        |
|       875 |                   13 |                8 |                   78.44 |                       47.06 |                       9.07 |                 0.6   |                      0.116 | False        |
|       190 |                    6 |               45 |                   81.59 |                       48.95 |                    -153.52 |                 0.6   |                     -1.882 | False        |
|       706 |                    1 |               85 |                   89.83 |                       53.9  |                     -23.77 |                 0.6   |                     -0.265 | False        |
|       625 |                   14 |               94 |                  105.94 |                       63.56 |                     376.11 |                 0.6   |                      3.55  | False        |
|       677 |                   13 |               63 |                  107.92 |                       64.75 |                     -26.29 |                 0.6   |                     -0.244 | False        |
|       940 |                    7 |               83 |                  137.84 |                       82.7  |                    -315.49 |                 0.6   |                     -2.289 | False        |
|       556 |                   13 |               32 |                  232.43 |                      139.46 |                      86.56 |                 0.6   |                      0.372 | False        |
|       831 |                    8 |               16 |                  259.02 |                      155.41 |                    -115.72 |                 0.6   |                     -0.447 | False        |
|       646 |                    4 |               18 |                  289.06 |                      173.44 |                     -79.56 |                 0.6   |                     -0.275 | False        |
|       548 |                    4 |               11 |                  312.01 |                      187.21 |                     -30.16 |                 0.6   |                     -0.097 | False        |
|       842 |                    9 |               51 |                  314.81 |                      188.89 |                     -49.64 |                 0.6   |                     -0.158 | False        |
|       442 |                    8 |               75 |                  315.71 |                      189.43 |                     -99.67 |                 0.6   |                     -0.316 | False        |
|       697 |                    9 |               52 |                  350.58 |                      210.35 |                    -153.35 |                 0.6   |                     -0.437 | False        |
|       472 |                    8 |               15 |                  377.85 |                      226.71 |                      -0.9  |                 0.6   |                     -0.002 | False        |
|       632 |                   14 |               68 |                  438.96 |                      263.38 |                     -62.68 |                 0.6   |                     -0.143 | False        |
|       471 |                   10 |               64 |                  455.9  |                      273.54 |                     -62.48 |                 0.6   |                     -0.137 | False        |


--- Diminishing Returns Check (Data-Driven Receipt Rate vs. Total Receipts) ---
| receipt_bin   |   median |       mean |   count |
|:--------------|---------:|-----------:|--------:|
| 0-19.99       | nan      | nan        |       0 |
| 20-49.99      | nan      | nan        |       0 |
| 50-99.99      |  -0.0745 |  -0.0745   |       2 |
| 100-199.99    |  -0.244  |  -0.244    |       1 |
| 200-499.99    |  -0.137  |  -0.140077 |      13 |
| 500-999.99    |   0.484  |   0.429444 |      18 |
| 1000-1499.99  |   0.647  |   0.641842 |      19 |
| 1500-1999.99  |   0.519  |   0.514667 |       6 |
| 2000+         |   0.379  |   0.343588 |      17 |
Overall median data-driven receipt rate (sane rates): 0.429
Overall mean data-driven receipt rate (sane rates): 0.351


--- Low Amount Penalty Check (-$10 for receipts > 0 & < $20 and days > 1) ---
Found 5 cases potentially subject to -$10 penalty by script logic.
Data for these cases (script vs data-driven receipt component):
|   case_id |   trip_duration_days |   total_receipts_amount |   calc_script_receipt_reimb |   data_driven_receipt_comp |
|----------:|---------------------:|------------------------:|----------------------------:|---------------------------:|
|         0 |                    3 |                    1.42 |                         -10 |                     -39.43 |
|         3 |                    2 |                    4.67 |                         -10 |                     -54.02 |
|         4 |                    3 |                    5.78 |                         -10 |                     -20.67 |
|         6 |                    3 |                    4.52 |                         -10 |                     -53.66 |
|        18 |                    2 |                   13.85 |                         -10 |                     -67.42 |
Median data_driven_receipt_comp for these penalty candidates: -53.66


--- Rounding Bug Check (.49 or .99 endings) ---
Median data-driven rate for receipts ending .49/.99 (sane rates, count 1): -0.072
Median data-driven rate for receipts NOT ending .49/.99 (sane rates, count 75): 0.430
Median data_driven_receipt_comp for receipts ending .49/.99 (all focused, count 1): $-168.02
Median data_driven_receipt_comp for receipts NOT ending .49/.99 (all focused, count 92): $534.40

## Receipt Analysis - Refining Low MPD Bonus Condition (Attempt 1)

Broader receipt analysis (miles <= 100) suggested that for low-mileage, low-receipt trips, the sum of non-receipt components might be overestimated by the script.
Hypothesis: The +0 MPD bonus for '0 < mpd < 100' might be too broadly applied to very short trips (in terms of total mileage).

Modified condition for the +0 Low MPD bonus in `calculate_reimbursement.py`:
- FROM: `if miles_per_day > 0 and miles_per_day < 100:`
- TO: `if miles_per_day > 0 and miles_per_day < 100 and miles > 50.0:`

### Evaluation Results After This Change:
- **Score**: 19857.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $197.57

Score (19857.00) did NOT improve from previous 19803.00. Reverting this specific change might be necessary if no further improvements are made in this path.

## Receipt Analysis - Implementing .49/.99 Rounding Bug (Attempt 1)

Previous change (restricting low MPD bonus) worsened score; reverted to 19803.00.
Hypothesis: Receipts ending in .49 or .99 receive a small bonus.
Analysis of (miles <= 100) cases suggested this was plausible.

Implemented in `calculate_reimbursement.py`:
- Added +$0.50 to total_reimbursement if `receipts` (input) ends in .49 or .99.

### Evaluation Results After Adding Rounding Bug Bonus:
- **Score**: 19804.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $197.04

Score (19804.00) did NOT improve from previous 19803.00.

## Receipt Analysis - Implementing .49/.99 Rounding Bug (Attempt 2)

Attempt 1 (+-bash.50 flat bonus) worsened score; reverted to 19803.00.
Hypothesis: Specific bonuses apply: +$0.51 if receipts end .49, +$0.01 if receipts end .99.

Implemented in `calculate_reimbursement.py`:
- If `receipts` ends in .49, add +$0.51 to total_reimbursement.
- If `receipts` ends in .99, add +$0.01 to total_reimbursement.

### Evaluation Results After This Change:
- **Score**: 19804.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $197.04

Score (19804.00) did NOT improve from previous 19803.00.

## Receipt Analysis - Implementing .49/.99 Rounding Bug (Attempt 3 - Pre-adjustment)

Previous attempts (final additive bonus) worsened score; reverted to 19803.00.
Hypothesis: Receipts ending .49/.99 are rounded up (e.g., by adding $0.01) *before* tiered percentage calculation.

Implemented in `calculate_reimbursement.py`:
- Before receipt tier logic, if input `receipts` ends .49 or .99, an `adjusted_receipts` variable is created by adding $0.01 and rounding to 2 decimal places.
- This `adjusted_receipts` is then used in all receipt tier calculations (e.g. for <20, <=500, <=1000, etc.).

### Evaluation Results After This Change:
- **Score**: 19803.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $197.03

Score (19803.00) did NOT improve from previous 19803.00.

## Receipt Analysis - Adjusting High-Amount Receipt Tiers (Attempt 1)

Previous .49/.99 bug attempts had no/marginal negative effect; reverted to 19803.00.
Hypothesis: Receipt reimbursement rates for higher amounts (> $1000) are too low.
Analysis of (miles <= 100) cases supported this, suggesting data-driven rates of ~0.64 for $1000-$1500 and ~0.52 for $1500-$2000, and ~0.38 for >$2000.

Implemented in `calculate_reimbursement.py`:
- Rate for receipts > $1000 and <= $1500 changed from 0.40 to 0.45.
- Rate for receipts > $1500 changed from 0.30 to 0.35.
(Rates for <= $500 (0.60) and <= $1000 (0.50) remain unchanged.)

### Evaluation Results After This Change:
- **Score**: 18487.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $183.87

Score improved from previous 19803.00.

## Receipt Analysis - Implementing .49/.99 Rounding Bug (Attempt 4 - ceil receipt component)

Previous attempts for .49/.99 bug were ineffective. Current score 18487.00 after receipt tier changes.
Hypothesis: If original `receipts` input ends .49/.99, the calculated `receipt_reimbursement` component (if >0) is rounded up to the nearest whole dollar using math.ceil().

Implemented this logic in `calculate_reimbursement.py`.

### Evaluation Results After This Change:
- **Score**: 18489.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $183.89

Score (18489.00) did NOT improve from previous 18487.00.

## Receipt Analysis - Adjusting Low Receipt Penalty (Attempt 1)

Score 18487.00. Previous .49/.99 bug attempts were ineffective and reverted.
Hypothesis: The -10.0 penalty for receipts < $20 (multi-day trips) is too small.
Analysis of low-mileage trips suggested data_driven_receipt_comp was often more negative than -10.0 for penalty cases.

Implemented in `calculate_reimbursement.py`:
- Changed penalty from -10.0 to -25.0 for: `if receipts < 20.00 and days > 1`.

### Evaluation Results After This Change:
- **Score**: 18481.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 3
- **Average error**: $183.81

Score improved from previous 18487.00.

## Receipt Analysis - Splitting Low-Amount Receipt Tier (Attempt 1)

Score 18481.00 after increasing low receipt penalty to -$25.0.
Hypothesis: The 0.60 rate for receipts <= $500 is too high for the lower end of that range (e.g. $20-$100).

Implemented in `calculate_reimbursement.py`:
- Added new tier: `elif receipts <= 100: receipt_reimbursement = receipts * 0.30`
- The existing tier `elif receipts <= 500: receipt_reimbursement = receipts * 0.60` now effectively covers $100.01 to $500.

### Evaluation Results After This Change:
- **Score**: 18464.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 2
- **Average error**: $183.64

Score improved from previous 18481.00.

## Receipt Analysis - Re-evaluation with Best Script (Score 18464.00)

The script now scores 18464.00 after changes to low-receipt penalty and splitting low-amount tiers.
Re-running the broader receipt analysis (miles <= 100) to see if 'data_driven_receipt_comp' for low receipt/low mileage trips is more reasonable, or if non-receipt components still seem overestimated for them.
Re-evaluating with script scoring 18464.00. Filter: Miles <= 100.
Found 93 cases matching criteria.

--- Data-Driven Receipt Component (Sorted by Receipts, first 30) ---
|   case_id |   trip_duration_days |   miles_traveled |   total_receipts_amount |   calc_script_receipt_reimb |   data_driven_receipt_comp |
|----------:|---------------------:|-----------------:|------------------------:|----------------------------:|---------------------------:|
|         0 |                    3 |               93 |                    1.42 |                      -25    |                     -39.43 |
|         1 |                    1 |               55 |                    3.6  |                        1.08 |                     -55.84 |
|         6 |                    3 |               41 |                    4.52 |                      -25    |                     -53.66 |
|         3 |                    2 |               13 |                    4.67 |                      -25    |                     -54.02 |
|         4 |                    3 |               88 |                    5.78 |                      -25    |                     -20.67 |
|        15 |                    1 |               58 |                    5.86 |                        1.76 |                     -66.4  |
|        17 |                    1 |               59 |                    8.31 |                        2.49 |                     -63.57 |
|         5 |                    1 |               76 |                   13.74 |                        4.12 |                     -35.73 |
|        18 |                    2 |               89 |                   13.85 |                      -25    |                     -67.42 |
|         2 |                    1 |               47 |                   17.97 |                        5.39 |                     -48.35 |
|        12 |                    2 |               21 |                   20.04 |                        6.01 |                     -57.6  |
|        11 |                    3 |               80 |                   21.05 |                        6.32 |                     -29.53 |
|       759 |                   12 |               37 |                   52.65 |                       15.79 |                     117.55 |
|       851 |                    5 |               14 |                   78.33 |                       23.5  |                    -201.42 |
|       875 |                   13 |                8 |                   78.44 |                       23.53 |                       9.07 |
|       190 |                    6 |               45 |                   81.59 |                       24.48 |                    -153.52 |
|       706 |                    1 |               85 |                   89.83 |                       26.95 |                     -23.77 |
|       625 |                   14 |               94 |                  105.94 |                       63.56 |                     376.11 |
|       677 |                   13 |               63 |                  107.92 |                       64.75 |                     -26.29 |
|       940 |                    7 |               83 |                  137.84 |                       82.7  |                    -315.49 |
|       556 |                   13 |               32 |                  232.43 |                      139.46 |                      86.56 |
|       831 |                    8 |               16 |                  259.02 |                      155.41 |                    -115.72 |
|       646 |                    4 |               18 |                  289.06 |                      173.44 |                     -79.56 |
|       548 |                    4 |               11 |                  312.01 |                      187.21 |                     -30.16 |
|       842 |                    9 |               51 |                  314.81 |                      188.89 |                     -49.64 |
|       442 |                    8 |               75 |                  315.71 |                      189.43 |                     -99.67 |
|       697 |                    9 |               52 |                  350.58 |                      210.35 |                    -153.35 |
|       472 |                    8 |               15 |                  377.85 |                      226.71 |                      -0.9  |
|       632 |                   14 |               68 |                  438.96 |                      263.38 |                     -62.68 |
|       471 |                   10 |               64 |                  455.9  |                      273.54 |                     -62.48 |


--- Data-Driven Receipt Rate vs. Total Receipts (Binned) ---
| receipt_bin   |   median |       mean |   count |
|:--------------|---------:|-----------:|--------:|
| (0)-19.99     |  nan     | nan        |       0 |
| 20-49.99      |   -1.403 |  -1.403    |       1 |
| 50-99.99      |   -0.265 |  -0.677    |       3 |
| 100-199.99    |   -0.244 |  -0.244    |       1 |
| 200-499.99    |   -0.137 |  -0.140077 |      13 |
| 500-999.99    |    0.484 |   0.429444 |      18 |
| 1000-1499.99  |    0.647 |   0.641842 |      19 |
| 1500-1999.99  |    0.519 |   0.514667 |       6 |
| 2000+         |    0.379 |   0.343588 |      17 |


--- Focus on Negative Data-Driven Receipt Components ---
Found 29 cases where data_driven_receipt_comp is negative.
Examples of negative data_driven_receipt_comp (first 10, sorted by magnitude):
|   case_id |   trip_duration_days |   miles_traveled |   total_receipts_amount |   calc_per_diem |   calc_mileage_incl_mpd |   calc_he_bonus |   expected_output |   data_driven_receipt_comp |
|----------:|---------------------:|-----------------:|------------------------:|----------------:|------------------------:|----------------:|------------------:|---------------------------:|
|       940 |                    7 |               83 |                  137.84 |             700 |                   98.14 |               0 |            482.65 |                    -315.49 |
|       851 |                    5 |               14 |                   78.33 |             550 |                   58.12 |               0 |            406.7  |                    -201.42 |
|       151 |                    4 |               69 |                 2321.49 |             400 |                   90.02 |               0 |            322    |                    -168.02 |
|       190 |                    6 |               45 |                   81.59 |             600 |                   76.1  |               0 |            522.58 |                    -153.52 |
|       697 |                    9 |               52 |                  350.58 |             675 |                   80.16 |               0 |            601.81 |                    -153.35 |
|       831 |                    8 |               16 |                  259.02 |             600 |                   59.28 |               0 |            543.56 |                    -115.72 |
|       442 |                    8 |               75 |                  315.71 |             600 |                   93.5  |               0 |            593.83 |                     -99.67 |
|       646 |                    4 |               18 |                  289.06 |             400 |                   60.44 |               0 |            380.88 |                     -79.56 |
|       747 |                   10 |               87 |                  498.96 |             750 |                  100.46 |               0 |            781.97 |                     -68.49 |
|        18 |                    2 |               89 |                   13.85 |             200 |                  101.62 |               0 |            234.2  |                     -67.42 |
Median 'data_driven_receipt_comp' for these negative cases: -57.60

## Receipt Analysis - Refining Low MPD Bonus Condition (Attempt 2 - Min Total Miles)

Re-evaluation of receipts (script score 18464.00) showed many low-mileage trips had negative 'data_driven_receipt_comp', suggesting non-receipt components were too high.
Hypothesis: The +0 MPD bonus for '0 < mpd < 100' is too generous for trips with very low *total* mileage (less than 25.0 miles).

Modified condition for the +0 Low MPD bonus in `calculate_reimbursement.py`:
- FROM: `if miles_per_day > 0 and miles_per_day < 100:`
- TO: `if miles_per_day > 0 and miles_per_day < 100 and miles >= 25.0:`

### Evaluation Results After This Change:
- **Score**: 18470.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 2
- **Average error**: $183.70

Score (18470.00) did NOT improve from previous 18464.00.

## Receipt Analysis - Adjusting Per Diem for 1-Day Ultra-Short Trips

Score 18464.00. Attempts to restrict low MPD bonus for short trips worsened score; reverted.
Persistent issue: Negative 'data_driven_receipt_comp' for some low-mileage/low-receipt trips, suggesting non-receipt components are too high.
Hypothesis: Per diem for 1-day ultra-short trips (e.g., <= 20.0 miles) is lower than the standard $100.

Implemented in `calculate_reimbursement.py`:
- For 1-7 day trips: if `days == 1 and miles <= 20.0`, per diem rate set to $50.0.
- Otherwise (for 1-7 days), per diem rate remains $100.0.

### Evaluation Results After This Change:
- **Score**: 18469.00
- **Exact matches (±$0.01)**: 0
- **Close matches (±$1.00)**: 2
- **Average error**: $183.69

Score (18469.00) did NOT improve from previous 18464.00.

## Receipt Analysis - Reverting 1-Day Ultra-Short Trip Per Diem Adjustment

The adjustment to per diem for 1-day ultra-short trips (rate $50 for days==1 and miles<=20) worsened the score to 18469.00 from 18464.00.
Reverted `calculate_reimbursement.py` to the version scoring 18464.00.
This concludes active changes for Task 3 (Receipt Processing Investigation) for now. Current best score is 18464.00.
Outstanding issues: .49/.99 rounding bug, and negative 'data_driven_receipt_comp' for some low-mileage trips.
