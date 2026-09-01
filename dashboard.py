import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI Finance Controller",
    page_icon="💰",
    layout="wide"
)

# Load data
bank_data = pd.read_csv("data/bank_transactions.csv")
settlement_data = pd.read_csv("data/settlements.csv")
exceptions = pd.read_csv("data/exceptions.csv")

# Calculate metrics
total_records = len(bank_data)
exception_count = len(exceptions)
matched_count = total_records - exception_count
match_rate = (matched_count / total_records) * 100

expected_cash = bank_data["amount"].sum()
actual_cash = settlement_data["amount"].sum()
cash_difference = expected_cash - actual_cash

missing_settlements = exceptions[
    exceptions["exception_type"] == "MISSING_SETTLEMENT"
]

missing_amount = missing_settlements["amount_x"].sum()

amount_mismatches = exceptions[
    exceptions["exception_type"] == "AMOUNT_MISMATCH"
]

amount_difference = (
    amount_mismatches["amount_y"] - amount_mismatches["amount_x"]
).sum()

# Title
st.title("💰 AI Finance Controller")
st.subheader("Finance Reconciliation Dashboard")

st.divider()

# Key metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    total_records
)

col2.metric(
    "Match Rate",
    f"{match_rate:.2f}%"
)

col3.metric(
    "Exceptions",
    exception_count
)

col4.metric(
    "Cash Difference",
    f"₹{cash_difference:,.0f}"
)

st.divider()

# Financial position
st.header("Cash Position")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Expected Cash",
    f"₹{expected_cash:,.0f}"
)

col2.metric(
    "Actual Settled Cash",
    f"₹{actual_cash:,.0f}"
)

col3.metric(
    "Cash Shortfall",
    f"₹{cash_difference:,.0f}"
)

st.divider()

# Exception breakdown
st.header("Exception Breakdown")

exception_counts = exceptions["exception_type"].value_counts()

st.bar_chart(exception_counts)

st.divider()

# Financial impact
st.header("Financial Impact")

col1, col2 = st.columns(2)

col1.metric(
    "Missing Settlement Amount",
    f"₹{missing_amount:,.0f}"
)

col2.metric(
    "Amount Mismatch Difference",
    f"₹{amount_difference:,.0f}"
)

st.divider()

# Risk section
st.header("Risk & Management Attention")

if not exceptions.empty:

    highest_risk = exceptions.sort_values(
        by="risk_score",
        ascending=False
    ).iloc[0]

    st.warning(
        f"Highest Risk Exception: {highest_risk['reference']}"
    )

    st.write(
        f"**Risk Score:** {highest_risk['risk_score']}"
    )

    st.write(
        f"**Priority:** {highest_risk['priority']}"
    )

    st.write(
        f"**Recommended Action:** "
        f"{highest_risk['recommended_action']}"
    )

st.divider()

# Exception table
st.header("Exception Details")

st.dataframe(
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
    ],
    use_container_width=True
)

st.divider()

# Controller decision
st.header("AI Finance Controller Decision")

if cash_difference > 0:

    st.error(
        "CASH SHORTFALL DETECTED"
    )

    st.write(
        f"Expected cash is higher than settled cash "
        f"by **₹{cash_difference:,.2f}**."
    )

    st.write(
        "Manual review is required for the identified exceptions."
    )

else:

    st.success(
        "NO CASH SHORTFALL DETECTED"
    )