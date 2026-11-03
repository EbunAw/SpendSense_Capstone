
from pathlib import Path
import pandas as pd


# ============================================================
# 1. PROJECT PATHS AND DATASET LOADING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "laramee26openBankTransactionData.xlsx"

OUTPUT_FILE = BASE_DIR / "data" / "transactions_cleaned.csv"


if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found at: {DATA_FILE}"
    )


df = pd.read_excel(
    DATA_FILE,
    sheet_name="Anonymized Original with Catego"
)


# ============================================================
# 2. VALIDATE REQUIRED COLUMNS
# ============================================================

expected_columns = [
    "Transaction Number",
    "Transaction Date",
    "Transaction Type",
    "Transaction Description",
    "Debit Amount",
    "Credit Amount",
    "Balance",
    "Category",
    "Location City",
    "Location Country"
]

missing_columns = set(expected_columns) - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing expected columns: {missing_columns}"
    )

original_count = len(df)


# ============================================================
# 3. CLEAN TRANSACTION DATA
# ============================================================

# Convert transaction dates
df["Transaction Date"] = pd.to_datetime(
    df["Transaction Date"],
    dayfirst=True,
    errors="coerce"
)

# Standardise categories
df["Category"] = df["Category"].fillna("Unclassified")
df["Category"] = df["Category"].str.strip()

# Replace missing debit and credit amounts with zero
df["Debit Amount"] = df["Debit Amount"].fillna(0)
df["Credit Amount"] = df["Credit Amount"].fillna(0)


# ============================================================
# 4. CLASSIFY TRANSACTION DIRECTION
# ============================================================

df["Direction"] = "Unknown"

df.loc[
    df["Debit Amount"] > 0,
    "Direction"
] = "Outgoing"

df.loc[
    df["Credit Amount"] > 0,
    "Direction"
] = "Incoming"


# ============================================================
# 5. VALIDATE TRANSACTION INTEGRITY
# ============================================================

invalid_transactions = df[
    (
        (df["Debit Amount"] > 0) &
        (df["Credit Amount"] > 0)
    )
    |
    (
        (df["Debit Amount"] == 0) &
        (df["Credit Amount"] == 0)
    )
]

assert len(df) == original_count, (
    "Unexpected change in transaction count!"
)

assert len(invalid_transactions) == 0, (
    "Invalid debit/credit transactions detected."
)

assert (df["Direction"] != "Unknown").all(), (
    "Some transactions have an unknown direction."
)

assert df["Transaction Date"].notna().all(), (
    "Some transaction dates could not be converted."
)

print("All transaction integrity checks passed!")


# ============================================================
# 6. CREATE FINANCIAL AMOUNT FIELDS
# ============================================================

# Signed transaction amount
df["Net Amount"] = (
    df["Credit Amount"] - df["Debit Amount"]
)

# Incoming money
df["Income Amount"] = df["Credit Amount"]

# Outgoing money
df["Outgoing Amount"] = df["Debit Amount"]


# ============================================================
# 7. IDENTIFY INTERNAL TRANSFERS
# ============================================================

transfer_mask = df["Transaction Type"] == "TFR"

df["Transfer In"] = 0.0
df["Transfer Out"] = 0.0

df.loc[
    transfer_mask,
    "Transfer In"
] = df.loc[
    transfer_mask,
    "Credit Amount"
]

df.loc[
    transfer_mask,
    "Transfer Out"
] = df.loc[
    transfer_mask,
    "Debit Amount"
]

# Separate transfer movements from other recorded movements
df["Non-Transfer Income"] = (
    df["Income Amount"] - df["Transfer In"]
)

df["Non-Transfer Outgoing"] = (
    df["Outgoing Amount"] - df["Transfer Out"]
)


# ============================================================
# 8. CALCULATE CONSUMPTION SPENDING
# ============================================================

non_consumption_categories = [
    "Savings",
    "Investment",
    "Account transfer"
]

df["Consumption Spending"] = df.apply(
    lambda row: (
        row["Debit Amount"]
        if (
            row["Category"] not in non_consumption_categories
            and row["Transaction Type"] != "TFR"
        )
        else 0
    ),
    axis=1
)


# ============================================================
# 9. CALCULATE FINANCIAL TOTALS
# ============================================================

total_income = df["Income Amount"].sum()

