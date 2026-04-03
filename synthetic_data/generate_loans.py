import pandas as pd
import sqlite3
import random
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

def generate_loan_info(num_payers, db_path=None):
    """
    Generates synthetic education loan records for each borrower.
    Now includes education program correlation for student loans.
    Returns a pandas DataFrame with loan information.
    """
    
    # Read program data if database exists
    program_data = {}
    if db_path:
        try:
            conn = sqlite3.connect(db_path)
            program_df = pd.read_sql_query("SELECT * FROM program_of_study", conn)
            conn.close()
            
            # Convert to dict for faster lookup
            for _, row in program_df.iterrows():
                program_data[row['program_id']] = {
                    'program_name': row['program_name'],
                    'program_difficulty': row['program_difficulty'],
                    'typical_tuition_cad': row['typical_tuition_cad'],
                    'duration_years': row['duration_years'],
                    'avg_starting_salary_cad': row['avg_starting_salary_cad'],
                    'employment_rate_percent': row['employment_rate_percent'],
                    'field_of_study': row['field_of_study']
                }
        except Exception as e:
            print(f"Warning: Could not read program data: {e}")
    
    # Get list of program IDs for random selection
    available_programs = list(program_data.keys()) if program_data else list(range(1, 43))  # Fallback
    
    # Loan types and their typical characteristics
    loan_types = [
        "Student Loan", "Education Line of Credit", "Parent PLUS Loan", 
        "Graduate Student Loan", "Professional Student Loan", "Private Education Loan"
    ]
    
    # Property types
    property_types = [
        "Single Family Detached", "Townhouse", "Condominium", 
        "Single Family Attached", "Multi-Family (2-4 units)"
    ]
    
    # Lender names (realistic Canadian financial institutions and education lenders)
    lenders = [
        "Royal Bank of Canada", "TD Canada Trust", "Bank of Nova Scotia", 
        "Bank of Montreal", "CIBC", "National Bank of Canada",
        "Canada Student Loans Program", "Provincial Student Aid", 
        "Scotiabank Student Line of Credit", "RBC Student Banking",
        "TD Student Line of Credit", "BMO Student Banking Program"
    ]
    
    # Property addresses - educational institutions across Canada
    institutions = [
        ("University of Toronto", "Toronto", "Ontario"),
        ("University of British Columbia", "Vancouver", "British Columbia"),
        ("McGill University", "Montreal", "Quebec"),
        ("University of Alberta", "Edmonton", "Alberta"),
        ("University of Calgary", "Calgary", "Alberta"),
        ("University of Ottawa", "Ottawa", "Ontario"),
        ("McMaster University", "Hamilton", "Ontario"),
        ("Queen's University", "Kingston", "Ontario"),
        ("University of Waterloo", "Waterloo", "Ontario"),
        ("Simon Fraser University", "Burnaby", "British Columbia"),
        ("University of Manitoba", "Winnipeg", "Manitoba"),
        ("Dalhousie University", "Halifax", "Nova Scotia"),
        ("University of Saskatchewan", "Saskatoon", "Saskatchewan"),
        ("Memorial University", "St. John's", "Newfoundland"),
        ("Carleton University", "Ottawa", "Ontario"),
        ("Ryerson University", "Toronto", "Ontario"),
        ("Concordia University", "Montreal", "Quebec"),
        ("York University", "Toronto", "Ontario"),
        ("University of Victoria", "Victoria", "British Columbia"),
        ("NAIT", "Edmonton", "Alberta")
    ]
    
    street_names = [
        "Maple Ave", "Oak St", "Pine St", "Cedar Ave", "Elm St", "King St",
        "Queen St", "Main St", "First Ave", "Second Ave", "Park Ave", "Church St",
        "Mill St", "Water St", "High St", "School St", "Spring St", "Wilson Ave",
        "Johnson St", "Smith St", "Brown Ave", "Davis St", "Miller Ave", "Moore St"
    ]
    
    loan_info = []
    current_date = datetime.now().date()
    
    for payer_id in range(1, num_payers + 1):
        # Select a random program for this payer
        program_id = random.choice(available_programs)
        
        # Get program information
        if program_id in program_data:
            program_info = program_data[program_id]
            base_tuition = program_info['typical_tuition_cad']
            duration = program_info['duration_years']
            difficulty = program_info['program_difficulty']
            expected_salary = program_info['avg_starting_salary_cad']
            employment_rate = program_info['employment_rate_percent']
        else:
            # Fallback values
            base_tuition = random.uniform(25000, 75000)
            duration = random.choice([2, 3, 4, 5])
            difficulty = random.randint(1, 3)
            expected_salary = random.uniform(40000, 80000)
            employment_rate = random.uniform(70, 95)
        
        # Calculate total education cost (tuition × years + living expenses)
        living_expenses_per_year = random.uniform(15000, 25000)
        total_education_cost = (base_tuition * duration) + (living_expenses_per_year * duration)
        
        # Loan amount is typically 60-90% of total education cost
        loan_coverage_ratio = random.uniform(0.6, 0.9)
        loan_amount = round(total_education_cost * loan_coverage_ratio, 2)
        
        # Interest rate varies by loan type and risk factors
        loan_type = random.choice(loan_types)
        
        # Education loans typically have different rates than traditional loans
        if "Student Loan" in loan_type or "Provincial" in loan_type:
            interest_rate = round(random.uniform(2.5, 4.5), 3)  # Government rates
        elif "Line of Credit" in loan_type:
            interest_rate = round(random.uniform(4.0, 7.5), 3)  # Bank rates
        else:  # Private loans
            interest_rate = round(random.uniform(5.5, 12.0), 3)  # Higher private rates
        
        # Difficulty affects interest rate (higher risk = higher rate)
        difficulty_adjustment = (difficulty - 1) * 0.5  # 0%, 0.5%, 1% increase
        interest_rate += difficulty_adjustment
        
        # Loan term varies by program type and amount
        if loan_amount < 30000:
            loan_term_years = random.choice([5, 7, 10])
        elif loan_amount < 60000:
            loan_term_years = random.choice([10, 15, 20])
        else:
            loan_term_years = random.choice([15, 20, 25])
        
        loan_term_months = loan_term_years * 12
        
        # Calculate property value and down payment (not applicable for education loans)
        # For education loans, we'll track the "education value" vs loan amount
        education_value = total_education_cost
        down_payment = education_value - loan_amount  # What student paid upfront
        ltv_ratio = round((loan_amount / education_value) * 100, 2)
        
        # Institution information
        institution_name, city, province = random.choice(institutions)
        
        # Loan dates
        years_ago = random.randint(0, int(duration) + 2)  # Recent graduates to current students
        months_ago = random.randint(0, 11)
        origination_date = current_date - relativedelta(years=years_ago, months=months_ago)
        
        # Disbursement date - spans exactly two full years (2022-2024 or 2023-2025)
        # Choose a two-year span for disbursements
        disbursement_start_year = random.choice([2022, 2023])  # Start either 2022 or 2023
        disbursement_end_year = disbursement_start_year + 1   # End the following year
        
        # Generate disbursement date within the two-year span
        # Typically at semester starts: January, May, September
        disbursement_month = random.choice([1, 5, 9])  # Academic term starts
        disbursement_year = random.choice([disbursement_start_year, disbursement_end_year])
        disbursement_day = random.randint(1, 15)  # Early in the month for term start
        
        disbursement_date = date(disbursement_year, disbursement_month, disbursement_day)
        
        # Ensure disbursement is after origination (adjust if needed)
        if disbursement_date < origination_date:
            # If disbursement would be before origination, set it to 30-90 days after origination
            disbursement_date = origination_date + timedelta(days=random.randint(30, 90))
        
        # Maturity date
        maturity_date = origination_date + relativedelta(months=loan_term_months)
        
        # Current balance calculation with education loan characteristics
        months_elapsed = max(0, (current_date - origination_date).days // 30)
        
        # Many education loans have grace periods or are in deferment
        grace_period_months = random.choice([0, 6, 12])  # 0-12 month grace period
        
        # Calculate payment and balance
        monthly_rate = interest_rate / 100 / 12
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term_months) / ((1 + monthly_rate)**loan_term_months - 1)
            
            # Account for grace period
            actual_payment_months = max(0, months_elapsed - grace_period_months)
            
            if actual_payment_months >= loan_term_months:
                current_balance = 0.0
                loan_status = "Paid Off"
            elif actual_payment_months <= 0:
                current_balance = loan_amount  # Still in grace period
                loan_status = "In Grace Period" if months_elapsed < grace_period_months else "Active"
            else:
                remaining_months = loan_term_months - actual_payment_months
                current_balance = monthly_payment * ((1 + monthly_rate)**remaining_months - 1) / (monthly_rate * (1 + monthly_rate)**remaining_months)
                current_balance = max(0, round(current_balance, 2))
                loan_status = "Active"
        else:
            monthly_payment = loan_amount / loan_term_months
            current_balance = max(0, loan_amount - (monthly_payment * max(0, months_elapsed - grace_period_months)))
            loan_status = "Active" if current_balance > 0 else "Paid Off"
        
        # Education loan specific statuses
        if random.random() < 0.05:  # 5% chance of deferment
            loan_status = "In Deferment"
        elif random.random() < 0.03:  # 3% chance of forbearance
            loan_status = "In Forbearance"
        elif random.random() < 0.02:  # 2% default rate (varies by difficulty)
            default_multiplier = difficulty * 0.5  # Higher difficulty = higher default risk
            if random.random() < (0.02 * default_multiplier):
                loan_status = "Defaulted"
        
        loan_info.append({
            'loan_id': payer_id,  # One loan per payer for simplicity
            'payer_id': payer_id,
            'program_id': program_id,
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'loan_term_years': loan_term_years,
            'loan_term_months': loan_term_months,
            'loan_type': loan_type,
            'institution_name': institution_name,
            'institution_city': city,
            'institution_province': province,
            'education_value': education_value,
            'down_payment': down_payment,
            'ltv_ratio': ltv_ratio,
            'origination_date': origination_date.strftime('%Y-%m-%d'),
            'disbursement_date': disbursement_date.strftime('%Y-%m-%d'),
            'maturity_date': maturity_date.strftime('%Y-%m-%d'),
            'current_balance': current_balance,
            'loan_status': loan_status,
            'lender': random.choice(lenders),
            'program_duration_years': duration,
            'monthly_payment': round(monthly_payment, 2),
            'grace_period_months': grace_period_months
        })
    
    return pd.DataFrame(loan_info)

