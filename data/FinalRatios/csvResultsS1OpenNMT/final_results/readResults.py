import pandas as pd
import glob
import os

def print_each_csv_summary():
    # Collect all CSV files in root
    csv_files = glob.glob("*.csv")
    if not csv_files:
        print("❌ No CSV files found in root dir.")
        return

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            print(f"\n📂 {os.path.basename(file)}")
            print(df.to_string(index=False))  # print the table
        except Exception as e:
            print(f"⚠️ Skipping {file}, error: {e}")


# -----------------------
# Run script
# -----------------------
if __name__ == "__main__":
    print_each_csv_summary()

