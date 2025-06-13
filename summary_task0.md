# Task 0: Baseline Evaluation Summary

## Objective
Evaluate the initial `calculate_reimbursement.py` script to confirm the starting score and establish a baseline for future improvements.

## Actions
1. Installed `jq` and `bc` dependencies which were missing in the environment.
2. Executed the `./eval.sh` script.

## Results
The evaluation script ran successfully against 1,000 test cases.

*   **Baseline Score:** 20408.00
*   **Exact Matches (±$0.01):** 0 (0%)
*   **Close Matches (±$1.00):** 4 (0.4%)
*   **Average Error:** $203.08
*   **Maximum Error:** $814.47

## Observations
The initial script has a very high error rate, indicating significant discrepancies between its calculations and the expected reimbursement amounts. This score serves as the starting point for our reverse-engineering efforts.

## High-Error Cases Noted by `eval.sh`
The evaluation script highlighted several cases with particularly high errors:
*   **Case 152:** 4 days, 69 miles, $2321.49 receipts (Expected: $322.00, Got: $1136.47, Error: $814.47)
*   **Case 996:** 1 day, 1082 miles, $1809.49 receipts (Expected: $446.94, Got: $1191.85, Error: $744.91)
*   **Case 684:** 8 days, 795 miles, $1645.99 receipts (Expected: $644.69, Got: $1379.30, Error: $734.61)
*   **Case 711:** 5 days, 516 miles, $1878.49 receipts (Expected: $669.85, Got: $1379.55, Error: $709.70)
*   **Case 520:** 14 days, 481 miles, $939.99 receipts (Expected: $877.17, Got: $1558.49, Error: $681.32)

These cases will be valuable for future analysis.
