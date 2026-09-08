
import pandas as pd
from pathlib import Path
import shutil
from sqlalchemy import create_engine , text
from dotenv import load_dotenv
import os


load_dotenv()

# =============================================
# SQL connection


SERVER = os.getenv("SERVER")

DATABASE = os.getenv("DATABASE")

DRIVER = os.getenv("DRIVER")

CONNECTION_STRING = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    f"?driver={DRIVER.replace(' ', '+')}"
)

engine = create_engine(
    CONNECTION_STRING,
    fast_executemany=True
)

# ================================================
# project file path


BASE_FOLDER = Path(__file__).parent


RECEIVED_FOLDER = BASE_FOLDER / "1-Received"

PROCESSED_FOLDER = BASE_FOLDER / "2-Processed"

REJECTED_FOLDER = BASE_FOLDER / "Rejected"

# requiered cols in csv
REQUIRED_COLUMNS = [
    "Client_ID",
    "User_ID",
    "Audit_Date",
    "Audit_Status",
    "Score",
    "Comments"
]

# creat a validiation def to make sure about reports quality
def validate_data(df):

    errors = []

    # 1. Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")

    else:
        # 2. Check missing values
        if df[REQUIRED_COLUMNS].isnull().any().any():
            errors.append("Missing values found")

        # 3. Check Score
            
        if not pd.api.types.is_numeric_dtype(df["Score"]):

            errors.append("Score must be a Number")
        else:

        # 4. Check Score range
            if not df["Score"].dropna().between(0, 100).all():
                errors.append("Score must be between 0 and 100")

        # 5. Check Audit Date
        if pd.to_datetime(df["Audit_Date"], errors="coerce").isnull().any():
            errors.append("Invalid Audit_Date")

        # 6. Check duplicates
        if df.duplicated().any():
            errors.append("Duplicate records found")

    # Final result
    if errors:
        return False, errors

    return True, errors 

# get all csv files from received folder
csv_files = list(
    RECEIVED_FOLDER.glob("*.csv"))

print(f"Found {len(csv_files)} CSV file(s).")


# ============================================================
# Validate each file


# check all csv files
for file in csv_files:

    print("\n" + "=" * 60)

    # show the file name
    print(f"File: {file.name}")

    df = pd.read_csv(file)

    # use the validation def
    is_valid, errors = validate_data(df)

    # --------------------------------------------------------
    # Validation result
    # --------------------------------------------------------

    if is_valid:

        print("✅ Validation Passed")
        
            # add the file name cols 
        df["File_Name"] = file.name

    # add actual time for file upload to sql
        df["Load_Date"] = pd.Timestamp.now()


            # check the file is uploaded before or not
        query = text(""" SELECT COUNT(*)
            FROM stg.Audited_Data_Raw
            WHERE File_Name = :file_name """)

        with engine.connect() as connection:
            result = connection.execute(
                query,
                {"file_name": file.name})

            existing_rows = result.scalar()
            
          # is there a duplicated rows or not
            if existing_rows == 0:

            # load to SQL
                df.to_sql(
                "Audited_Data_Raw",
                con=engine,
                schema="stg",
                if_exists="append",
                index=False
                )

                print("✅ Data loaded successfully into SQL.")
                shutil.move(
                str(file),
                str(PROCESSED_FOLDER / file.name))
                print("File moved to 2-Processed.")

            else:

                print("⚠️ File already processed Before, Data was NOT loaded again.")
              

    else:

        print("❌ Validation Failed")

        print("\nErrors:")

        # show all errors
        for error in errors:
            print(f"- {error}")
        
        error_log = pd.DataFrame({
        "File_Name": [file.name] * len(errors),
        "Error": errors })
        
        # create log csv file with error for each report
        ERROR_LOG_FILE = REJECTED_FOLDER / f"{file.stem}_validation_errors.csv"
        
        error_log.to_csv(
        ERROR_LOG_FILE,
        mode="a",
        header=not ERROR_LOG_FILE.exists(),
        index=False)
        
        shutil.move(
                str(file),
                str(REJECTED_FOLDER / file.name))
        

        print("\nFile will NOT be loaded into SQL.")
        print("File moved to Rejected.")
        
        
     