total_outgoing = df["Outgoing Amount"].sum()

total_consumption = df["Consumption Spending"].sum()

total_savings = df.loc[
    df["Category"] == "Savings",
    "Debit Amount"
].sum()

total_investment = df.loc[
    df["Category"] == "Investment",
    "Debit Amount"
].sum()

total_transfer_in = df["Transfer In"].sum()

total_transfer_out = df["Transfer Out"].sum()

non_transfer_income = df["Non-Transfer Income"].sum()

non_transfer_outgoing = df["Non-Transfer Outgoing"].sum()

net_cash_flow = total_income - total_outgoing


# ============================================================
# 10. DISPLAY FINANCIAL SUMMARY
# ============================================================

print("\nSPENDSENSE FINANCIAL SUMMARY")
print("============================")

print(f"Total income: £{total_income:,.2f}")
print(f"Total outgoing: £{total_outgoing:,.2f}")
print(f"Net cash flow: £{net_cash_flow:,.2f}")

print("\nTRANSFER ANALYSIS")
print("-----------------")

print(f"Transfers in: £{total_transfer_in:,.2f}")
print(f"Transfers out: £{total_transfer_out:,.2f}")

print("\nNON-TRANSFER ACTIVITY")
print("---------------------")

print(f"Non-transfer income: £{non_transfer_income:,.2f}")
print(f"Non-transfer outgoing: £{non_transfer_outgoing:,.2f}")

print("\nSPENDING BREAKDOWN")
print("------------------")

print(f"Consumption spending: £{total_consumption:,.2f}")
print(f"Savings: £{total_savings:,.2f}")
print(f"Investment: £{total_investment:,.2f}")


# ============================================================
# 11. CATEGORY-LEVEL FINANCIAL ANALYSIS
# ============================================================

category_summary = (
    df.groupby("Category", as_index=False)
    .agg(
        Transaction_Count=("Transaction Number", "count"),
        Total_Income=("Income Amount", "sum"),
        Total_Outgoing=("Outgoing Amount", "sum"),
        Consumption_Spending=("Consumption Spending", "sum")
    )
    .sort_values(
        by="Total_Outgoing",
        ascending=False
    )
)

print("\nTOP 10 CATEGORIES BY OUTGOING AMOUNT")
print("====================================")

print(
    category_summary.head(10).to_string(index=False)
)


# ============================================================
# 12. MONTHLY FINANCIAL ANALYSIS
# ============================================================

# Create separate savings and investment amount fields

df["Savings Amount"] = df["Debit Amount"].where(
    df["Category"] == "Savings",
    0
)

df["Investment Amount"] = df["Debit Amount"].where(
    df["Category"] == "Investment",
    0
)

# Create a monthly period from transaction dates

df["Month"] = df["Transaction Date"].dt.to_period("M")

# Group transactions by month and calculate financial totals

monthly_summary = (
    df.groupby("Month", as_index=False)
    .agg(
        Transaction_Count=("Transaction Number", "count"),
        Total_Income=("Income Amount", "sum"),
        Total_Outgoing=("Outgoing Amount", "sum"),
        Non_Transfer_Income=("Non-Transfer Income", "sum"),
        Non_Transfer_Outgoing=("Non-Transfer Outgoing", "sum"),
        Consumption_Spending=("Consumption Spending", "sum"),
        Savings=("Savings Amount", "sum"),
        Investment=("Investment Amount", "sum"),
        Transfers_In=("Transfer In", "sum"),
        Transfers_Out=("Transfer Out", "sum")
    )
    .sort_values("Month")
)

# Calculate monthly net cash flow

monthly_summary["Net_Cash_Flow"] = (
    monthly_summary["Total_Income"]
    - monthly_summary["Total_Outgoing"]
)

# Calculate month-on-month consumption change

monthly_summary["Consumption_Change_Percent"] = (
    monthly_summary["Consumption_Spending"]
    .pct_change()
    .mul(100)
    .round(2)
)

# Convert month periods into readable text

monthly_summary["Month"] = (
    monthly_summary["Month"].astype(str)
)

# Display the latest 12 months

print("\nMONTHLY FINANCIAL ANALYSIS")
print("==========================")

print(
    monthly_summary.tail(12).to_string(index=False)
)

# Export monthly financial analysis

