# AI Finance Controller

An AI Finance Controller that reconciles bank transactions with settlement records, detects financial exceptions, evaluates risk, and reports the current cash position.

## Project Objective

The goal of this project is to automate a finance-operations reconciliation workflow across a batch of financial records.

The controller compares bank transactions against settlement records and identifies transactions that require manual attention.

## What the System Does

The Finance Controller:

1. Loads bank transaction data.
2. Loads settlement data.
3. Matches records using transaction references.
4. Compares transaction amounts.
5. Compares transaction and settlement dates.
6. Classifies exceptions.
7. Calculates reconciliation metrics.
8. Calculates financial impact.
9. Assigns risk scores and priorities.
10. Generates recommended actions.
11. Calculates the expected and actual cash position.
12. Produces a management report.
13. Displays the results through a Streamlit dashboard.

## Exception Types

The system identifies three main exception types:

- `AMOUNT_MISMATCH`
- `DATE_MISMATCH`
- `MISSING_SETTLEMENT`

Each exception receives:

- Recommended action
- Priority
- Risk score

## Current Results

The current synthetic dataset contains:

- Total records: 60
- Matched records: 50
- Exceptions: 10
- Match rate: 83.33%

Exception breakdown:

- Amount mismatches: 5
- Date mismatches: 4
- Missing settlements: 1

Financial impact:

- Amount mismatch difference: ₹550
- Missing settlement amount: ₹6,000
- Expected cash: ₹213,000
- Actual settled cash: ₹207,550
- Cash difference: ₹5,450

The highest-risk exception is `REF1055`, a missing settlement with a risk score of 100.

## Processing Performance

The controller processes the complete 60-record batch automatically and reports processing time and records processed per second.

## Project Structure

```text
ai-finance-controller/
│
├── data/
│   ├── bank_transactions.csv
│   ├── settlements.csv
│   ├── exceptions.csv
│   └── management_report.txt
│
├── main.py
├── dashboard.py
├── generate_data.py
└── README.md