import pandas as pd

bank_data = pd.read_csv("data/bank_transactions.csv")

print(bank_data)
print(bank_data.shape)
print(bank_data.columns)

settlement_data = pd.read_csv("data/settlements.csv")


reconciled_data = bank_data.merge(
    settlement_data,
    on="reference"
)

print(reconciled_data)
print(reconciled_data["amount_x"] == reconciled_data["amount_y"])

reconciled_data["amount_status"] = (
    reconciled_data["amount_x"] == reconciled_data["amount_y"]
)
print(reconciled_data[["reference", "amount_x", "amount_y", "amount_status"]])

reconciled_data["date_status"] = (
    reconciled_data["transaction_date"] ==
    reconciled_data["settlement_date"]
)

print(
    reconciled_data[
        ["reference", "transaction_date", "settlement_date", "date_status"]
    ]
)

reconciled_data["reconciliation_status"] = (
    reconciled_data["amount_status"] &
    reconciled_data["date_status"]
)
print(
    reconciled_data[
        ["reference", "amount_status", "date_status", "reconciliation_status"]
    ]
)

reconciled_data["exception_type"] = "MATCH"

reconciled_data.loc[
    (~reconciled_data["amount_status"]) &
    (reconciled_data["date_status"]),
    "exception_type"
] = "AMOUNT_MISMATCH"

reconciled_data.loc[
    (reconciled_data["amount_status"]) &
    (~reconciled_data["date_status"]),
    "exception_type"
] = "DATE_MISMATCH"

print(
    reconciled_data[
        ["reference", "amount_status", "date_status", "exception_type"]
    ]
)

match_count = (
    reconciled_data["exception_type"] == "MATCH"
).sum()

total_count = len(reconciled_data)

match_rate = (match_count / total_count) * 100

print("Match count:", match_count)
print("Total records:", total_count)
print("Match rate:", match_rate, "%")