MONTHLY_OUTPUT_FILE = (
    BASE_DIR / "data" / "monthly_financial_summary.csv"
)

monthly_summary.to_csv(
    MONTHLY_OUTPUT_FILE,
    index=False
)

print("\nMonthly financial summary exported successfully!")
print(f"Saved to: {MONTHLY_OUTPUT_FILE}")


# ============================================================
# 13. MONTHLY DATA COVERAGE INVESTIGATION
# ============================================================

monthly_coverage = (
    df.groupby("Month", as_index=False)
    .agg(
        Transaction_Count=("Transaction Number", "count"),
        First_Transaction_Date=("Transaction Date", "min"),
        Last_Transaction_Date=("Transaction Date", "max"),
        Days_With_Transactions=("Transaction Date", "nunique")
    )
    .sort_values("Month")
)

# Calculate the number of calendar days in each month

monthly_coverage["Calendar_Days"] = (
    monthly_coverage["Month"].dt.days_in_month
)

# Display the latest 12 months

print("\nMONTHLY DATA COVERAGE INVESTIGATION")
print("==================================")

print(
    monthly_coverage.tail(12).to_string(index=False)
)


# ============================================================
# 14. LARGE TRANSACTION ANOMALY DETECTION
# ============================================================

# Select outgoing transactions with positive debit amounts

outgoing_transactions = df[
    (df["Direction"] == "Outgoing") &
    (df["Debit Amount"] > 0)
].copy()

# Calculate the first and third quartiles

Q1 = outgoing_transactions["Debit Amount"].quantile(0.25)

Q3 = outgoing_transactions["Debit Amount"].quantile(0.75)

# Calculate the interquartile range

IQR = Q3 - Q1

# Calculate the upper anomaly threshold

upper_bound = Q3 + (1.5 * IQR)

# Identify unusually large transactions

anomaly_transactions = outgoing_transactions[
    outgoing_transactions["Debit Amount"] > upper_bound
].copy()

# Sort anomalies from largest to smallest

anomaly_transactions = anomaly_transactions.sort_values(
    by="Debit Amount",
    ascending=False
)

# Display anomaly investigation results

print("\nLARGE TRANSACTION ANOMALY DETECTION")
print("===================================")

print(f"First quartile (Q1): £{Q1:,.2f}")
print(f"Third quartile (Q3): £{Q3:,.2f}")
print(f"Interquartile range: £{IQR:,.2f}")
print(f"Upper anomaly threshold: £{upper_bound:,.2f}")

print(
    f"\nNumber of outgoing transactions: "
    f"{len(outgoing_transactions)}"
)

print(
    f"Number of anomaly candidates: "
    f"{len(anomaly_transactions)}"
)

# Display the 20 largest anomaly candidates

print("\nTOP 20 ANOMALY CANDIDATES")

print(
    anomaly_transactions[
        [
            "Transaction Number",
            "Transaction Date",
            "Transaction Type",
            "Category",
            "Debit Amount"
        ]
    ].head(20).to_string(index=False)
)


# ============================================================
# 15. CATEGORY-AWARE ANOMALY DETECTION
# ============================================================

# Exclude transactions that should not be treated as
# ordinary consumption spending

excluded_categories = [
    "Savings",
    "Investment",
    "Account transfer",
    "Supplementary Income"
]

# Select eligible outgoing transactions

eligible_transactions = df[
    (df["Direction"] == "Outgoing") &
    (df["Debit Amount"] > 0) &
    (~df["Category"].isin(excluded_categories)) &
    (df["Transaction Type"] != "TFR")
].copy()

# Set a minimum number of transactions required
# before calculating a category-specific threshold

minimum_category_transactions = 10

# Calculate the number of outgoing transactions in each category

category_counts = eligible_transactions.groupby(
    "Category"
)["Debit Amount"].transform("count")

# Keep categories with enough observations

eligible_transactions = eligible_transactions[
    category_counts >= minimum_category_transactions
].copy()

# Calculate Q1 and Q3 separately for each category

category_q1 = eligible_transactions.groupby(
    "Category"
)["Debit Amount"].transform(
    lambda values: values.quantile(0.25)
)

category_q3 = eligible_transactions.groupby(
    "Category"
)["Debit Amount"].transform(
    lambda values: values.quantile(0.75)
)

# Calculate category-specific IQR and upper thresholds

