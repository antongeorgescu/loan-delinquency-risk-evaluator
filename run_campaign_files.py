#!/usr/bin/env python3
"""
Campaign Files Generator
========================

This script generates targeted marketing campaign files by extracting borrowers
based on their ML-calculated delinquency risk levels.

Usage:
    python run_campaign_files.py [--db_path path_to_database]
    
Example:
    python run_campaign_files.py --db_path student_loan_data.db
    
Outputs:
    - campaigns/high_risk_users.csv (Risk level 2)
    - campaigns/medium_risk_users.csv (Risk level 1)
"""

import pandas as pd
import sqlite3
import os
import argparse
from datetime import datetime

def create_campaigns_folder():
    """
    Create campaigns folder if it doesn't exist.
    """
    campaigns_dir = "campaigns"
    if not os.path.exists(campaigns_dir):
        os.makedirs(campaigns_dir)
        print(f"✓ Created '{campaigns_dir}' folder")
    else:
        print(f"✓ Using existing '{campaigns_dir}' folder")
    return campaigns_dir

def extract_campaign_data(db_path, risk_level, risk_label):
    """
    Extract campaign data for a specific risk level.
    
    Args:
        db_path: Path to SQLite database
        risk_level: Integer risk level (1 or 2)
        risk_label: String label for the risk level
    
    Returns:
        DataFrame with campaign data
    """
    conn = sqlite3.connect(db_path)
    
    # Comprehensive query joining all relevant tables
    query = """
    SELECT 
        -- User Profile Information
        up.payer_id,
        up.age,
        up.annual_income_cad,
        up.employment_status,
        up.marital_status,
        up.city,
        up.province,
        
        -- Loan Information
        li.loan_amount,
        li.interest_rate,
        li.loan_term_years,
        li.loan_term_months,
        li.current_balance,
        li.loan_status,
        li.monthly_payment,
        li.origination_date,
        li.maturity_date,
        li.delinquency_risk,
        li.lender,
        li.institution_name,
        li.institution_city,
        li.institution_province,
        
        -- Program of Study Information
        pos.program_name,
        pos.program_type,
        pos.field_of_study,
        pos.program_difficulty,
        pos.duration_years as program_duration_years,
        pos.typical_tuition_cad,
        pos.employment_rate_percent,
        pos.avg_starting_salary_cad,
        pos.university_name,
        pos.institution_type,
        pos.requires_licensing,
        pos.job_market_outlook,
        
        -- Calculated Fields for Campaign Use
        CASE 
            WHEN up.annual_income_cad < 40000 THEN 'Low Income'
            WHEN up.annual_income_cad < 70000 THEN 'Medium Income'
            ELSE 'High Income'
        END as income_category,
        
        CASE 
            WHEN up.age < 25 THEN 'Young Adult (18-24)'
            WHEN up.age < 35 THEN 'Young Professional (25-34)'
            WHEN up.age < 50 THEN 'Mid-Career (35-49)'
            ELSE 'Senior (50+)'
        END as age_group,
        
        CASE 
            WHEN pos.program_difficulty = 1 THEN 'Low Difficulty'
            WHEN pos.program_difficulty = 2 THEN 'Medium Difficulty'
            ELSE 'High Difficulty'
        END as program_difficulty_label,
        
        ROUND((li.current_balance / li.loan_amount) * 100, 2) as remaining_balance_pct,
        ROUND((li.monthly_payment * 12 / up.annual_income_cad) * 100, 2) as payment_to_income_ratio_pct,
        
        -- Contact Strategy Flags
        CASE 
            WHEN li.delinquency_risk = 2 THEN 'Immediate Intervention'
            WHEN li.delinquency_risk = 1 THEN 'Proactive Monitoring'
            ELSE 'Standard Communication'
        END as recommended_approach,
        
        CASE 
            WHEN pos.employment_rate_percent < 70 THEN 'Career Support Needed'
            WHEN pos.employment_rate_percent < 85 THEN 'Moderate Job Market'
            ELSE 'Strong Job Market'
        END as career_outlook_flag
        
    FROM user_profile up
    JOIN loan_info li ON up.payer_id = li.payer_id
    JOIN program_of_study pos ON li.program_id = pos.program_id
    WHERE li.delinquency_risk = ?
    ORDER BY up.payer_id
    """
    
    df = pd.read_sql_query(query, conn, params=[risk_level])
    conn.close()
    
    print(f"✓ Extracted {len(df):,} {risk_label} borrowers")
    
    return df

