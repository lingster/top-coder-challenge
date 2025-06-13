# Model Iteration Log

## Baseline Model (Restored from analyzed content)
- Score: 20408.00
- Notes: Restored calculate_reimbursement.py to the version analyzed from read_files. run.sh was modified to correctly call the python script. This score is the confirmed baseline.

## Iteration 1: Kevin's Mileage Efficiency Bonus/Penalty
- Score: 20880.00
- Notes: Implemented Kevin's mileage efficiency logic.
    - Miles per day (mpd) calculated as `miles / days`.
    - Bonus/Penalty structure:
        - `180 <= mpd <= 220`: +$50.0 (Sweet spot)
        - `150 <= mpd < 180` or `220 < mpd <= 250`: +$20.0 (Mildly outside)
        - `mpd < 150` or `mpd > 250`: -$25.0 (Penalty)
    - This logic was added before the final rounding of `total_reimbursement`.
    - The score increased by 472.00, indicating the initial values/logic worsened performance. Further tuning is needed.

## Iteration 2: Lisa's Receipt Rounding Bug
- Score: 20410.00
- Notes: Implemented Lisa's receipt rounding bug.
    - Reverted code to baseline (20408.00 score) before applying this change.
    - Logic: If the fractional part of `receipts` is .49 or .99 (e.g., $XX.49 or $XX.99), a bonus of $0.75 is added to `total_reimbursement`.
    - This was implemented by converting `receipts` to a formatted string (`receipt_str = f"{receipts:.2f}"`) and checking `receipt_str.endswith(".49")` or `receipt_str.endswith(".99")`.
    - The logic was added before the final rounding of `total_reimbursement`.
    - The score increased by 2.00 from the baseline, indicating this specific implementation also slightly worsened performance.

## Iteration 3: Three-Tier Mileage System
- Score: 20427.00
- Notes: Implemented a three-tier mileage reimbursement system.
    - Reverted code to baseline (20408.00 score) before applying this change.
    - The existing two-tier mileage calculation was replaced with:
        - Tier 1 (0-100 miles): $0.58/mile
        - Tier 2 (101-500 miles): $0.50/mile for this segment
        - Tier 3 (>500 miles): $0.52/mile for this segment
    - The score increased by 19.00 from the baseline, indicating this change also worsened performance.

## Iteration 4: Refine "High Effort Bonus" Conditions
- Score: 20563.00
- Notes: Modified the "High Effort Bonus" logic.
    - Reverted code to baseline (20408.00 score) before applying this change.
    - Changed comment to "High Effort Bonus (Refined: daily_receipts condition removed)".
    - Commented out the nested `if not (days >= 8 and daily_receipts < 20 and miles > 800):` condition.
    - This makes the bonus of $350.0 apply if `days > 6 and days < 11 and miles > 800`, without the additional check on `daily_receipts` that was intended to prevent double penalizing or missing the bonus.
    - The score increased by 155.00 from the baseline, indicating this simplification significantly worsened performance.

## Iteration 5: Adjust Per Diem Threshold for High Effort
- Score: 20408.00
- Notes: Modified a per diem condition for 8-10 day trips.
    - Reverted code to baseline (20408.00 score) before applying this change.
    - Changed the line `if miles > 800 and daily_receipts > 20:` to `if miles > 800 and daily_receipts > 25:`. This condition influences when `current_per_diem_rate` is set to $75.0 for potentially high-effort trips.
    - The score remained unchanged at 20408.00, indicating this specific adjustment had no measurable impact on the overall score.

## Iteration 6: Adjust Per Diem Penalty Threshold
- Score: 20414.00
- Notes: Modified a per diem penalty condition for 8-10 day trips.
    - Reverted code to baseline (20408.00 score) before applying this change.
    - Changed the line `elif miles <= 800 and daily_receipts > 90:` to `elif miles <= 800 and daily_receipts > 85:`. This condition reduces the per diem rate to $60.0 for trips with high daily receipts but not high mileage.
    - The score increased by 6.00 from the baseline, indicating this specific adjustment slightly worsened performance.

