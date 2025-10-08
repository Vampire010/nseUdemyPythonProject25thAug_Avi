import pandas as pd

def dat_to_excel(dat_file, excel_file):
    """
    Convert NSE .DAT file into Excel .xlsx with proper columns.
    
    Args:
        dat_file (str): Path to input .DAT file
        excel_file (str): Path to output .xlsx file
    """
    # Read the data (skip first 3 metadata rows)
    df = pd.read_csv(dat_file, skiprows=3)
    
    # Save to Excel
    df.to_excel(excel_file, index=False)
    print(f"✅ Converted: {dat_file} → {excel_file}")

if __name__ == "__main__":
    dat_file = "MTO_12092025.DAT"   # Input DAT file
    excel_file = "MTO_12092025.xlsx"  # Output Excel file
    
    dat_to_excel(dat_file, excel_file)