eligible_transactions["Category_IQR"] = (
    category_q3 - category_q1
)

eligible_transactions["Category_Upper_Bound"] = (
    category_q3 + (1.5 * eligible_transactions["Category_IQR"])
)

# Flag transactions above their category-specific threshold

category_anomalies = eligible_transactions[
    eligible_transactions["Debit Amount"] >
    eligible_transactions["Category_Upper_Bound"]
].copy()

# Sort candidates from largest to smallest

category_anomalies = category_anomalies.sort_values(
    by="Debit Amount",
    ascending=False
)

# Summarise anomaly candidates by category

anomaly_category_summary = (
    category_anomalies.groupby("Category")
    .agg(
        Anomaly_Count=("Debit Amount", "count"),
        Total_Anomaly_Amount=("Debit Amount", "sum")
    )
    .sort_values(
        by="Anomaly_Count",
        ascending=False
    )
)

# Display results

print("\nCATEGORY-AWARE ANOMALY DETECTION")
print("================================")

print(
    f"Eligible outgoing transactions: "
    f"{len(eligible_transactions)}"
)

print(
    f"Categories excluded for insufficient data: "
    f"{df.loc[
        (df['Direction'] == 'Outgoing') &
        (df['Debit Amount'] > 0) &
        (~df['Category'].isin(excluded_categories)) &
        (df['Transaction Type'] != 'TFR'),
        'Category'
    ].nunique() - eligible_transactions['Category'].nunique()}"
)

print(
    f"Category anomaly candidates: "
    f"{len(category_anomalies)}"
)

print("\nANOMALY CANDIDATES BY CATEGORY")

if anomaly_category_summary.empty:
    print("No category-level anomaly candidates identified.")
else:
    print(anomaly_category_summary.to_string())

print("\nTOP 20 CATEGORY ANOMALY CANDIDATES")

if category_anomalies.empty:
    print("No anomaly candidates to display.")
else:
    print(
        category_anomalies[
            [
                "Transaction Number",
                "Transaction Date",
                "Category",
                "Debit Amount",
                "Category_Upper_Bound"
            ]
        ].head(20).to_string(index=False)
    )


    print(
        category_anomalies[
            [
                "Transaction Number",
                "Transaction Date",
                "Category",
                "Debit Amount",
                "Category_Upper_Bound"
            ]
        ].head(20).to_string(index=False)
    )

# Export category-aware anomaly results

anomaly_file = (
    BASE_DIR / "data" / "category_anomalies.csv"
)

category_anomalies[
    [
        "Transaction Number",
        "Transaction Date",
        "Category",
        "Debit Amount",
        "Category_Upper_Bound"
    ]
].to_csv(anomaly_file, index=False)

print(f"\nAnomaly results exported to: {anomaly_file}")


# ============================================================
# 12. INVESTIGATE ACCOUNT TRANSFERS
# ============================================================

account_transfer = df[
    df["Category"] == "Account transfer"
]

print("\nACCOUNT TRANSFER INVESTIGATION")
print("==============================")

print(
    account_transfer[
        [
            "Transaction Number",
            "Transaction Date",
            "Transaction Type",
            "Debit Amount",
            "Credit Amount",
            "Balance",
            "Category"
        ]
    ].to_string(index=False)
)


# ============================================================
# 13. INVESTIGATE ALL TFR TRANSACTIONS
# ============================================================

transfer_transactions = df[transfer_mask]

print("\nTRANSFER TRANSACTION INVESTIGATION")
print("==================================")

print(
    f"Number of transfer transactions: "
    f"{len(transfer_transactions)}"
)

transfers_by_category = (
    transfer_transactions.groupby("Category")
    .agg(
        Transaction_Count=("Transaction Number", "count"),
        Total_Debit=("Debit Amount", "sum"),
        Total_Credit=("Credit Amount", "sum")
    )
    .sort_values(
        by="Total_Debit",
        ascending=False
    )
)

print("\nTransfers by category:")
print(transfers_by_category.to_string())

print(
    f"\nTotal transferred out: "
    f"£{total_transfer_out:,.2f}"
)

print(
    f"Total transferred in: "
    f"£{total_transfer_in:,.2f}"
)


# ============================================================
# 16. ANOMALY PATTERN INVESTIGATION
# ============================================================

