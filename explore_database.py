import sqlite3
import pandas as pd

def explore_database(db_path="student_loan_data.db"):
    """
    Explore the database structure and show sample data
    """
    conn = sqlite3.connect(db_path)
    
    print("=== DATABASE STRUCTURE ===")
    
    # Get table information
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Define expected table names for validation (prevents SQL injection)
    expected_tables = {'user_profile', 'program_of_study', 'loan_info', 'loan_payments'}
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Validate table name against expected schema before using in SQL
        if table_name in expected_tables:
            # Method 1: Use explicit string validation and safe construction
            # Validate table name contains only safe characters
            if table_name.replace('_', '').isalnum():
                # Construct SQL with validated identifier (no f-string interpolation)
                sql_query = 'PRAGMA table_info("' + table_name + '")'  # nosec B608
                cursor.execute(sql_query)
                columns = cursor.fetchall()
            else:
                print(f"  Error: Invalid table name characters: {table_name}")
                continue
        else:
            print(f"  Warning: Unexpected table '{table_name}' found in database")
            continue
        
        print("Columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}){' PRIMARY KEY' if col[5] else ''}")
    
    print("\n" + "="*50)
    print("SAMPLE USER PROFILES")
    print("="*50)
    
    # Sample user profiles with different characteristics
    query = """
    SELECT 
        payer_id,
        first_name || ' ' || last_name as full_name,
        age,
        city || ', ' || province as location,
        employment_status,
        annual_income_cad,
        marital_status
    FROM user_profile 
    ORDER BY payer_id 
    LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print("\n" + "="*50)
    print("EMPLOYMENT AND INCOME ANALYSIS")
    print("="*50)
    
    # Employment analysis
    query = """
    SELECT 
        employment_status,
        COUNT(*) as count,
        AVG(annual_income_cad) as avg_income,
        MIN(annual_income_cad) as min_income,
        MAX(annual_income_cad) as max_income
    FROM user_profile 
    GROUP BY employment_status
    ORDER BY avg_income DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print("\n" + "="*50)
    print("GEOGRAPHIC DISTRIBUTION")
    print("="*50)
    
    # Geographic distribution
    query = """
    SELECT 
        province,
        COUNT(*) as users,
        AVG(annual_income_cad) as avg_income
    FROM user_profile 
    GROUP BY province
    ORDER BY users DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print("\n" + "="*50)
    print("AGE DEMOGRAPHICS")
    print("="*50)
    
    # Age demographics
    query = """
    SELECT 
        CASE 
            WHEN age BETWEEN 18 AND 25 THEN '18-25'
            WHEN age BETWEEN 26 AND 35 THEN '26-35'
            WHEN age BETWEEN 36 AND 44 THEN '36-44'
        END as age_group,
        COUNT(*) as users,
        AVG(annual_income_cad) as avg_income
    FROM user_profile 
    GROUP BY age_group
    ORDER BY age_group
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print("\n" + "="*50)
    print("EDUCATION LOAN PAYMENT INTEGRATION EXAMPLE")
    print("="*50)
    
    # Show integration between user profiles and education loan payments
    query = """
    SELECT 
        up.payer_id,
        up.first_name || ' ' || up.last_name as full_name,
        up.age,
        up.city,
        up.employment_status,
        up.annual_income_cad,
        COUNT(mp.due_date) as total_payments,
        SUM(CASE WHEN mp.status = 'Missed' THEN 1 ELSE 0 END) as missed_payments,
        AVG(mp.payment_due) as avg_payment_due
    FROM user_profile up
    JOIN loan_payments mp ON up.payer_id = mp.payer_id
    GROUP BY up.payer_id
    HAVING missed_payments > 0
    ORDER BY missed_payments DESC
    LIMIT 5
    """
    
    df = pd.read_sql_query(query, conn)
    print("Top 5 students with missed payments:")
    print(df.to_string(index=False))
    
    print("\n" + "="*50)
    print("PAYMENT TIMING ANALYSIS")
    print("="*50)
    
    # Payment timing analysis using new due_date and paid_date columns
    query = """
    SELECT 
        payer_id,
        due_date,
        paid_date,
        payment_due,
        amount_paid,
        status,
        CASE 
            WHEN status = 'Paid' THEN 
                julianday(paid_date) - julianday(due_date)
            ELSE NULL
        END as days_difference
    FROM loan_payments 
    WHERE status = 'Paid'
    ORDER BY days_difference DESC
    LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    print("Top 10 latest payments (days after due date):")
    print(df.to_string(index=False))
    
    # Payment behavior summary
    query = """
    SELECT 
        CASE 
            WHEN status = 'Missed' THEN 'Missed Payment'
            WHEN julianday(paid_date) - julianday(due_date) <= 2 THEN 'On Time (0-2 days)'
            WHEN julianday(paid_date) - julianday(due_date) <= 7 THEN 'Within Week (3-7 days)'
            ELSE 'Late (8+ days)'
        END as payment_behavior,
        COUNT(*) as count,
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM loan_payments) as percentage
    FROM loan_payments 
    GROUP BY payment_behavior
    ORDER BY count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\nPayment Behavior Summary:")
    print(df.to_string(index=False))
    
    print("\\n" + "="*50)
    print("ENHANCED PAYMENT ANALYSIS")
    print("="*50)
    
    # Enhanced payment breakdown analysis
    query = """
    SELECT 
        payer_id,
        due_date,
        paid_date,
        payment_due,
        principal_payment,
        interest_payment,
        escrow_payment,
        late_fee,
        remaining_balance,
        status,
        payment_method,
        payment_type
    FROM loan_payments 
    WHERE status = 'Paid'
    ORDER BY due_date
    LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    print("Sample Enhanced Payment Records:")
    print(df.to_string(index=False))
    
    # Payment method analysis
    query = """
    SELECT 
        payment_method,
        COUNT(*) as count,
        AVG(amount_paid) as avg_amount,
        AVG(days_late) as avg_days_late
    FROM loan_payments 
    WHERE status = 'Paid' AND payment_method IS NOT NULL
    GROUP BY payment_method
    ORDER BY count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\\nPayment Method Analysis:")
    print(df.to_string(index=False))
    
    # Late fee analysis
    query = """
    SELECT 
        CASE 
            WHEN late_fee = 0 THEN 'No Late Fee'
            WHEN late_fee BETWEEN 0.01 AND 50 THEN 'Low Late Fee ($0-$50)'
            WHEN late_fee BETWEEN 50.01 AND 100 THEN 'Medium Late Fee ($50-$100)'
            ELSE 'High Late Fee ($100+)'
        END as late_fee_category,
        COUNT(*) as count,
        AVG(late_fee) as avg_late_fee,
        SUM(late_fee) as total_late_fees
    FROM loan_payments 
    WHERE status = 'Paid'
    GROUP BY late_fee_category
    ORDER BY count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\\nLate Fee Analysis:")
    print(df.to_string(index=False))
    
    # Principal vs Interest breakdown over time
    query = """
    SELECT 
        substr(due_date, 1, 7) as year_month,
        COUNT(*) as payment_count,
        AVG(principal_payment) as avg_principal,
        AVG(interest_payment) as avg_interest,
        AVG(escrow_payment) as avg_escrow,
        AVG(remaining_balance) as avg_remaining_balance
    FROM loan_payments 
    WHERE status = 'Paid'
    GROUP BY substr(due_date, 1, 7)
    ORDER BY year_month
    LIMIT 12
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\\nPrincipal vs Interest Over Time (First 12 Months):")
    print(df.to_string(index=False))
    
    print("\\n" + "="*50)
    print("LOAN PORTFOLIO ANALYSIS")
    print("="*50)
    
    # Loan portfolio overview
    query = """
    SELECT 
        loan_status,
        COUNT(*) as loan_count,
        AVG(loan_amount) as avg_loan_amount,
        AVG(interest_rate) as avg_interest_rate,
        AVG(ltv_ratio) as avg_ltv_ratio,
        SUM(loan_amount) as total_portfolio_value
    FROM loan_info 
    GROUP BY loan_status
    ORDER BY loan_count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"Loan Portfolio by Status:")
    print(df.to_string(index=False))
    
    # Top lenders
    query = """
    SELECT 
        lender,
        COUNT(*) as loan_count,
        AVG(interest_rate) as avg_rate,
        SUM(loan_amount) as total_value
    FROM loan_info 
    GROUP BY lender
    ORDER BY loan_count DESC
    LIMIT 5
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\nTop 5 Lenders:")
    print(df.to_string(index=False))
    
    # Institution analysis
    query = """
    SELECT 
        institution_name,
        COUNT(*) as count,
        AVG(education_value) as avg_education_value,
        AVG(loan_amount) as avg_loan_amount
    FROM loan_info 
    GROUP BY institution_name
    ORDER BY count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\nInstitution Analysis:")
    print(df.to_string(index=False))
    
    print("\n" + "="*50)
    print("EDUCATION PROGRAM ANALYSIS")
    print("="*50)
    
    # Program of study analysis
    query = """
    SELECT 
        pos.field_of_study,
        pos.program_difficulty,
        COUNT(lr.loan_id) as loan_count,
        AVG(lr.loan_amount) as avg_loan_amount,
        AVG(pos.typical_tuition_cad) as avg_tuition,
        AVG(pos.employment_rate_percent) as avg_employment_rate
    FROM program_of_study pos
    LEFT JOIN loan_info lr ON pos.program_id = lr.program_id
    GROUP BY pos.field_of_study, pos.program_difficulty
    ORDER BY loan_count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\nEducation Program Analysis:")
    print(df.to_string(index=False))
    
    # University analysis
    query = """
    SELECT 
        pos.university_name,
        COUNT(lr.loan_id) as loan_count,
        AVG(lr.loan_amount) as avg_loan_amount,
        AVG(pos.typical_tuition_cad) as avg_tuition
    FROM program_of_study pos
    LEFT JOIN loan_info lr ON pos.program_id = lr.program_id
    GROUP BY pos.university_name
    HAVING loan_count > 0
    ORDER BY loan_count DESC
    LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\nTop 10 Universities by Loan Volume:")
    print(df.to_string(index=False))
    
    print("\n" + "="*50)
    print("COMPREHENSIVE BORROWER ANALYSIS")
    print("="*50)
    
    # Comprehensive analysis joining all tables
    query = """
    SELECT 
        up.payer_id,
        up.first_name || ' ' || up.last_name as full_name,
        up.age,
        up.employment_status,
        up.annual_income_cad,
        pos.program_name,
        pos.field_of_study,
        pos.program_difficulty,
        pos.university_name,
        lr.loan_amount,
        lr.interest_rate,
        lr.loan_status,
        lr.lender,
        COUNT(mp.due_date) as total_payments,
        SUM(CASE WHEN mp.status = 'Missed' THEN 1 ELSE 0 END) as missed_payments,
        AVG(mp.principal_payment) as avg_principal,
        AVG(mp.interest_payment) as avg_interest,
        SUM(mp.late_fee) as total_late_fees,
        MIN(mp.remaining_balance) as current_balance
    FROM user_profile up
    JOIN loan_info lr ON up.payer_id = lr.payer_id
    JOIN program_of_study pos ON lr.program_id = pos.program_id
    JOIN loan_payments mp ON up.payer_id = mp.payer_id
    WHERE mp.status = 'Paid'
    GROUP BY up.payer_id
    ORDER BY missed_payments DESC, total_late_fees DESC, lr.loan_amount DESC
    LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"Top 10 Student Profiles (by risk, late fees, and loan size):")
    print(df.to_string(index=False))
    
    print("\n" + "="*50)
    print("DELINQUENCY RISK FACTOR ANALYSIS")
    print("="*50)
    
    # Delinquency by Income Level
    print(f"\nDelinquency Rate by Income Level:")
    income_query = """
    SELECT 
        CASE 
            WHEN up.annual_income_cad = 0 THEN 'Unemployed ($0)'
            WHEN up.annual_income_cad < 25000 THEN 'Very Low (<$25k)'
            WHEN up.annual_income_cad < 40000 THEN 'Low ($25k-$40k)'
            WHEN up.annual_income_cad < 60000 THEN 'Moderate ($40k-$60k)'
            ELSE 'Higher ($60k+)'
        END as income_bracket,
        COUNT(DISTINCT up.payer_id) as total_borrowers,
        COUNT(DISTINCT CASE WHEN mp.status = 'Missed' THEN up.payer_id END) as delinquent_borrowers,
        ROUND(COUNT(DISTINCT CASE WHEN mp.status = 'Missed' THEN up.payer_id END) * 100.0 / 
              COUNT(DISTINCT up.payer_id), 2) as delinquency_rate_percent,
        AVG(up.annual_income_cad) as avg_income
    FROM user_profile up
    JOIN loan_info lr ON up.payer_id = lr.payer_id
    LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id AND mp.status = 'Missed'
    GROUP BY income_bracket
    ORDER BY avg_income
    """
    
    df = pd.read_sql_query(income_query, conn)
    print(df.to_string(index=False))
    
    # Delinquency by Age Group
    print(f"\nDelinquency Rate by Age Group:")
    age_query = """
    SELECT 
        CASE 
            WHEN up.age < 22 THEN 'Very Young (<22)'
            WHEN up.age < 26 THEN 'Young (22-25)'
            WHEN up.age < 30 THEN 'Moderate (26-29)'
            ELSE 'Mature (30+)'
        END as age_group,
        COUNT(DISTINCT up.payer_id) as total_borrowers,
        COUNT(DISTINCT CASE WHEN mp.status = 'Missed' THEN up.payer_id END) as delinquent_borrowers,
        ROUND(COUNT(DISTINCT CASE WHEN mp.status = 'Missed' THEN up.payer_id END) * 100.0 / 
              COUNT(DISTINCT up.payer_id), 2) as delinquency_rate_percent,
        AVG(up.age) as avg_age
    FROM user_profile up
    JOIN loan_info lr ON up.payer_id = lr.payer_id
    LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id AND mp.status = 'Missed'
    GROUP BY age_group
    ORDER BY avg_age
    """
    
    df = pd.read_sql_query(age_query, conn)
    print(df.to_string(index=False))
    
    # Delinquency by Program Difficulty (Enhanced)
    print(f"\nDelinquency Rate by Program Difficulty:")
    difficulty_query = """
    SELECT 
        pos.program_difficulty,
        CASE 
            WHEN pos.program_difficulty = 1 THEN 'Easy Programs'
            WHEN pos.program_difficulty = 2 THEN 'Moderate Programs'
            ELSE 'Hard Programs'
        END as difficulty_level,
        COUNT(DISTINCT up.payer_id) as total_borrowers,
        COUNT(DISTINCT CASE WHEN mp.status = 'Missed' THEN up.payer_id END) as delinquent_borrowers,
        ROUND(COUNT(DISTINCT CASE WHEN mp.status = 'Missed' THEN up.payer_id END) * 100.0 / 
              COUNT(DISTINCT up.payer_id), 2) as delinquency_rate_percent
    FROM user_profile up
    JOIN loan_info lr ON up.payer_id = lr.payer_id
    JOIN program_of_study pos ON lr.program_id = pos.program_id
    LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id AND mp.status = 'Missed'
    GROUP BY pos.program_difficulty, difficulty_level
    ORDER BY pos.program_difficulty
    """
    
    df = pd.read_sql_query(difficulty_query, conn)
    print(df.to_string(index=False))
    
    # Delinquency by Proximity to Maturity
    print(f"\nDelinquency Rate by Loan Maturity Proximity:")
    maturity_query = """
    SELECT 
        CASE 
            WHEN (julianday(lr.maturity_date) - julianday('now')) / 365.25 < 1 THEN 'Less than 1 year'
            WHEN (julianday(lr.maturity_date) - julianday('now')) / 365.25 < 2 THEN '1-2 years'
            WHEN (julianday(lr.maturity_date) - julianday('now')) / 365.25 < 3 THEN '2-3 years'
            ELSE 'More than 3 years'
        END as time_to_maturity,
        COUNT(DISTINCT up.payer_id) as total_borrowers,
        COUNT(DISTINCT CASE WHEN mp.status = 'Missed' THEN up.payer_id END) as delinquent_borrowers,
        ROUND(COUNT(DISTINCT CASE WHEN mp.status = 'Missed' THEN up.payer_id END) * 100.0 / 
              COUNT(DISTINCT up.payer_id), 2) as delinquency_rate_percent,
        ROUND(AVG((julianday(lr.maturity_date) - julianday('now')) / 365.25), 1) as avg_years_to_maturity
    FROM user_profile up
    JOIN loan_info lr ON up.payer_id = lr.payer_id
    LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id AND mp.status = 'Missed'
    GROUP BY time_to_maturity
    ORDER BY avg_years_to_maturity
    """
    
    df = pd.read_sql_query(maturity_query, conn)
    print(df.to_string(index=False))
    
    # Combined Risk Factor Analysis
    print(f"\nCombined Risk Factor Summary - High Risk Profile:")
    high_risk_query = """
    SELECT 
        up.payer_id,
        up.first_name || ' ' || up.last_name as full_name,
        up.age,
        up.annual_income_cad,
        pos.program_difficulty,
        ROUND((julianday(lr.maturity_date) - julianday('now')) / 365.25, 1) as years_to_maturity,
        COUNT(CASE WHEN mp.status = 'Missed' THEN 1 END) as missed_payments,
        CASE 
            WHEN COUNT(CASE WHEN mp.status = 'Missed' THEN 1 END) > 0 THEN 'DELINQUENT' 
            ELSE 'Current' 
        END as status
    FROM user_profile up
    JOIN loan_info lr ON up.payer_id = lr.payer_id
    JOIN program_of_study pos ON lr.program_id = pos.program_id
    LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id
    WHERE (up.annual_income_cad < 40000 OR up.age < 26 OR pos.program_difficulty = 3 OR 
           (julianday(lr.maturity_date) - julianday('now')) / 365.25 < 2)
    GROUP BY up.payer_id
    ORDER BY missed_payments DESC, up.annual_income_cad ASC, up.age ASC
    LIMIT 10
    """
    
    df = pd.read_sql_query(high_risk_query, conn)
    print(df.to_string(index=False))
    
    # ML-Based Delinquency Risk Analysis (if risk scores are available)
    print(f"\nML-BASED DELINQUENCY RISK ANALYSIS:")
    risk_check_query = "SELECT COUNT(*) as count FROM pragma_table_info('loan_info') WHERE name='delinquency_risk'"
    has_risk_column = pd.read_sql_query(risk_check_query, conn).iloc[0]['count'] > 0
    
    if has_risk_column:
        print(f"Machine Learning Risk Scores Available")
        print("-" * 50)
        
        # Risk score distribution
        risk_distribution_query = """
        SELECT 
            CASE 
                WHEN li.delinquency_risk BETWEEN 0 AND 5 THEN 'Very Low (0-5%)'
                WHEN li.delinquency_risk BETWEEN 5 AND 10 THEN 'Low (5-10%)'
                WHEN li.delinquency_risk BETWEEN 10 AND 15 THEN 'Moderate (10-15%)'
                WHEN li.delinquency_risk BETWEEN 15 AND 25 THEN 'High (15-25%)'
                WHEN li.delinquency_risk BETWEEN 25 AND 50 THEN 'Very High (25-50%)'
                ELSE 'Extreme (50%+)'
            END as risk_category,
            COUNT(*) as borrower_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM loan_info), 2) as percentage,
            AVG(li.delinquency_risk) as avg_risk_score,
            COUNT(CASE WHEN mp.status = 'Missed' THEN up.payer_id END) as actual_delinquent_count
        FROM loan_info li
        JOIN user_profile up ON li.payer_id = up.payer_id
        LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id AND mp.status = 'Missed'
        WHERE li.delinquency_risk IS NOT NULL AND li.delinquency_risk > 0
        GROUP BY risk_category
        ORDER BY avg_risk_score
        """
        
        df = pd.read_sql_query(risk_distribution_query, conn)
        print("Risk Score Distribution:")
        print(df.to_string(index=False))
        
        # Top 10 highest risk borrowers
        high_risk_borrowers_query = """
        SELECT 
            up.payer_id,
            up.first_name || ' ' || up.last_name as full_name,
            up.age,
            up.annual_income_cad,
            pos.program_difficulty,
            li.loan_amount,
            ROUND(li.delinquency_risk, 2) as risk_score_pct,
            COUNT(CASE WHEN mp.status = 'Missed' THEN 1 END) as actual_missed_payments,
            CASE WHEN COUNT(CASE WHEN mp.status = 'Missed' THEN 1 END) > 0 THEN 'DELINQUENT' ELSE 'Current' END as actual_status
        FROM loan_info li
        JOIN user_profile up ON li.payer_id = up.payer_id
        JOIN program_of_study pos ON li.program_id = pos.program_id
        LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id
        WHERE li.delinquency_risk IS NOT NULL AND li.delinquency_risk > 0
        GROUP BY up.payer_id
        ORDER BY li.delinquency_risk DESC
        LIMIT 10
        """
        
        df = pd.read_sql_query(high_risk_borrowers_query, conn)
        print(f"\nTop 10 Highest Risk Borrowers (ML Predicted):")
        print(df.to_string(index=False))
        
        # Model validation - correlation between predicted risk and actual delinquency
        validation_query = """
        SELECT 
            ROUND(AVG(li.delinquency_risk), 2) as avg_predicted_risk,
            COUNT(CASE WHEN mp.status = 'Missed' THEN up.payer_id END) * 100.0 / COUNT(DISTINCT up.payer_id) as actual_delinquency_rate,
            COUNT(DISTINCT up.payer_id) as total_borrowers
        FROM loan_info li
        JOIN user_profile up ON li.payer_id = up.payer_id
        LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id AND mp.status = 'Missed'
        WHERE li.delinquency_risk IS NOT NULL AND li.delinquency_risk > 0
        """
        
        df = pd.read_sql_query(validation_query, conn)
        print(f"\nModel Validation Summary:")
        print(f"Average Predicted Risk: {df.iloc[0]['avg_predicted_risk']:.2f}%")
        print(f"Actual Delinquency Rate: {df.iloc[0]['actual_delinquency_rate']:.2f}%")
        print(f"Total Borrowers Analyzed: {df.iloc[0]['total_borrowers']:,}")
    else:
        print("Machine Learning risk scores not available.")
        print("Run 'python delinquency_analysis.py' to generate ML-based risk scores.")
    
    conn.close()

if __name__ == "__main__":
    explore_database()