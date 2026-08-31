import pandas as pd

records = []

merchants = [
    "Amazon",
    "Flipkart",
    "Myntra",
    "Swiggy",
    "Zomato",
    "Blinkit",
    "Meesho",
    "Ajio",
    "Zepto",
    "Uber"
]

for i in range(1, 61):
    reference = f"REF{1000 + i}"
    transaction_id = f"B{i:03d}"
    settlement_id = f"S{i:03d}"

    merchant = merchants[(i - 1) % len(merchants)]
    amount = 500 + (i * 100)
    date = pd.Timestamp("2026-08-01") + pd.Timedelta(days=(i - 1) % 20)

    records.append([
        transaction_id,
        date.strftime("%Y-%m-%d"),
        amount,
        merchant,
        reference,
        settlement_id
    ])

bank_data = pd.DataFrame(
    records,
    columns=[
        "transaction_id",
        "transaction_date",
        "amount",
        "merchant",
        "reference",
        "settlement_id"
    ]
)

settlement_data = bank_data[
    ["settlement_id", "transaction_date", "amount", "merchant", "reference"]
].copy()

settlement_data = settlement_data.rename(
    columns={"transaction_date": "settlement_date"}
)

bank_data = bank_data.drop(columns=["settlement_id"])

settlement_data.loc[9, "amount"] += 50
settlement_data.loc[19, "amount"] += 100
settlement_data.loc[29, "amount"] += 75
settlement_data.loc[39, "amount"] += 125
settlement_data.loc[49, "amount"] += 200

settlement_data.loc[14, "settlement_date"] = "2026-08-25"
settlement_data.loc[24, "settlement_date"] = "2026-08-26"
settlement_data.loc[34, "settlement_date"] = "2026-08-27"
settlement_data.loc[44, "settlement_date"] = "2026-08-28"
settlement_data.loc[54, "settlement_date"] = "2026-08-29"

settlement_data = settlement_data.drop(index=[54])

bank_data.to_csv("data/bank_transactions.csv", index=False)
settlement_data.to_csv("data/settlements.csv", index=False)

print("Generated 60 bank transactions.")
print(f"Generated {len(settlement_data)} settlement records.")