def save_loans_to_sqlite(df, db_path):
    """
    Save loan records to SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the loan_info table with education program integration
    cursor.execute('''
    CREATE TABLE loan_info (
        loan_id INTEGER PRIMARY KEY,
        payer_id INTEGER NOT NULL,
        program_id INTEGER NOT NULL,
        loan_amount REAL NOT NULL,
        interest_rate REAL NOT NULL,
        loan_term_years INTEGER NOT NULL,
        loan_term_months INTEGER NOT NULL,
        loan_type TEXT NOT NULL,
        institution_name TEXT NOT NULL,
        institution_city TEXT NOT NULL,
        institution_province TEXT NOT NULL,
        education_value REAL NOT NULL,
        down_payment REAL NOT NULL,
        ltv_ratio REAL NOT NULL,
        origination_date TEXT NOT NULL,
        disbursement_date TEXT NOT NULL,
        maturity_date TEXT NOT NULL,
        current_balance REAL NOT NULL,
        loan_status TEXT NOT NULL,
        lender TEXT NOT NULL,
        program_duration_years REAL NOT NULL,
        monthly_payment REAL NOT NULL,
        grace_period_months INTEGER NOT NULL DEFAULT 0,
        delinquency_risk REAL DEFAULT 0.0,
        FOREIGN KEY (payer_id) REFERENCES user_profile (payer_id),
        FOREIGN KEY (program_id) REFERENCES program_of_study (program_id)
    )
    ''')
    
    # Insert data
    df.to_sql('loan_info', conn, if_exists='append', index=False)
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX idx_payer_id_loans ON loan_info(payer_id)')
    cursor.execute('CREATE INDEX idx_program_id_loans ON loan_info(program_id)')
    cursor.execute('CREATE INDEX idx_loan_status ON loan_info(loan_status)')
    cursor.execute('CREATE INDEX idx_loan_type ON loan_info(loan_type)')
    cursor.execute('CREATE INDEX idx_institution_city ON loan_info(institution_city)')
    cursor.execute('CREATE INDEX idx_lender ON loan_info(lender)')
    cursor.execute('CREATE INDEX idx_origination_date ON loan_info(origination_date)')
    cursor.execute('CREATE INDEX idx_disbursement_date ON loan_info(disbursement_date)')
    cursor.execute('CREATE INDEX idx_delinquency_risk ON loan_info(delinquency_risk)')
    
    conn.commit()
    conn.close()

def generate_loan_statistics(df):
    """
    Generate and display statistics about the loan data.
    """
    total_loans = len(df)
    total_loan_value = df['loan_amount'].sum()
    avg_loan_amount = df['loan_amount'].mean()
    avg_interest_rate = df['interest_rate'].mean()
    avg_ltv = df['ltv_ratio'].mean()
    
    # Status distribution
    status_counts = df['loan_status'].value_counts()
    
    # Loan type distribution
    type_counts = df['loan_type'].value_counts()
    
    print(f"\\nLoan Portfolio Statistics:")
    print(f"  Total loans: {total_loans:,}")
    print(f"  Total loan value: ${total_loan_value:,.2f}")
    print(f"  Average loan amount: ${avg_loan_amount:,.2f}")
    print(f"  Average interest rate: {avg_interest_rate:.3f}%")
    print(f"  Average LTV ratio: {avg_ltv:.1f}%")
    
    print(f"\\nLoan Status Distribution:")
    for status, count in status_counts.items():
        percentage = (count / total_loans) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    print(f"\\nTop Loan Types:")
    for loan_type, count in type_counts.head(5).items():
        percentage = (count / total_loans) * 100
        print(f"  {loan_type}: {count} ({percentage:.1f}%)")
    
    return {
        'total_loans': total_loans,
        'total_loan_value': total_loan_value,
        'avg_loan_amount': avg_loan_amount,
        'avg_interest_rate': avg_interest_rate,
        'status_counts': status_counts,
        'type_counts': type_counts
    }

# This module can be imported and used by run_data_generation.py
# No command line interface - use run_data_generation.py as the main entry point