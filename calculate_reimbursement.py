import sys

# numpy as np was removed as it's not used in the active code path.

def calculate_reimbursement(days_arg, miles_arg, receipts_arg):
    days = int(days_arg)
    miles = float(miles_arg)
    receipts = float(receipts_arg)

    if days <= 0:
        return 0.0

    # Derived features
    daily_receipts = receipts / days if days > 0 else 0
    # miles_per_day is implicitly used via miles > 800 for HE bonus and some 8-10 day PD conditions.

    # --- Per Diem Calculation (logic from model scoring 20408) ---
    current_per_diem_rate = 0.0
    if days >= 11: # "Very long" trips
        if daily_receipts < 30.0:
            current_per_diem_rate = 50.0
        elif daily_receipts < 75.0:
            current_per_diem_rate = 60.0
        else:
            current_per_diem_rate = 65.0
    elif days >= 8: # Trips 8-10 days
        if miles > 800 and daily_receipts > 20.0: # Min $20/day receipts to qualify for this rate with HE
            current_per_diem_rate = 75.0
        elif miles <= 800 and daily_receipts > 90.0: # Penalized for high spend, low effort
            current_per_diem_rate = 60.0
        elif daily_receipts < 20.0: # Penalized for very low spend
            current_per_diem_rate = 60.0
        else: # Default for 8-10 days not otherwise specified
            current_per_diem_rate = 75.0
    else: # Trips 1-7 days
        current_per_diem_rate = 100.0

    per_diem_total = days * current_per_diem_rate

    # 5-Day Trip Bonus
    if days == 5:
        per_diem_total += 50.0

    # --- Mileage Reimbursement (from model scoring 20408) ---
    mileage_reimbursement = 0.0
    if miles <= 100:
        mileage_reimbursement = miles * 0.58
    else:
        mileage_reimbursement = (100 * 0.58) + ((miles - 100) * 0.50)

    # --- Receipt Reimbursement (from model scoring 20408) ---
    receipt_reimbursement = 0.0
    if receipts < 20.00 and days > 1:
        receipt_reimbursement = -10.0
    elif receipts <= 500: # This covers $20-$500 for multi-day, or $0-$500 for 1-day
        receipt_reimbursement = receipts * 0.60
    elif receipts <= 1000: # $500.01 - $1000
        receipt_reimbursement = receipts * 0.50
    elif receipts <= 1500: # $1000.01 - $1500
        receipt_reimbursement = receipts * 0.40
    else: # > $1500
        receipt_reimbursement = receipts * 0.30

    total_reimbursement = per_diem_total + mileage_reimbursement + receipt_reimbursement

    # --- High Effort Bonus (from model scoring 20408) ---
    apply_HE_bonus = False
    # HE_BONUS_DAYS_MIN = 7 (implies days > 6)
    # HE_BONUS_DAYS_MAX = 10 (implies days < 11)
    # HE_BONUS_MILES_MIN = 800
    # HE_BONUS_RECEIPTS_PER_DAY_MIN = 20.0
    # HE_BONUS_AMOUNT = 350.0

    if days > 6 and days < 11 and miles > 800: # Main conditions for HE bonus
        # Sub-condition: Do not apply if per diem already penalized for very low daily receipts on an 8-10 day high mileage trip
        # This means if (days is 8-10 AND daily_receipts < 20 AND miles > 800), this path to $60 PD was taken.
        # The bonus should still apply if the PD rate was $75 (e.g. daily_receipts > 20 for HE)
        is_penalized_low_receipt_he_trip = (
            (days >= 8) and # and days < 11 (implicit from outer if)
            (daily_receipts < 20.0) and
            (miles > 800) # This condition is actually identical to the HE bonus miles condition
        )
        if not is_penalized_low_receipt_he_trip:
            apply_HE_bonus = True

    if apply_HE_bonus:
        total_reimbursement += 350.0 # HE_BONUS_AMOUNT

    return round(total_reimbursement, 2)

# --- Main Execution ---
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <days> <miles> <receipts>", file=sys.stderr)
        sys.exit(1)

    try:
        days_arg_main = int(sys.argv[1])
        miles_arg_main = float(sys.argv[2])
        receipts_arg_main = float(sys.argv[3])

        if days_arg_main <= 0:
             print("Error: Trip duration must be at least 1 day.", file=sys.stderr)
             print(0.0)
             sys.exit(0)

    except ValueError:
        print("Error: Input arguments must be convertible to the correct types (int, float, float).", file=sys.stderr)
        sys.exit(1)

    result = calculate_reimbursement(days_arg_main, miles_arg_main, receipts_arg_main)
    print(result)
