import sqlite3
import pandas as pd

def verify_education_loan_system():
    """Verify that program difficulty correlation with delinquency is working correctly."""
    
    conn = sqlite3.connect('student_loan_data.db')
    
    # Check program difficulty distribution
    print('Program Difficulty Distribution:')
    difficulty_query = '''
    SELECT program_difficulty, COUNT(*) as count 
    FROM program_of_study 
    GROUP BY program_difficulty 
    ORDER BY program_difficulty
    '''
    df_difficulty = pd.read_sql_query(difficulty_query, conn)
    for _, row in df_difficulty.iterrows():
        print(f'  Difficulty Level {row["program_difficulty"]}: {row["count"]} programs')
    
    # Check delinquency by program difficulty
    print('\nDelinquency Analysis by Program Difficulty:')
    delinquency_query = '''
    SELECT 
        pos.program_difficulty,
        COUNT(DISTINCT up.payer_id) as total_users,
        COUNT(DISTINCT CASE WHEN mp.status = "Missed" THEN up.payer_id END) as delinquent_users
    FROM user_profile up
    JOIN loan_info lr ON up.payer_id = lr.payer_id
    JOIN program_of_study pos ON lr.program_id = pos.program_id
    LEFT JOIN loan_payments mp ON up.payer_id = mp.payer_id AND mp.status = "Missed"
    GROUP BY pos.program_difficulty
    ORDER BY pos.program_difficulty
    '''
    df_delinquency = pd.read_sql_query(delinquency_query, conn)
    
    for _, row in df_delinquency.iterrows():
        total = row['total_users']
        delinquent = row['delinquent_users'] if row['delinquent_users'] else 0
        rate = (delinquent / total * 100) if total > 0 else 0
        difficulty = row['program_difficulty']
        risk_level = ["Low Risk", "Moderate Risk", "High Risk"][difficulty-1]
        print(f'  Difficulty {difficulty} ({risk_level}): {delinquent}/{total} users delinquent ({rate:.1f}%)')
    
    # Show sample users and their programs
    print('\nSample User Program Assignments:')
    sample_query = '''
    SELECT 
        up.payer_id,
        up.first_name || ' ' || up.last_name as full_name,
        pos.program_difficulty,
        pos.program_name,
        pos.field_of_study,
        lr.loan_amount,
        CASE WHEN mp.payer_id IS NOT NULL THEN "Yes" ELSE "No" END as has_missed_payments
    FROM user_profile up
    JOIN loan_info lr ON up.payer_id = lr.payer_id
    JOIN program_of_study pos ON lr.program_id = pos.program_id
    LEFT JOIN (
        SELECT DISTINCT payer_id
        FROM loan_payments 
        WHERE status = "Missed"
    ) mp ON up.payer_id = mp.payer_id
    ORDER BY pos.program_difficulty DESC, up.payer_id
    LIMIT 15
    '''
    df_sample = pd.read_sql_query(sample_query, conn)
    print(df_sample.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    verify_education_loan_system()