def generate_campaign_summary(df, risk_label):
    """
    Generate summary statistics for campaign data.
    """
    if len(df) == 0:
        print(f"⚠️  No {risk_label} borrowers found")
        return
    
    print(f"\n📊 {risk_label.upper()} BORROWERS CAMPAIGN SUMMARY:")
    print(f"   Total Borrowers: {len(df):,}")
    print(f"   Average Age: {df['age'].mean():.1f} years")
    print(f"   Average Income: ${df['annual_income_cad'].mean():,.0f}")
    print(f"   Average Loan Amount: ${df['loan_amount'].mean():,.0f}")
    print(f"   Average Monthly Payment: ${df['monthly_payment'].mean():.0f}")
    
    # Geographic distribution
    print(f"\n📍 Geographic Distribution:")
    province_dist = df['province'].value_counts().head(5)
    for province, count in province_dist.items():
        pct = (count / len(df)) * 100
        print(f"   {province}: {count:,} ({pct:.1f}%)")
    
    # Program difficulty distribution
    print(f"\n🎓 Program Difficulty Distribution:")
    difficulty_dist = df['program_difficulty_label'].value_counts()
    for difficulty, count in difficulty_dist.items():
        pct = (count / len(df)) * 100
        print(f"   {difficulty}: {count:,} ({pct:.1f}%)")
    
    # Income categories
    print(f"\n💰 Income Categories:")
    income_dist = df['income_category'].value_counts()
    for category, count in income_dist.items():
        pct = (count / len(df)) * 100
        print(f"   {category}: {count:,} ({pct:.1f}%)")

def save_campaign_file(df, campaigns_dir, filename, risk_label):
    """
    Save campaign data to CSV file.
    """
    if len(df) == 0:
        print(f"⚠️  Skipping {filename} - no data to export")
        return
    
    filepath = os.path.join(campaigns_dir, filename)
    
    # Sort by recommended priority (higher risk score first, then by loan amount)
    df_sorted = df.sort_values(['delinquency_risk', 'loan_amount'], ascending=[False, False])
    
    # Save to CSV
    df_sorted.to_csv(filepath, index=False)
    
    print(f"✅ Saved {len(df):,} {risk_label} borrowers to: {filepath}")

def generate_campaign_files(db_path="student_loan_data.db"):
    """
    Main function to generate all campaign files.
    """
    print("🎯 GENERATING CAMPAIGN FILES")
    print("=" * 50)
    print(f"Database: {db_path}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Error: Database file '{db_path}' not found.")
        print("Please run 'python run_data_generation.py' first to create the database.")
        return False
    
    # Create campaigns folder
    campaigns_dir = create_campaigns_folder()
    
    # Check if delinquency risk scores exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM loan_info WHERE delinquency_risk IS NOT NULL")
        total_with_risk = cursor.fetchone()[0]
        
        if total_with_risk == 0:
            print("❌ Error: No delinquency risk scores found in database.")
            print("Please run 'python run_delinquency_analysis.py' first to calculate risk scores.")
            return False
            
        # Check risk distribution
        cursor.execute("SELECT delinquency_risk, COUNT(*) FROM loan_info GROUP BY delinquency_risk ORDER BY delinquency_risk")
        risk_dist = cursor.fetchall()
        
        print(f"\n📊 Risk Score Distribution:")
        risk_labels = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}
        for risk_level, count in risk_dist:
            if risk_level is not None:
                label = risk_labels.get(risk_level, f"Risk {risk_level}")
                pct = (count / total_with_risk) * 100
                print(f"   {label} ({risk_level}): {count:,} borrowers ({pct:.1f}%)")
        
    finally:
        conn.close()
    
    # Generate files for medium and high risk borrowers
    campaign_configs = [
        (1, "Medium Risk", "medium_risk_users.csv"),
        (2, "High Risk", "high_risk_users.csv")
    ]
    
    for risk_level, risk_label, filename in campaign_configs:
        print(f"\n🔄 Processing {risk_label} Borrowers...")
        
        # Extract data
        df = extract_campaign_data(db_path, risk_level, risk_label)
        
        # Generate summary
        generate_campaign_summary(df, risk_label)
        
        # Save file
        save_campaign_file(df, campaigns_dir, filename, risk_label)
    
    print(f"\n🎉 CAMPAIGN FILES GENERATION COMPLETE!")
    print(f"📁 Files saved in: {os.path.abspath(campaigns_dir)}")
    print(f"🕒 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def main():
    """
    Main entry point for campaign files generation.
    """
    parser = argparse.ArgumentParser(
        description="Generate targeted marketing campaign files based on delinquency risk levels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_campaign_files.py
  python run_campaign_files.py --db_path student_loan_data.db
  
The script generates two campaign files:
  - high_risk_users.csv (delinquency_risk = 2)
  - medium_risk_users.csv (delinquency_risk = 1)
  
Each file contains comprehensive borrower information for targeted campaigns.
        """
    )
    
    parser.add_argument(
        "--db_path",
        default="student_loan_data.db",
        help="Path to SQLite database (default: student_loan_data.db)"
    )
    
    args = parser.parse_args()
    
    try:
        success = generate_campaign_files(args.db_path)
        if not success:
            exit(1)
            
    except Exception as e:
        print(f"❌ Error generating campaign files: {str(e)}")
        print("\n🔍 Troubleshooting tips:")
        print("1. Ensure the database exists and has been populated")
        print("2. Run delinquency analysis first to calculate risk scores")
        print("3. Check database permissions and available disk space")
        exit(1)

if __name__ == "__main__":
    main()