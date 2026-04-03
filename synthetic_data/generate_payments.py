import pandas as pd
import numpy as np
import random
import sqlite3
from datetime import datetime, timedelta
import uuid

def generate_education_loan_payments(num_payers, start_date_str, end_date_str, db_path=None):
    """
    Generates synthetic education loan payment data synchronized with loan records.
    Uses actual loan amounts, terms, and interest rates for accurate amortization.
    Delinquency rates are correlated with multiple risk factors:
    1. Lower income (higher risk)
    2. Younger age (higher risk) 
    3. Program difficulty level (harder = higher risk)
    4. Proximity to maturity date (closer = higher risk)
    Payment schedules start after each loan's disbursement_date.
    Returns a pandas DataFrame with payment records.
    """
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)
    
    # Generate monthly payment due dates between the start and end dates
    # Note: Individual payment schedules will be generated per payer based on disbursement_date
    
    # If db_path is provided, read loan data from database
    loan_data = {}
    user_risk_factors = {}
    if db_path:
        try:
            conn = sqlite3.connect(db_path)
            # Read comprehensive data for delinquency risk calculation
            risk_query = """
            SELECT lr.*, pos.program_difficulty, up.annual_income_cad, up.age
            FROM loan_info lr
            JOIN program_of_study pos ON lr.program_id = pos.program_id
            JOIN user_profile up ON lr.payer_id = up.payer_id
            """
            risk_df = pd.read_sql_query(risk_query, conn)
            conn.close()
            
            # Convert to dict for faster lookup
            for _, row in risk_df.iterrows():
                loan_data[row['payer_id']] = {
                    'loan_amount': row['loan_amount'],
                    'interest_rate': row['interest_rate'],
                    'loan_term_months': row['loan_term_months'],
                    'monthly_payment': row['monthly_payment'],
                    'origination_date': pd.to_datetime(row['origination_date']),
                    'disbursement_date': pd.to_datetime(row['disbursement_date']),
                    'maturity_date': pd.to_datetime(row['maturity_date']),
                    'loan_status': row['loan_status']
                }
                user_risk_factors[row['payer_id']] = {
                    'program_difficulty': row['program_difficulty'],
                    'annual_income_cad': row['annual_income_cad'],
                    'age': row['age']
                }
        except Exception as e:
            print(f"Warning: Could not read loan data from database: {e}")
            print("Using default payment calculation...")
    
    # Calculate delinquency probability based on multiple risk factors:
    # 1. Lower income (higher risk)
    # 2. Younger age (higher risk) 
    # 3. Program difficulty level (harder = higher risk)
    # 4. Proximity to maturity date (closer = higher risk)
    #
    # Risk Scoring Model:
    # - Base Risk: 2%
    # - Income Risk: 0-8% (Unemployed=8%, <$25k=6%, <$40k=4%, <$60k=2%, $60k+=1%)
    # - Age Risk: 0-4% (<22=4%, <26=3%, <30=2%, 30+=1%)
    # - Difficulty Risk: 0-4% (Easy=1%, Moderate=2%, Hard=4%)
    # - Maturity Risk: 0-6% (<1yr=6%, <2yr=4%, <3yr=2%, 3yr+=1%)
    # - Total Risk Range: 2% to 25% (capped)
    
    def calculate_delinquency_risk(payer_id, current_date=end_date):
        """
        Calculate comprehensive delinquency risk score based on multiple factors.
        Returns probability between 0.01 and 0.25 (1% to 25% risk)
        """
        if payer_id not in user_risk_factors:
            return 0.05  # Default 5% risk if no data
        
        risk_data = user_risk_factors[payer_id]
        base_risk = 0.02  # Base 2% risk
        
        # Factor 1: Income Risk (0-8% additional risk)
        income = risk_data['annual_income_cad']
        if income == 0:  # Unemployed
            income_risk = 0.08
        elif income < 25000:  # Very low income
            income_risk = 0.06
        elif income < 40000:  # Low income
            income_risk = 0.04
        elif income < 60000:  # Moderate income
            income_risk = 0.02
        else:  # Higher income
            income_risk = 0.01
        
        # Factor 2: Age Risk (0-4% additional risk)
        age = risk_data['age']
        if age < 22:  # Very young
            age_risk = 0.04
        elif age < 26:  # Young
            age_risk = 0.03
        elif age < 30:  # Moderate
            age_risk = 0.02
        else:  # More mature
            age_risk = 0.01
        
        # Factor 3: Program Difficulty Risk (0-4% additional risk)
        difficulty = risk_data['program_difficulty']
        if difficulty == 1:  # Easy programs
            difficulty_risk = 0.01
        elif difficulty == 2:  # Moderate programs
            difficulty_risk = 0.02
        else:  # difficulty == 3, Hard programs
            difficulty_risk = 0.04
        
        # Factor 4: Maturity Proximity Risk (0-6% additional risk)
        if payer_id in loan_data:
            maturity_date = loan_data[payer_id]['maturity_date']
            days_to_maturity = (maturity_date - current_date).days
            
            if days_to_maturity < 365:  # Less than 1 year to maturity
                maturity_risk = 0.06
            elif days_to_maturity < 730:  # Less than 2 years
                maturity_risk = 0.04
            elif days_to_maturity < 1095:  # Less than 3 years
                maturity_risk = 0.02
            else:  # More than 3 years
                maturity_risk = 0.01
        else:
            maturity_risk = 0.02  # Default
        
        # Combine all risk factors
        total_risk = base_risk + income_risk + age_risk + difficulty_risk + maturity_risk
        
        # Cap at 25% maximum risk
        return min(total_risk, 0.25)
    
    delinquent_payers_set = set()
    for payer_id in range(1, num_payers + 1):
        delinquency_probability = calculate_delinquency_risk(payer_id)
        
        if random.random() < delinquency_probability:
            delinquent_payers_set.add(payer_id)
    
    # Payment methods
    payment_methods = ["Bank Transfer", "Online Payment", "Check", "Auto-Pay", "Phone Payment", "Mobile App"]
    payment_processors = ["Interac", "Visa Debit", "Mastercard Debit", "RBC Online", "TD EasyWeb", "BMO Digital Banking"]
    
    data = []
    
    for payer_id in range(1, num_payers + 1):
        # Get loan data for this payer
        if payer_id in loan_data:
            loan_info = loan_data[payer_id]
            loan_amount = loan_info['loan_amount']
            annual_rate = loan_info['interest_rate'] / 100
            monthly_rate = annual_rate / 12
            loan_term_months = loan_info['loan_term_months']
            monthly_payment = loan_info['monthly_payment']
            loan_status = loan_info['loan_status']
            disbursement_date = loan_info['disbursement_date']
            maturity_date = loan_info['maturity_date']
        else:
            # Fallback to random values if no loan data
            loan_amount = round(random.uniform(200000, 800000), 2)
            annual_rate = random.uniform(0.03, 0.06)
            monthly_rate = annual_rate / 12
            loan_term_months = random.choice([180, 240, 300, 360])  # 15, 20, 25, 30 years
            disbursement_date = start_date  # Fallback to start_date
            maturity_date = start_date + pd.DateOffset(months=loan_term_months)  # Calculate maturity
            
            # Calculate monthly payment using standard formula
            if monthly_rate > 0:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term_months) / ((1 + monthly_rate)**loan_term_months - 1)
            else:
                monthly_payment = loan_amount / loan_term_months
            loan_status = "Active"
        
        # Generate individual payment schedule starting after disbursement_date
        # First payment due is typically 30-60 days after disbursement
        first_payment_due = disbursement_date + pd.DateOffset(days=random.randint(30, 60))
        # Round to first of month for realistic payment scheduling
        first_payment_due = first_payment_due.replace(day=1)
        
        # Generate payment due dates for this payer from first payment until end_date
        payer_payment_dates = pd.date_range(
            start=first_payment_due, 
            end=end_date, 
            freq='MS'
        )
        
        # Skip if no valid payment dates for this payer
        if len(payer_payment_dates) == 0:
            continue
        
        # If payer is delinquent, pick 1 or 2 random months to miss a payment
        missed_months = []
        if payer_id in delinquent_payers_set and loan_status == "Active":
            num_missed = random.choice([1, 2])
            missed_months = random.sample(range(len(payer_payment_dates)), min(num_missed, len(payer_payment_dates)))
        
        # Calculate remaining balance for amortization schedule
        remaining_balance = loan_amount
        
        for i, due_date in enumerate(payer_payment_dates):
            # Skip payments if loan is not active
            if loan_status in ["Paid Off", "Defaulted", "Refinanced"]:
                break
                
            status = 'Missed' if i in missed_months else 'Paid'
            
            # Calculate payment breakdown for amortization
            if remaining_balance <= 0:
                # Loan is paid off
                principal_payment = 0
                interest_payment = 0
                total_payment = 0
                remaining_balance = 0
                status = 'Paid'
            elif status == 'Missed':
                principal_payment = 0
                interest_payment = 0
                total_payment = 0
                # Balance remains the same
            else:
                # Normal payment calculation
                interest_payment = remaining_balance * monthly_rate
                principal_payment = monthly_payment - interest_payment
                
                # Ensure we don't overpay on the last payment
                if remaining_balance < principal_payment:
                    principal_payment = remaining_balance
                    total_payment = principal_payment + interest_payment
                else:
                    total_payment = monthly_payment
                
                remaining_balance -= principal_payment
                remaining_balance = max(0, remaining_balance)
            
            # Additional student loan payment attributes
            escrow_payment = round(random.uniform(200, 800), 2) if status == 'Paid' else 0  # Property taxes + insurance
            
            # Late fee calculation
            late_fee = 0
            payment_behavior = None
            days_late = 0
            
            # Generate paid_date based on status
            if status == 'Paid':
                # Payment timing logic
                payment_behavior = random.choices(
                    ['on_time', 'within_week', 'late'], 
                    weights=[80, 15, 5]
                )[0]
                
                if payment_behavior == 'on_time':
                    days_late = random.randint(0, 2)
                elif payment_behavior == 'within_week':
                    days_late = random.randint(3, 7)
                else:  # late
                    days_late = random.randint(8, 15)
                    # Late fee calculation (typically 4-5% of payment or $25-50 minimum)
                    late_fee = max(25, round(total_payment * 0.04, 2))
                
                paid_date = due_date + timedelta(days=days_late)
            else:
                # For missed payments, no paid date
                paid_date = None
            
            # Payment method and processing details
            payment_method = random.choice(payment_methods) if status == 'Paid' else None
            payment_processor = random.choice(payment_processors) if status == 'Paid' else None
            transaction_id = str(uuid.uuid4())[:8].upper() if status == 'Paid' else None
            
            # Payment confirmation number
            confirmation_number = f"MP{random.randint(100000, 999999)}" if status == 'Paid' else None
            
            data.append({
                'payer_id': payer_id,
                'due_date': due_date.strftime('%Y-%m-%d'),
                'paid_date': paid_date.strftime('%Y-%m-%d') if paid_date else None,
                'payment_due': round(monthly_payment, 2),
                'amount_paid': round(total_payment, 2),
                'principal_payment': round(principal_payment, 2),
                'interest_payment': round(interest_payment, 2),
                'escrow_payment': escrow_payment,
                'late_fee': late_fee,
                'total_amount_due': round(monthly_payment + escrow_payment, 2),
                'remaining_balance': round(remaining_balance, 2),
                'status': status,
                'days_late': days_late if status == 'Paid' else None,
                'payment_method': payment_method,
                'payment_processor': payment_processor,
                'transaction_id': transaction_id,
                'confirmation_number': confirmation_number,
                'payment_type': 'Regular' if late_fee == 0 else 'Late Payment'
            })
            
    df = pd.DataFrame(data)
    return df