## Iteration 7: Milder Kevin's Mileage Efficiency Bonus
- Score: 20398.00
- Notes: Re-implemented Kevin's mileage efficiency logic with milder bonuses and no penalties.
    - Reverted code to baseline (20408.00 score) before applying this change.
    - Logic:
        - `180 <= mpd <= 220`: +$25.0 (Sweet spot, was +$50 in Iteration 1)
        - `150 <= mpd < 180` or `220 < mpd <= 250`: +$10.0 (Mildly outside, was +$20 in Iteration 1)
        - No penalty for `mpd < 150` or `mpd > 250` (was -$25 in Iteration 1).
    - This logic was added before the "High Effort Bonus" block.
    - The score DECREASED by 10.00 from the baseline (20408.00 -> 20398.00). This is an IMPROVEMENT.

## Iteration 8: Fine-tune Milder Kevin's Bonus (Sweet Spot $25 -> $30)
- Score: 20397.00
- Notes: Adjusted the "Milder Kevin's Mileage Efficiency Bonus" from Iteration 7.
    - Started with the code from Iteration 7 (score 20398.00).
    - The "sweet spot" bonus (`180 <= mpd <= 220`) was increased from $25.0 to $30.0.
    - The "mildly outside" bonus remained $10.0. No penalties.
    - The score DECREASED by 1.00 from the previous iteration (20398.00 -> 20397.00). This is a further IMPROVEMENT.

## Iteration 9: Fine-tune Milder Kevin's Bonus ("Mildly Outside" $10 -> $12)
- Score: 20397.00
- Notes: Adjusted the "Milder Kevin's Mileage Efficiency Bonus" from Iteration 8.
    - Started with the code from Iteration 8 (score 20397.00).
    - The "sweet spot" bonus (`180 <= mpd <= 220`) remained $30.0.
    - The "mildly outside" bonus (`150 <= mpd < 180` or `220 < mpd <= 250`) was increased from $10.0 to $12.0.
    - No penalties.
    - The score remained UNCHANGED from the previous iteration (20397.00). This indicates the change had no measurable impact.

## Iteration 10: Fine-tune Milder Kevin's Bonus (Adjust MPD Thresholds)
- Score: 20385.00
- Notes: Adjusted MPD thresholds for "Milder Kevin's Mileage Efficiency Bonus".
    - Started with code from Iteration 8 (effectively, as Iteration 9's $12 bonus showed no change from $10 and was reset to $10 at start of this subtask). Sweet spot bonus $30, mildly outside $10.
    - Original MPD thresholds:
        - Sweet spot: `180 <= mpd <= 220`
        - Mildly outside: `(150 <= mpd < 180) or (220 < mpd <= 250)`
    - New MPD thresholds:
        - Sweet spot: `185 <= mpd <= 215` (+$30 bonus)
        - Mildly outside: `(150 <= mpd < 185) or (215 < mpd <= 250)` (+$10 bonus)
    - The score DECREASED by 12.00 from the previous effective score of 20397.00. This is a significant IMPROVEMENT.

## Iteration 11: Fine-tune Milder Kevin's Bonus (Adjust "Mildly Outside" MPD Outer Boundaries)
- Score: 20387.00
- Notes: Adjusted the "Mildly Outside" MPD outer boundaries for "Milder Kevin's Mileage Efficiency Bonus".
    - Started with code from Iteration 10 (score 20385.00). Sweet spot bonus $30 (185-215 mpd), mildly outside $10 (150-184 mpd or 216-250 mpd).
    - "Mildly outside" MPD thresholds changed from `(150 <= mpd < 185) or (215 < mpd <= 250)` to `(160 <= mpd < 185) or (215 < mpd <= 240)`.
    - The "sweet spot" thresholds and bonus amounts remained unchanged.
    - The score INCREASED by 2.00 from the previous iteration (20385.00 -> 20387.00), indicating this change slightly worsened performance.
