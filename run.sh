#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

# Execute the Python script with the provided arguments
python3 calculate_reimbursement.py "$1" "$2" "$3"