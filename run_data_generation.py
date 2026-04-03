import pandas as pd
import sqlite3
import argparse
import os
import shutil
from datetime import datetime
from synthetic_data.generate_user_profiles import generate_user_profile, save_profiles_to_sqlite
from synthetic_data.generate_programs import generate_programs_of_study, save_programs_to_sqlite
from synthetic_data.generate_payments import generate_education_loan_payments, save_payments_to_sqlite
from synthetic_data.generate_loans import generate_loan_info, save_loans_to_sqlite

def purge_existing_tables(db_path):
    """
    Purge all existing tables before generating new data.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop tables if they exist
    cursor.execute('DROP TABLE IF EXISTS loan_payments')
    cursor.execute('DROP TABLE IF EXISTS loan_info')
    cursor.execute('DROP TABLE IF EXISTS user_profile')
    
    conn.commit()
    conn.close()
    print("Existing tables purged successfully.")

def generate_complete_dataset(num_payers, start_date_str, end_date_str, db_path, validate=False):
    """
    Orchestrates the generation of the complete synthetic dataset.
    """
    print(f"Generating complete synthetic dataset for {num_payers} payers...")
    print(f"Payment period: {start_date_str} to {end_date_str}")
    
    # Step 1: Purge existing tables
    purge_existing_tables(db_path)
    
    # Step 2: Generate user profiles
    print("\n[1/3] Generating user profiles...")
    df_profiles = generate_user_profile(num_payers)
    save_profiles_to_sqlite(df_profiles, db_path)
    print(f"✓ {len(df_profiles)} user profiles created")
    
    # Step 2: Generate programs of study
    print("\n[2/5] Generating programs of study...")
    df_programs = generate_programs_of_study()
    save_programs_to_sqlite(df_programs, db_path)  
    print(f"✓ {len(df_programs)} program records created")
    
    # Step 3: Generate loan records
    print("\n[3/5] Generating loan records...")
    df_loans = generate_loan_info(num_payers)
    save_loans_to_sqlite(df_loans, db_path)
    print(f"✓ {len(df_loans)} loan records created")
    
    # Step 4: Generate education loan payments
    print("\n[4/5] Generating education loan payments...")
    df_payments = generate_education_loan_payments(num_payers, start_date_str, end_date_str, db_path)
    save_payments_to_sqlite(df_payments, db_path)
    print(f"✓ {len(df_payments)} payment records created")
    
    return df_profiles, df_programs, df_loans, df_payments

def display_summary_statistics(db_path):
    """
    Display comprehensive statistics about the generated dataset.
    """
    conn = sqlite3.connect(db_path)
    
    print("\n" + "="*60)
    print("DATASET SUMMARY STATISTICS")
    print("="*60)
    
    # User profiles statistics
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM user_profile')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT employment_status, COUNT(*) FROM user_profile GROUP BY employment_status')
    employment_stats = cursor.fetchall()
    
    cursor.execute('SELECT province, COUNT(*) FROM user_profile GROUP BY province ORDER BY COUNT(*) DESC')
    province_stats = cursor.fetchall()
    
    # Loan statistics
    cursor.execute('SELECT COUNT(*) FROM loan_info')
    total_loans = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(loan_amount) FROM loan_info')
    total_loan_value = cursor.fetchone()[0]
    
    cursor.execute('SELECT loan_status, COUNT(*) FROM loan_info GROUP BY loan_status')
    loan_status_stats = cursor.fetchall()
    
    cursor.execute('SELECT AVG(interest_rate) FROM loan_info')
    avg_interest_rate = cursor.fetchone()[0]
    
    # Payment statistics
    cursor.execute('SELECT COUNT(*) FROM loan_payments')
    total_payments = cursor.fetchone()[0]
    
    cursor.execute("SELECT status, COUNT(*) FROM loan_payments GROUP BY status")
    payment_status_stats = cursor.fetchall() 
    
    cursor.execute("SELECT COUNT(DISTINCT payer_id) FROM loan_payments WHERE status = 'Missed'")
    delinquent_users = cursor.fetchone()[0]
    
    print(f"Total Users: {total_users}")
    print(f"Total Loans: {total_loans}")
    print(f"Total Loan Portfolio Value: ${total_loan_value:,.2f}")
    print(f"Average Interest Rate: {avg_interest_rate:.3f}%")
    print(f"Total Payment Records: {total_payments}")
    print(f"Delinquent Users: {delinquent_users} ({delinquent_users/total_users*100:.1f}%)")
    
    print(f"\nEmployment Distribution:")
    for status, count in employment_stats:
        percentage = (count / total_users) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    print(f"\nLoan Status Distribution:")
    for status, count in loan_status_stats:
        percentage = (count / total_loans) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    print(f"\nPayment Status Distribution:")
    for status, count in payment_status_stats:
        percentage = (count / total_payments) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
        
    print(f"\nTop Provinces by User Count:")
    for province, count in province_stats:
        percentage = (count / total_users) * 100
        print(f"  {province}: {count} ({percentage:.1f}%)")
    
    conn.close()

def export_to_csv(df_profiles, df_programs, df_loans, df_payments):
    """
    Export all generated data tables to CSV files in an organized database_exports folder.
    """
    # Create database_exports directory if it doesn't exist
    exports_dir = "database_exports"
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
    else:
        # Clear existing files in database_exports directory
        for filename in os.listdir(exports_dir):
            file_path = os.path.join(exports_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        print(f"📁 Cleared existing files in '{exports_dir}' folder")
    
    # Generate timestamp for unique file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define CSV file paths
    csv_files = {
        "user_profile": os.path.join(exports_dir, f"user_profile_{timestamp}.csv"),
        "program_of_study": os.path.join(exports_dir, f"program_of_study_{timestamp}.csv"),
        "loan_info": os.path.join(exports_dir, f"loan_info_{timestamp}.csv"),
        "loan_payments": os.path.join(exports_dir, f"loan_payments_{timestamp}.csv")
    }
    
    # Export each DataFrame to CSV
    try:
        print(f"\n📄 Exporting data to CSV files in '{exports_dir}' folder...")
        
        df_profiles.to_csv(csv_files["user_profile"], index=False)
        print(f"  ✓ User profile exported: {csv_files['user_profile']}")
        
        df_programs.to_csv(csv_files["program_of_study"], index=False)
        print(f"  ✓ Programs of study exported: {csv_files['program_of_study']}")
        
        df_loans.to_csv(csv_files["loan_info"], index=False)
        print(f"  ✓ Loan info exported: {csv_files['loan_info']}")
        
        df_payments.to_csv(csv_files["loan_payments"], index=False)
        print(f"  ✓ Loan payments exported: {csv_files['loan_payments']}")
        
        # Summary
        total_files = len(csv_files)
        total_records = len(df_profiles) + len(df_programs) + len(df_loans) + len(df_payments)
        print(f"\n📊 Export Summary:")
        print(f"  Total files exported: {total_files}")
        print(f"  Total records exported: {total_records:,}")
        print(f"  Export location: {os.path.abspath(exports_dir)}")
        
    except Exception as e:
        print(f"❌ Error exporting CSV files: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate complete synthetic student loan and user profile dataset.")
    parser.add_argument("--num_payers", type=int, default=1000, help="Number of distinct student loan payers.")
    parser.add_argument("--start_date", type=str, default="2020-01-01", help="Start date for payments (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date for payments (YYYY-MM-DD)")
    parser.add_argument("--db_path", type=str, default="student_loan_data.db", help="SQLite database path")
    parser.add_argument("--export_csv", action="store_true", help="Export data to CSV files")
        
    args = parser.parse_args()
    
    try:
        # Generate complete dataset
        df_profiles, df_programs, df_loans, df_payments = generate_complete_dataset(
            args.num_payers, 
            args.start_date, 
            args.end_date, 
            args.db_path,
        )
        
        # Export to CSV if requested
        if args.export_csv:
            export_to_csv(df_profiles, df_programs, df_loans, df_payments)
        
        # Display summary statistics
        display_summary_statistics(args.db_path)
        
        print(f"\n✓ Complete dataset successfully generated in: {args.db_path}")
        
    except Exception as e:
        print(f"Error generating dataset: {str(e)}")
        raise