# Calculate how many times each transaction exceeds
# its category-specific upper threshold

category_anomalies["Threshold_Multiple"] = (
    category_anomalies["Debit Amount"] /
    category_anomalies["Category_Upper_Bound"]
)

# ------------------------------------------------------------
# 1. Rank anomaly candidates by threshold multiple
# ------------------------------------------------------------

print("\nANOMALIES RELATIVE TO CATEGORY THRESHOLDS")
print("=========================================")

print(
    category_anomalies[
        [
            "Transaction Number",
            "Transaction Date",
            "Category",
            "Debit Amount",
            "Category_Upper_Bound",
            "Threshold_Multiple"
        ]
    ].sort_values(
        by="Threshold_Multiple",
        ascending=False
    ).head(20).to_string(index=False)
)

# ------------------------------------------------------------
# 2. Summarise flagged amounts by category
# ------------------------------------------------------------

print("\nCATEGORY ANOMALY IMPACT")
print("=======================")

category_impact = (
    category_anomalies.groupby("Category")
    .agg(
        Candidate_Count=("Debit Amount", "count"),
        Total_Flagged_Amount=("Debit Amount", "sum"),
        Average_Flagged_Amount=("Debit Amount", "mean"),
        Largest_Flagged_Amount=("Debit Amount", "max")
    )
    .sort_values(
        by="Total_Flagged_Amount",
        ascending=False
    )
)

print(category_impact.to_string())


# ============================================================
# 17. RECURRING TRANSACTION DETECTION
# ============================================================

# Exclude categories that do not represent ordinary
# recurring consumption payments

recurring_excluded_categories = [
    "Savings",
    "Investment",
    "Account transfer",
    "Supplementary Income"
]

# Select eligible outgoing transactions

recurring_eligible = df[
    (df["Direction"] == "Outgoing") &
    (df["Debit Amount"] > 0) &
    (~df["Category"].isin(recurring_excluded_categories)) &
    (df["Transaction Type"] != "TFR")
].copy()

# Round amounts to two decimal places to group
# transactions with the same monetary value

recurring_eligible["Rounded_Amount"] = (
    recurring_eligible["Debit Amount"].round(2)
)

# Sort transactions by date

recurring_eligible = recurring_eligible.sort_values(
    by="Transaction Date"
)

# Store the recurring transaction findings

recurring_results = []

# Group transactions by category and amount

for (category, amount), group in recurring_eligible.groupby(
    ["Category", "Rounded_Amount"]
):

    # Require at least three occurrences before
    # investigating a possible recurring pattern

    if len(group) < 3:
        continue

    # Sort the dates for this transaction group

    dates = group["Transaction Date"].sort_values()

    # Calculate the number of days between transactions

    gaps = dates.diff().dt.days.dropna()

    # Calculate the median and standard deviation of gaps

    median_gap = gaps.median()
    gap_std = gaps.std()

    # Identify a possible payment frequency

    if 25 <= median_gap <= 35 and gap_std <= 7:
        pattern = "Potential monthly pattern"

    elif 12 <= median_gap <= 16 and gap_std <= 5:
        pattern = "Potential fortnightly pattern"

    elif 5 <= median_gap <= 9 and gap_std <= 3:
        pattern = "Potential weekly pattern"

    elif 80 <= median_gap <= 100 and gap_std <= 14:
        pattern = "Potential quarterly pattern"

    else:
        pattern = "Repeated amount - irregular timing"

    # Save the findings

    recurring_results.append({
        "Category": category,
        "Amount": amount,
        "Occurrences": len(group),
        "First_Date": dates.min(),
        "Last_Date": dates.max(),
        "Median_Gap_Days": median_gap,
        "Gap_Std_Dev": gap_std,
        "Pattern_Indication": pattern
    })

# Convert the findings into a DataFrame

recurring_summary = pd.DataFrame(recurring_results)

# Display recurring transaction investigation

print("\nRECURRING TRANSACTION INVESTIGATION")
print("===================================")

print(
    f"Eligible outgoing transactions: "
    f"{len(recurring_eligible)}"
)

print(
    f"Repeated amount patterns identified: "
    f"{len(recurring_summary)}"
)

if recurring_summary.empty:

    print("No repeated transaction amounts identified.")

