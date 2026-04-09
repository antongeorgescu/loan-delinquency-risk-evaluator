"""
Database utilities for SQLite operations in local development
"""
import os
import sqlite3
import json
from typing import List, Dict, Any


class DatabaseManager:
    def __init__(self, db_path=None):
        # Use custom path if provided, otherwise default to shared directory
        if db_path:
            self.db_filename = db_path
        else:
            self.db_filename = os.path.join(os.path.dirname(__file__), "student_loan_data.db")
        
    def get_connection(self) -> sqlite3.Connection:
        """Get SQLite connection"""
        # Check if database exists, if not create it
        if not os.path.exists(self.db_filename):
            self.create_database()
        
        return sqlite3.connect(self.db_filename)
    
    def create_database(self):
        """Create initial database schema"""
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        
        # Create tables with correct schema matching the actual data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                payer_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                date_of_birth TEXT,
                age INTEGER,
                address TEXT,
                city TEXT,
                province TEXT,
                employment_status TEXT,
                annual_income_cad INTEGER,
                marital_status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS program_of_study (
                program_id INTEGER PRIMARY KEY,
                program_name TEXT,
                program_type TEXT,
                field_of_study TEXT,
                program_difficulty TEXT,
                duration_years REAL,
                typical_tuition_cad INTEGER,
                employment_rate_percent REAL,
                avg_starting_salary_cad INTEGER,
                accreditation_body TEXT,
                institution_type TEXT,
                university_name TEXT,
                requires_licensing TEXT,
                job_market_outlook TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loan_info (
                loan_id INTEGER PRIMARY KEY,
                payer_id INTEGER,
                program_id INTEGER,
                loan_amount REAL,
                interest_rate REAL,
                loan_term_years INTEGER,
                loan_term_months INTEGER,
                loan_type TEXT,
                institution_name TEXT,
                institution_city TEXT,
                institution_province TEXT,
                education_value REAL,
                down_payment REAL,
                ltv_ratio REAL,
                origination_date TEXT,
                disbursement_date TEXT,
                maturity_date TEXT,
                current_balance REAL,
                loan_status TEXT,
                lender TEXT,
                program_duration_years REAL,
                monthly_payment REAL,
                grace_period_months INTEGER,
                delinquency_risk REAL DEFAULT 0.0,
                FOREIGN KEY (payer_id) REFERENCES user_profile (payer_id),
                FOREIGN KEY (program_id) REFERENCES program_of_study (program_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loan_payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                payer_id INTEGER,
                due_date TEXT,
                paid_date TEXT,
                payment_due REAL,
                amount_paid REAL,
                principal_payment REAL,
                interest_payment REAL,
                escrow_payment REAL,
                late_fee REAL,
                total_amount_due REAL,
                remaining_balance REAL,
                status TEXT,
                days_late INTEGER,
                payment_method TEXT,
                payment_processor TEXT,
                transaction_id TEXT,
                confirmation_number TEXT,
                payment_type TEXT,
                FOREIGN KEY (payer_id) REFERENCES user_profile (payer_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = [dict(row) for row in rows]
        conn.close()
        
        return result
    
    def execute_insert(self, query: str, params: tuple = ()):
        """Execute an INSERT query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def execute_many(self, query: str, data: List[tuple]):
        """Execute multiple INSERT queries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.executemany(query, data)
        conn.commit()
        conn.close()
    
    def execute_update(self, query: str, params: tuple = ()):
        """Execute an UPDATE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return cursor.rowcount
    
    # ===========================================
    # DATABASE EXPLORATION QUERIES
    # ===========================================
    
    def get_table_names(self) -> List[str]:
        """Get all table names in the database"""
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        result = self.execute_query(query)
        return [row['name'] for row in result]
    
    def get_sample_user_profiles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample user profiles with different characteristics"""
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
        LIMIT ?
        """
        return self.execute_query(query, (limit,))
    
    def get_employment_income_analysis(self) -> List[Dict[str, Any]]:
        """Get employment and income analysis"""
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
        return self.execute_query(query)
    
    def get_province_analysis(self) -> List[Dict[str, Any]]:
        """Get province-wise analysis"""
        query = """
        SELECT 
            province,
            COUNT(*) as count,
            AVG(annual_income_cad) as avg_income,
            AVG(age) as avg_age
        FROM user_profile 
        GROUP BY province
        ORDER BY count DESC
        """
        return self.execute_query(query)
    
    def get_loan_amount_analysis(self) -> List[Dict[str, Any]]:
        """Get loan amount analysis"""
        query = """
        SELECT 
            loan_type,
            COUNT(*) as count,
            AVG(loan_amount) as avg_loan_amount,
            MIN(loan_amount) as min_loan_amount,
            MAX(loan_amount) as max_loan_amount,
            AVG(interest_rate) as avg_interest_rate
        FROM loan_info 
        GROUP BY loan_type
        ORDER BY avg_loan_amount DESC
        """
        return self.execute_query(query)
    
    def get_program_analysis(self) -> List[Dict[str, Any]]:
        """Get program of study analysis"""
        query = """
        SELECT 
            program_type,
            field_of_study,
            COUNT(*) as count,
            AVG(duration_years) as avg_duration
        FROM program_of_study 
        GROUP BY program_type, field_of_study
        ORDER BY count DESC
        """
        return self.execute_query(query)
    
    def get_payment_status_analysis(self) -> List[Dict[str, Any]]:
        """Get payment status analysis"""
        query = """
        SELECT 
            status,
            COUNT(*) as count,
            AVG(amount_paid) as avg_payment_amount,
            SUM(amount_paid) as total_payment_amount
        FROM loan_payments 
        GROUP BY status
        ORDER BY count DESC
        """
        return self.execute_query(query)
    
    def get_payment_trends_analysis(self) -> List[Dict[str, Any]]:
        """Get payment trends analysis"""
        query = """
        SELECT 
            DATE(paid_date) as payment_date,
            COUNT(*) as transaction_count,
            SUM(amount_paid) as total_payments,
            AVG(amount_paid) as avg_payment
        FROM loan_payments 
        GROUP BY DATE(paid_date)
        ORDER BY payment_date
        """
        return self.execute_query(query)
    
    # ===========================================
    # COMPREHENSIVE DATA ANALYSIS QUERIES
    # ===========================================
    
    def get_comprehensive_loan_data(self) -> List[Dict[str, Any]]:
        """Get comprehensive loan data joining all tables for campaign analysis"""
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
            pos.field_of_study,
            pos.program_type,
            pos.program_difficulty,
            pos.duration_years as program_duration_years,
            pos.employment_rate_percent as graduation_rate,
            pos.employment_rate_percent,
            pos.avg_starting_salary_cad as average_starting_salary,
            
            -- Payment Information (aggregated)
            COALESCE(payment_stats.total_payments, 0) as total_payments_made,
            COALESCE(payment_stats.avg_payment_amount, 0) as avg_payment_amount,
            COALESCE(payment_stats.late_payments, 0) as late_payment_count,
            COALESCE(payment_stats.missed_payments, 0) as missed_payment_count,
            COALESCE(payment_stats.last_payment_date, 'Never') as last_payment_date
            
        FROM user_profile up
        LEFT JOIN loan_info li ON up.payer_id = li.payer_id
        LEFT JOIN program_of_study pos ON li.program_id = pos.program_id
        LEFT JOIN (
            SELECT 
                lp.payer_id,
                COUNT(*) as total_payments,
                AVG(lp.amount_paid) as avg_payment_amount,
                SUM(CASE WHEN lp.status = 'Late' THEN 1 ELSE 0 END) as late_payments,
                SUM(CASE WHEN lp.status = 'Missed' THEN 1 ELSE 0 END) as missed_payments,
                MAX(lp.paid_date) as last_payment_date
            FROM loan_payments lp
            GROUP BY lp.payer_id
        ) payment_stats ON li.payer_id = payment_stats.payer_id
        
        WHERE li.loan_id IS NOT NULL
        ORDER BY up.payer_id
        """
        return self.execute_query(query)
    
    def get_delinquency_analysis_data(self) -> List[Dict[str, Any]]:
        """Get comprehensive data for delinquency analysis and ML modeling"""
        query = """
        SELECT 
            -- User Profile Features
            up.payer_id,
            up.age,
            up.annual_income_cad,
            up.employment_status,
            up.marital_status,
            up.city,
            up.province,
            
            -- Loan Info Features  
            li.loan_amount,
            li.interest_rate,
            li.loan_term_years,
            li.loan_term_months,
            li.loan_type,
            li.institution_name,
            li.institution_city,
            li.institution_province,
            li.education_value,
            li.down_payment,
            li.ltv_ratio,
            li.origination_date,
            li.disbursement_date,
            li.maturity_date,
            li.current_balance,
            li.loan_status,
            li.lender,
            li.program_duration_years,
            li.monthly_payment,
            li.grace_period_months,
            
            -- Program of Study Features
            pos.program_name,
            pos.program_type,
            pos.field_of_study,
            pos.program_difficulty,
            pos.duration_years as pos_duration,
            pos.employment_rate_percent as employment_rate,
            pos.avg_starting_salary_cad as average_starting_salary,
            pos.typical_tuition_cad,
            pos.job_market_outlook,
            
            -- Payment Behavior Features (Aggregated)
            COALESCE(payment_agg.total_payments, 0) as total_payments_made,
            COALESCE(payment_agg.total_amount_paid, 0) as total_amount_paid,
            COALESCE(payment_agg.avg_payment_amount, 0) as avg_payment_amount,
            COALESCE(payment_agg.on_time_payments, 0) as on_time_payments,
            COALESCE(payment_agg.late_payments, 0) as late_payments,
            COALESCE(payment_agg.missed_payments, 0) as missed_payments,
            COALESCE(payment_agg.days_since_last_payment, 9999) as days_since_last_payment,
            COALESCE(payment_agg.payment_consistency, 0) as payment_consistency,
            COALESCE(payment_agg.early_payments, 0) as early_payments,
            
            -- Delinquency Target Variable (More realistic classification)
            CASE 
                WHEN COALESCE(payment_agg.missed_payments, 0) > 2 OR 
                     COALESCE(payment_agg.late_payments, 0) > 5 OR
                     (COALESCE(payment_agg.late_payments, 0) + COALESCE(payment_agg.missed_payments, 0)) > 6 OR
                     COALESCE(payment_agg.payment_consistency, 100) < 75
                THEN 1 
                ELSE 0 
            END as is_delinquent
            
        FROM user_profile up
        JOIN loan_info li ON up.payer_id = li.payer_id
        LEFT JOIN program_of_study pos ON li.program_id = pos.program_id
        LEFT JOIN (
            SELECT 
                payer_id,
                COUNT(*) as total_payments,
                SUM(amount_paid) as total_amount_paid,
                AVG(amount_paid) as avg_payment_amount,
                SUM(CASE WHEN status = 'Paid' AND COALESCE(days_late, 0) = 0 THEN 1 ELSE 0 END) as on_time_payments,
                SUM(CASE WHEN status = 'Late' OR COALESCE(days_late, 0) > 0 THEN 1 ELSE 0 END) as late_payments,
                SUM(CASE WHEN status = 'Missed' THEN 1 ELSE 0 END) as missed_payments,
                SUM(CASE WHEN status = 'Early' THEN 1 ELSE 0 END) as early_payments,
                JULIANDAY('now') - JULIANDAY(MAX(paid_date)) as days_since_last_payment,
                (CAST(SUM(CASE WHEN status = 'Paid' AND COALESCE(days_late, 0) = 0 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100 as payment_consistency
            FROM loan_payments 
            GROUP BY payer_id
        ) payment_agg ON up.payer_id = payment_agg.payer_id
        
        WHERE li.loan_id IS NOT NULL
        ORDER BY up.payer_id
        """
        return self.execute_query(query)
    
    # ===========================================
    # DELINQUENCY RISK UPDATE METHODS
    # ===========================================
    
    def update_delinquency_risk(self, payer_id: str, risk_score: float) -> int:
        """Update delinquency risk for a specific payer"""
        query = "UPDATE loan_info SET delinquency_risk = ? WHERE payer_id = ?"
        return self.execute_update(query, (risk_score, payer_id))
    
    def batch_update_delinquency_risks(self, risk_scores: Dict[str, float]) -> int:
        """Batch update delinquency risks for multiple payers"""
        query = "UPDATE loan_info SET delinquency_risk = ? WHERE payer_id = ?"
        data = [(score, payer_id) for payer_id, score in risk_scores.items()]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, data)
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rowcount
    
    def get_delinquency_risk_count(self) -> int:
        """Get count of loans with calculated delinquency risk"""
        query = "SELECT COUNT(*) as count FROM loan_info WHERE delinquency_risk IS NOT NULL"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0
    
    def get_delinquency_risk_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of delinquency risk scores"""
        query = """
        SELECT 
            delinquency_risk, 
            COUNT(*) as count 
        FROM loan_info 
        GROUP BY delinquency_risk 
        ORDER BY delinquency_risk
        """
        return self.execute_query(query)