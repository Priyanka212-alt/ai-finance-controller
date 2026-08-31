import pandas as pd


# Load data
bank_data = pd.read_csv("data/bank_transactions.csv")
settlement_data = pd.read_csv("data/settlements.csv")


# Reconcile bank transactions with settlements
reconciled_data = bank_data.merge(
    settlement_data,
    on="reference",
    how="left"
)


# Check amount
reconciled_data["amount_status"] = (
    reconciled_data["amount_x"] == reconciled_data["amount_y"]
)


# Check date
reconciled_data["date_status"] = (
    reconciled_data["transaction_date"]
    == reconciled_data["settlement_date"]
)


# Overall reconciliation status
reconciled_data["reconciliation_status"] = (
    reconciled_data["amount_status"]
    & reconciled_data["date_status"]
)


# Classify exceptions
reconciled_data["exception_type"] = "MATCH"

reconciled_data.loc[
    reconciled_data["settlement_id"].isna(),
    "exception_type"
] = "MISSING_SETTLEMENT"

reconciled_data.loc[
    (~reconciled_data["amount_status"])
    & reconciled_data["date_status"]
    & reconciled_data["settlement_id"].notna(),
    "exception_type"
] = "AMOUNT_MISMATCH"

reconciled_data.loc[
    reconciled_data["amount_status"]
    & (~reconciled_data["date_status"])
    & reconciled_data["settlement_id"].notna(),
    "exception_type"
] = "DATE_MISMATCH"


# Calculate reconciliation metrics
match_count = (
    reconciled_data["exception_type"] == "MATCH"
).sum()

total_count = len(reconciled_data)

exception_count = total_count - match_count

match_rate = (match_count / total_count) * 100


# Create exception report
exceptions = reconciled_data[
    reconciled_data["exception_type"] != "MATCH"
].copy()


exceptions.to_csv(
    "data/exceptions.csv",
    index=False
)


# Amount exception analysis
amount_exceptions = reconciled_data[
    reconciled_data["exception_type"] == "AMOUNT_MISMATCH"
].copy()

amount_exceptions["amount_difference"] = (
    amount_exceptions["amount_y"]
    - amount_exceptions["amount_x"]
)

total_amount_difference = amount_exceptions[
    "amount_difference"
].sum()


# Missing settlement analysis
missing_settlements = reconciled_data[
    reconciled_data["exception_type"] == "MISSING_SETTLEMENT"
]

missing_settlement_amount = missing_settlements[
    "amount_x"
].sum()


# Cash position
expected_total = bank_data["amount"].sum()

actual_total = settlement_data["amount"].sum()

cash_difference = expected_total - actual_total


# Final report
print("\nFINANCE RECONCILIATION SUMMARY")
print("------------------------------")

print("Total records:", total_count)
print("Matched:", match_count)
print("Exceptions:", exception_count)
print("Match rate:", round(match_rate, 2), "%")

print("\nEXCEPTION BREAKDOWN")
print("-------------------")

exception_counts = reconciled_data[
    reconciled_data["exception_type"] != "MATCH"
]["exception_type"].value_counts()

print(exception_counts)

print("\nEXCEPTION RATES")
print("---------------")

for exception_type, count in exception_counts.items():
    percentage = (count / exception_count) * 100
    print(
        exception_type + ":",
        round(percentage, 2),
        "%"
    )

print("\nAMOUNT EXCEPTION SUMMARY")
print("------------------------")
print(
    "Total amount difference:",
    round(total_amount_difference, 2)
)

print("\nMISSING SETTLEMENT SUMMARY")
print("--------------------------")
print(
    "Total missing settlement amount:",
    round(missing_settlement_amount, 2)
)

print("\nCASH POSITION")
print("-------------")
print("Expected cash:", round(expected_total, 2))
print("Actual settled cash:", round(actual_total, 2))
print("Cash difference:", round(cash_difference, 2))

print("\nEXCEPTIONS")
print("----------")

if exceptions.empty:
    print("No exceptions found.")
else:
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

print("\nException report saved to data/exceptions.csv")