def save_payments_to_sqlite(df, db_path):
    """
    Save student loan payments to SQLite database with enhanced schema.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the loan_payments table with enhanced schema
    cursor.execute('''
    CREATE TABLE loan_payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        payer_id INTEGER NOT NULL,
        due_date TEXT NOT NULL,
        paid_date TEXT,
        payment_due REAL NOT NULL,
        amount_paid REAL NOT NULL,
        principal_payment REAL NOT NULL,
        interest_payment REAL NOT NULL,
        escrow_payment REAL NOT NULL,
        late_fee REAL NOT NULL DEFAULT 0,
        total_amount_due REAL NOT NULL,
        remaining_balance REAL NOT NULL,
        status TEXT NOT NULL,
        days_late INTEGER,
        payment_method TEXT,
        payment_processor TEXT,
        transaction_id TEXT,
        confirmation_number TEXT,
        payment_type TEXT,
        FOREIGN KEY (payer_id) REFERENCES user_profile (payer_id)
    )
    ''')
    
    # Insert data
    df.to_sql('loan_payments', conn, if_exists='append', index=False)
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX idx_payer_id_payments ON loan_payments(payer_id)')
    cursor.execute('CREATE INDEX idx_due_date ON loan_payments(due_date)')
    cursor.execute('CREATE INDEX idx_status ON loan_payments(status)')
    cursor.execute('CREATE INDEX idx_paid_date ON loan_payments(paid_date)')
    cursor.execute('CREATE INDEX idx_payment_method ON loan_payments(payment_method)')
    cursor.execute('CREATE INDEX idx_payment_type ON loan_payments(payment_type)')
    cursor.execute('CREATE INDEX idx_transaction_id ON loan_payments(transaction_id)')
    
    conn.commit()
    conn.close()

def generate_payment_statistics(df):
    """
    Generate and display statistics about the payment data.
    """
    total_payments = len(df)
    total_payers = df['payer_id'].nunique()
    
    # Status distribution
    status_counts = df['status'].value_counts()
    
    # Payment behavior analysis
    paid_df = df[df['status'] == 'Paid'].copy()
    if not paid_df.empty:
        paid_df['due_date'] = pd.to_datetime(paid_df['due_date'])
        paid_df['paid_date'] = pd.to_datetime(paid_df['paid_date'])
        paid_df['days_late'] = (paid_df['paid_date'] - paid_df['due_date']).dt.days
        
        on_time_count = len(paid_df[paid_df['days_late'] <= 2])
        within_week_count = len(paid_df[(paid_df['days_late'] > 2) & (paid_df['days_late'] <= 7)])
        late_count = len(paid_df[paid_df['days_late'] > 7])
        
        print(f"\\nPayment Behavior Analysis:")
        print(f"  On-time (0-2 days): {on_time_count} ({on_time_count/len(paid_df)*100:.1f}%)")
        print(f"  Within week (3-7 days): {within_week_count} ({within_week_count/len(paid_df)*100:.1f}%)")
        print(f"  Late (8+ days): {late_count} ({late_count/len(paid_df)*100:.1f}%)")
        print(f"  Average days late: {paid_df['days_late'].mean():.1f}")
    
    return {
        'total_payments': total_payments,
        'total_payers': total_payers,
        'status_counts': status_counts
    }

# This module can be imported and used by run_data_generation.py
# No command line interface - use run_data_generation.py as the main entry point