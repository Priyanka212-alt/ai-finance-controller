import pandas as pd
import time

start_time = time.time()

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

end_time = time.time()

processing_time = end_time - start_time

records_per_second = total_count / processing_time

print("\nPROCESSING PERFORMANCE")
print("----------------------")
print("Records processed:", total_count)
print("Processing time:", round(processing_time, 4), "seconds")
print("Records per second:", round(records_per_second, 2))

# Recommended action for each exception

exceptions["recommended_action"] = ""
exceptions["priority"] = ""

exceptions["risk_score"] = 0

exceptions.loc[
    exceptions["exception_type"] == "AMOUNT_MISMATCH",
    "risk_score"
] = 80

exceptions.loc[
    exceptions["exception_type"] == "DATE_MISMATCH",
    "risk_score"
] = 50

exceptions.loc[
    exceptions["exception_type"] == "MISSING_SETTLEMENT",
    "risk_score"
] = 100

exceptions.loc[
    exceptions["exception_type"] == "MISSING_SETTLEMENT",
    "priority"
] = "HIGH"

exceptions.loc[
    exceptions["exception_type"] == "AMOUNT_MISMATCH",
    "priority"
] = "HIGH"

exceptions.loc[
    exceptions["exception_type"] == "DATE_MISMATCH",
    "priority"
] = "MEDIUM"

exceptions.loc[
    exceptions["exception_type"] == "AMOUNT_MISMATCH",
    "recommended_action"
] = "Review settlement amount"

exceptions.loc[
    exceptions["exception_type"] == "DATE_MISMATCH",
    "recommended_action"
] = "Investigate settlement timing"

exceptions.loc[
    exceptions["exception_type"] == "MISSING_SETTLEMENT",
    "recommended_action"
] = "Follow up with payment processor"


print("\nEXCEPTIONS")
print("----------")

if exceptions.empty:

    print("No exceptions found.")

else:
    exceptions = exceptions.sort_values(
    by="risk_score",
    ascending=False
    )

    print(
        exceptions[
            [
                "reference",
                "amount_x",
                "amount_y",
                "transaction_date",
                "settlement_date",
                "exception_type",
                "recommended_action",
                "priority",
                "risk_score"
            ]
        ]
    )


exceptions.to_csv(
    "data/exceptions.csv",
    index=False
)

print("\nException report saved to data/exceptions.csv")

print("\nFINANCE CONTROLLER INSIGHTS")
print("---------------------------")

if exception_count == 0:
    print("No financial exceptions detected.")
else:
    highest_risk = exceptions.iloc[0]

    print("Highest risk exception:", highest_risk["reference"])
    print("Highest risk score:", highest_risk["risk_score"])
    print("Recommended action:", highest_risk["recommended_action"])

    print("\nManagement attention required:")
    
    if cash_difference > 0:
        print(
            "Expected cash is higher than settled cash by ₹",
            round(cash_difference, 2)
        )

    if missing_settlement_amount > 0:
        print(
            "₹",
            round(missing_settlement_amount, 2),
            "is tied to missing settlements."
        )

    if amount_exceptions["amount_difference"].sum() != 0:
        print(
            "₹",
            round(amount_exceptions["amount_difference"].sum(), 2),
            "difference exists across amount mismatches."
        )
print("\nAI FINANCE CONTROLLER DECISION")
print("------------------------------")

if cash_difference > 0:
    print("Overall status: CASH SHORTFALL DETECTED")
else:
    print("Overall status: CASH POSITION BALANCED")

if highest_risk["risk_score"] >= 80:
    print("Urgency: HIGH")
elif highest_risk["risk_score"] >= 50:
    print("Urgency: MEDIUM")
else:
    print("Urgency: LOW")

print("Primary issue:", highest_risk["exception_type"])

if missing_settlement_amount > 0:
    print(
        "Priority recommendation: Resolve missing settlements totaling ₹",
        round(missing_settlement_amount, 2)
    )
elif total_amount_difference != 0:
    print(
        "Priority recommendation: Review settlement amount differences totaling ₹",
        round(abs(total_amount_difference), 2)
    )
else:
    print("Priority recommendation: Investigate settlement timing.")

print("Controller decision: Manual review required.")

# Management report

report = f"""
AI FINANCE CONTROLLER - MANAGEMENT REPORT
=========================================

RECONCILIATION
--------------
Total records: {total_count}
Matched records: {match_count}
Exceptions: {exception_count}
Match rate: {match_rate:.2f}%

EXCEPTION BREAKDOWN
-------------------
Amount mismatches: {exception_counts.get("AMOUNT_MISMATCH", 0)}
Date mismatches: {exception_counts.get("DATE_MISMATCH", 0)}
Missing settlements: {exception_counts.get("MISSING_SETTLEMENT", 0)}

FINANCIAL IMPACT
----------------
Expected cash: ₹{expected_total:.2f}
Actual settled cash: ₹{actual_total:.2f}
Cash difference: ₹{cash_difference:.2f}
Amount mismatch difference: ₹{total_amount_difference:.2f}
Missing settlement amount: ₹{missing_settlement_amount:.2f}

RISK
----
Highest risk exception: {highest_risk["reference"]}
Risk score: {highest_risk["risk_score"]}
Priority: {highest_risk["priority"]}
Recommended action: {highest_risk["recommended_action"]}

CONTROLLER DECISION
-------------------
Overall status: CASH SHORTFALL DETECTED
Urgency: HIGH
Manual review required.
"""

with open("data/management_report.txt", "w", encoding="utf-8") as file:
    file.write(report)

print("\nManagement report saved to data/management_report.txt")


