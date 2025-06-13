import sys

def calculate_reimbursement(days, miles, receipts):
    # Per Diem Rate Determination
    current_per_diem_rate = 0.0
    daily_receipts = receipts / days if days > 0 else 0.0 # Ensure float if receipts is float
    miles_per_day = miles / days if days > 0 else 0.0 # Ensure float if miles is float

    if days >= 11: # "Very long" trips
        if daily_receipts < 30.0:
            current_per_diem_rate = 50.0
        elif daily_receipts < 75.0:
            current_per_diem_rate = 60.0
        else:
            current_per_diem_rate = 65.0
    elif days >= 8: # Trips 8-10 days
        # If it qualifies for High Effort Bonus (high miles, not excessively low daily receipts), use standard rate. Bonus adds on top.
        if miles > 800 and daily_receipts > 20:
            current_per_diem_rate = 75.0 # Standard rate, bonus will make it effectively higher
        # Penalized for high daily spend if not high effort (miles <=800)
        elif miles <= 800 and daily_receipts > 90:
            current_per_diem_rate = 60.0
        # Penalized for very low daily receipts if not high effort (miles <=800, or high miles but daily_receipts <=20)
        elif daily_receipts < 20: # This will also catch (miles > 800 and daily_receipts <=20)
             current_per_diem_rate = 60.0
        else: # Default for 8-10 days (e.g. moderate miles/receipts)
            current_per_diem_rate = 75.0
    else: # Trips 1-7 days
        current_per_diem_rate = 100.0 # Default for shorter trips

    per_diem_total = days * current_per_diem_rate

    # 5-Day Trip Bonus (Lisa) - applied after base per diem calculation
    if days == 5:
        per_diem_total += 50.0

    # Mileage Reimbursement
    mileage_reimbursement = 0.0
    if miles <= 100:
        mileage_reimbursement = miles * 0.58
    else:
        # Secondary mileage rate $0.50/mile
        mileage_reimbursement = (100 * 0.58) + ((miles - 100) * 0.50)

    # Receipt Reimbursement
    receipt_reimbursement = 0.0
    # Reverted to the logic from the 20408-scoring model
    if receipts < 20.00 and days > 1:
        receipt_reimbursement = -25.0
    elif receipts <= 500:
        receipt_reimbursement = receipts * 0.60
    elif receipts <= 1000:
        receipt_reimbursement = receipts * 0.50
    elif receipts <= 1500:
        receipt_reimbursement = receipts * 0.45
    else: # > $1500
        receipt_reimbursement = receipts * 0.35

    total_reimbursement = per_diem_total + mileage_reimbursement + receipt_reimbursement

    # High Effort Bonus (Simplified condition, similar to 23343 score model)
    if days > 6 and days < 11 and miles > 800:
        # Bonus should not apply if per diem already penalized for low spend on high effort trip
        if not (days >= 8 and daily_receipts < 20 and miles > 800): # Avoid double penalizing/missing bonus
             total_reimbursement += 350.0

    # MPD-Based Efficiency Bonuses
    if miles_per_day > 0 and miles_per_day < 100: # Bonus for 0-99 mpd
        total_reimbursement += 50.0
    if miles_per_day >= 200 and miles_per_day < 225:
        total_reimbursement += 60.0
    if miles_per_day >= 300:
        total_reimbursement += 120.0

    # Ensure the final output is just the number
    return round(total_reimbursement, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        # This error message goes to stderr, so it won't interfere with stdout capture by eval.sh
        print(f"Usage: python {sys.argv[0]} <days> <miles> <receipts>", file=sys.stderr)
        sys.exit(1)

    try:
        days_arg = int(sys.argv[1])
        miles_arg = float(sys.argv[2]) # Changed to float to handle fractional miles
        receipts_arg = float(sys.argv[3])
    except ValueError:
        print("Error: Input arguments must be convertible to the correct types (int, float, float).", file=sys.stderr)
        sys.exit(1)


    result = calculate_reimbursement(days_arg, miles_arg, receipts_arg)
    print(result)
