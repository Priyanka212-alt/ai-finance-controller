import pandas as pd

bank_data = pd.read_csv("data/bank_transactions.csv")

# print(bank_data)
# print(bank_data.shape)
# print(bank_data.columns)

settlement_data = pd.read_csv("data/settlements.csv")


reconciled_data = bank_data.merge(
    settlement_data,
    on="reference",
    how="left"
)
# print(reconciled_data["settlement_id"].isna())

# print(reconciled_data)
# print(reconciled_data["amount_x"] == reconciled_data["amount_y"])

reconciled_data["amount_status"] = (
    reconciled_data["amount_x"] == reconciled_data["amount_y"]
)
#print(reconciled_data[["reference", "amount_x", "amount_y", "amount_status"]])

reconciled_data["date_status"] = (
    reconciled_data["transaction_date"] ==
    reconciled_data["settlement_date"]
)

# print(
#     reconciled_data[
#         ["reference", "transaction_date", "settlement_date", "date_status"]
#     ]
# )

reconciled_data["reconciliation_status"] = (
    reconciled_data["amount_status"] &
    reconciled_data["date_status"]
)
# print(
#     reconciled_data[
#         ["reference", "amount_status", "date_status", "reconciliation_status"]
#     ]
# )

reconciled_data["exception_type"] = "MATCH"
reconciled_data.loc[
    reconciled_data["settlement_id"].isna(),
    "exception_type"
] = "MISSING_SETTLEMENT"

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

# print(
#     reconciled_data[
#         ["reference", "amount_status", "date_status", "exception_type"]
#     ]
# )

match_count = (
    reconciled_data["exception_type"] == "MATCH"
).sum()

total_count = len(reconciled_data)

match_rate = (match_count / total_count) * 100

print("Match count:", match_count)
print("Total records:", total_count)
print("Match rate:", match_rate, "%")

missing_bank = settlement_data.merge(
    bank_data,
    on="reference",
    how="left",
    indicator=True
)

missing_bank = missing_bank[missing_bank["_merge"] == "left_only"]

# print("Missing bank transactions:")
# print(missing_bank)

exceptions = reconciled_data[
    reconciled_data["exception_type"] != "MATCH"
]

print("Exceptions:")
print(
    exceptions[
        [
            "reference",
            "amount_x",
            "amount_y",
            "transaction_date",
            "settlement_date",
            "exception_type"
        ]
    ]
)
print("Exception counts:")
print(reconciled_data["exception_type"].value_counts())
exceptions.to_csv("data/exceptions.csv", index=False)

print("Exception report saved.")

exception_count = total_count - match_count

print("\nFINANCE RECONCILIATION SUMMARY")
print("------------------------------")
print("Total records:", total_count)
print("Matched:", match_count)
print("Exceptions:", exception_count)
print("Match rate:", round(match_rate, 2), "%")

print("\nException breakdown:")
print(reconciled_data["exception_type"].value_counts())

amount_exceptions = reconciled_data[
    reconciled_data["exception_type"] == "AMOUNT_MISMATCH"
].copy()

amount_exceptions["amount_difference"] = (
    amount_exceptions["amount_y"] -
    amount_exceptions["amount_x"]
)

print("\nAMOUNT EXCEPTION SUMMARY")
print("------------------------")
print(
    "Total amount difference:",
    round(amount_exceptions["amount_difference"].sum(), 2)
)

missing_settlements = reconciled_data[
    reconciled_data["exception_type"] == "MISSING_SETTLEMENT"
]

missing_settlement_amount = missing_settlements["amount_x"].sum()

print("\nMISSING SETTLEMENT SUMMARY")
print("--------------------------")
print(
    "Total missing settlement amount:",
    round(missing_settlement_amount, 2)
)

expected_total = bank_data["amount"].sum()

actual_total = settlement_data["amount"].sum()

cash_difference = expected_total - actual_total

print("\nCASH POSITION")
print("-------------")
print("Expected cash:", expected_total)
print("Actual settled cash:", actual_total)
print("Cash difference:", cash_difference)