else:

    # Sort by number of occurrences

    recurring_summary = recurring_summary.sort_values(
        by="Occurrences",
        ascending=False
    )

    print("\nTOP 25 REPEATED TRANSACTION PATTERNS")

    print(
        recurring_summary.head(25).to_string(index=False)
    )

# ------------------------------------------------------------
# Investigate the repeated £981.71 Bills payment
# ------------------------------------------------------------

print("\nINVESTIGATION: BILLS PAYMENT OF £981.71")
print("=======================================")

target_payment = recurring_eligible[
    (recurring_eligible["Category"] == "Bills") &
    (recurring_eligible["Rounded_Amount"] == 981.71)
].sort_values(
    by="Transaction Date"
)

if target_payment.empty:

    print("No matching Bills transactions found.")

else:

    target_dates = target_payment["Transaction Date"]

    target_gaps = target_dates.diff().dt.days.dropna()

    print(f"Number of matching payments: {len(target_payment)}")

    print("\nPayment dates:")

    print(
        target_payment[
            ["Transaction Number", "Transaction Date", "Debit Amount"]
        ].to_string(index=False)
    )

    if not target_gaps.empty:

        print(
            f"\nMedian gap between payments: "
            f"{target_gaps.median():.1f} days"
        )

        print(
            f"Average gap between payments: "
            f"{target_gaps.mean():.1f} days"
        )

        print(
            f"Standard deviation of gaps: "
            f"{target_gaps.std():.1f} days"
        )


# ============================================================
# 18. RECURRING PAYMENT VALIDATION AND EXPORT
# ============================================================

print("\nRECURRING PAYMENT VALIDATION")
print("============================")

if recurring_summary.empty:

    print("No recurring payment patterns available for validation.")

else:

    # Count patterns by their detected timing indication

    pattern_counts = (
        recurring_summary["Pattern_Indication"]
        .value_counts()
    )

    print("\nPATTERN CLASSIFICATION SUMMARY")

    print(pattern_counts.to_string())

    # Select patterns with consistent payment intervals

    potential_recurring = recurring_summary[
        recurring_summary["Pattern_Indication"].isin([
            "Potential monthly pattern",
            "Potential fortnightly pattern",
            "Potential weekly pattern",
            "Potential quarterly pattern"
        ])
    ].copy()

    print(
        f"\nPotential recurring payment patterns: "
        f"{len(potential_recurring)}"
    )

    print("\nPOTENTIAL RECURRING PAYMENTS")

    if potential_recurring.empty:

        print("No consistent recurring payment patterns identified.")

    else:

        print(
            potential_recurring.sort_values(
                by="Occurrences",
                ascending=False
            ).to_string(index=False)
        )

    # Export all repeated amount patterns

    recurring_summary.to_csv(
        BASE_DIR / "data" / "recurring_transaction_analysis.csv",
        index=False
    )

    # Export only potentially recurring patterns

    potential_recurring.to_csv(
        BASE_DIR / "data" / "potential_recurring_payments.csv",
        index=False
    )



    print("\nRECURRING ANALYSIS EXPORT")
    print("=========================")

    print("All repeated patterns exported successfully.")

    print("Potential recurring payments exported successfully.")


# ------------------------------------------------------------
# 3. Investigate repeated flagged transaction amounts
# ------------------------------------------------------------

print("\nREPEATED ANOMALY AMOUNTS")
print("========================")

repeated_amounts = (
    category_anomalies
    .assign(
        Rounded_Amount=lambda data: data["Debit Amount"].round(2)
    )
    .groupby(["Category", "Rounded_Amount"])
    .agg(
        Occurrences=("Transaction Number", "count"),
        First_Date=("Transaction Date", "min"),
        Last_Date=("Transaction Date", "max")
    )
    .reset_index()
)

repeated_amounts = repeated_amounts[
    repeated_amounts["Occurrences"] >= 2
].sort_values(
    by="Occurrences",
    ascending=False
)

if repeated_amounts.empty:
    print("No repeated flagged amounts identified.")
else:
    print(repeated_amounts.head(20).to_string(index=False))


# ============================================================
# 14. EXPORT CLEANED DATASET
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nDATASET EXPORT")
print("==============")

print(f"Cleaned dataset saved to: {OUTPUT_FILE}")
print(f"Final dataset shape: {df.shape}")

print("\nSpendSense data preparation completed successfully!")
