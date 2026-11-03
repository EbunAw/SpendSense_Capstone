import pandas as pd
from pathlib import Path


# Get the main project directory
BASE_DIR = Path(__file__).resolve().parent

# Locate the Excel dataset
DATA_FILE = BASE_DIR / "data" / "laramee26openBankTransactionData.xlsx"


# Check whether the dataset exists
if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")


# Display available Excel sheets
excel_file = pd.ExcelFile(DATA_FILE)

print("\nAVAILABLE SHEETS:")
print(excel_file.sheet_names)


# Read the first sheet
df = pd.read_excel(DATA_FILE, sheet_name=0)


# Display dataset information
print("\nDATASET SHAPE:")
print(df.shape)

print("\nCOLUMN NAMES:")
print(df.columns.tolist())

print("\nFIRST 10 TRANSACTIONS:")
print(df.head(10))

print("\nDATA TYPES:")
print(df.dtypes)

print("\nMISSING VALUES:")
print(df.isnull().sum())

print("\nDATASET INFORMATION:")
df.info()

# -------------------------------------------------
# Further dataset investigation
# -------------------------------------------------

# Inspect the second Excel sheet
categories_df = pd.read_excel(
    DATA_FILE,
    sheet_name="Description of Categories"
)

print("\nCATEGORY DESCRIPTION SHEET:")
print(categories_df.head(20))

print("\nCATEGORY SHEET COLUMNS:")
print(categories_df.columns.tolist())


# Check transaction types
print("\nTRANSACTION TYPE DISTRIBUTION:")
print(df["Transaction Type"].value_counts(dropna=False))


# Check available categories
print("\nCATEGORY DISTRIBUTION:")
print(df["Category"].value_counts(dropna=False))


# Convert transaction dates
df["Transaction Date"] = pd.to_datetime(
    df["Transaction Date"],
    dayfirst=True,
    errors="coerce"
)

print("\nDATE RANGE:")
print("Earliest:", df["Transaction Date"].min())
print("Latest:", df["Transaction Date"].max())


# Check duplicate transaction numbers
print("\nDUPLICATE TRANSACTION NUMBERS:")
print(df["Transaction Number"].duplicated().sum())


# Check debit and credit combinations
print("\nDEBIT AND CREDIT CHECKS:")

print(
    "Both amounts missing:",
    (df["Debit Amount"].isna() & df["Credit Amount"].isna()).sum()
)

print(
    "Both amounts populated:",
    (df["Debit Amount"].notna() & df["Credit Amount"].notna()).sum()
)

print(
    "Debit only:",
    (df["Debit Amount"].notna() & df["Credit Amount"].isna()).sum()
)

print(
    "Credit only:",
    (df["Debit Amount"].isna() & df["Credit Amount"].notna()).sum()
)

# -------------------------------------------------
# Investigating category names and transaction codes
# -------------------------------------------------

# Read the category sheet without assuming its first row is a header
categories_df = pd.read_excel(
    DATA_FILE,
    sheet_name="Description of Categories",
    header=None
)

print("\nCOMPLETE CATEGORY DESCRIPTIONS:")
print(categories_df.to_string(index=False, header=False))


# Investigate possible category inconsistencies
print("\nCATEGORY NAMES WITH EXACT SPACING:")
print(
    df["Category"]
    .dropna()
    .map(repr)
    .value_counts()
    .to_string()
)


# Inspect transaction descriptions
print("\nMOST COMMON TRANSACTION DESCRIPTIONS:")
print(df["Transaction Description"].value_counts().head(20))


# Inspect examples of each transaction type
print("\nTRANSACTION TYPE EXAMPLES:")
print(
    df.groupby("Transaction Type", dropna=False)
    ["Transaction Description"]
    .apply(lambda values: values.head(3).tolist())
    .to_string()
)


# Inspect transaction amount ranges
print("\nDEBIT AMOUNT SUMMARY:")
print(df["Debit Amount"].describe())

print("\nCREDIT AMOUNT SUMMARY:")
print(df["Credit Amount"].describe())

# -------------------------------------------------
# Investigating financial direction by category
# -------------------------------------------------

print("\nCATEGORY BY TRANSACTION DIRECTION:")

df["Transaction Direction"] = "Unknown"

df.loc[df["Debit Amount"].notna(), "Transaction Direction"] = "Outgoing"

df.loc[df["Credit Amount"].notna(), "Transaction Direction"] = "Incoming"

category_direction = pd.crosstab(
    df["Category"],
    df["Transaction Direction"],
    margins=True
)

print(category_direction)


# Inspect missing transaction types
print("\nTRANSACTIONS WITH MISSING TYPES:")

print(
    df[df["Transaction Type"].isna()][
        [
            "Transaction Number",
            "Transaction Description",
            "Debit Amount",
            "Credit Amount",
            "Category"
        ]
    ].head(15).to_string(index=False)
)


# Inspect missing categories
print("\nTRANSACTIONS WITH MISSING CATEGORIES:")

print(
    df[df["Category"].isna()][
        [
            "Transaction Number",
            "Transaction Description",
            "Debit Amount",
            "Credit Amount",
            "Transaction Type"
        ]
    ].head(15).to_string(index=False)
)

# -------------------------------------------------
# Final checks before data cleaning
# -------------------------------------------------

# Include missing categories in the direction analysis
print("\nCATEGORY DIRECTION INCLUDING MISSING CATEGORIES:")

category_direction_complete = pd.crosstab(
    df["Category"].fillna("Unclassified"),
    df["Transaction Direction"]
)

print(category_direction_complete)

print("\nTOTAL TRANSACTIONS BY DIRECTION:")
print(df["Transaction Direction"].value_counts())


# Inspect all transactions with missing types
print("\nALL TRANSACTIONS WITH MISSING TYPES:")

missing_types = df[df["Transaction Type"].isna()]

print(
    missing_types[
        [
            "Transaction Number",
            "Transaction Description",
            "Debit Amount",
            "Credit Amount",
            "Category"
        ]
    ].to_string(index=False)
)


# Inspect all transactions with missing categories
print("\nALL TRANSACTIONS WITH MISSING CATEGORIES:")

missing_categories = df[df["Category"].isna()]

print(
    missing_categories[
        [
            "Transaction Number",
            "Transaction Description",
            "Transaction Type",
            "Debit Amount",
            "Credit Amount"
        ]
    ].to_string(index=False)
)