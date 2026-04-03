import pandas as pd
import sqlite3
import random

def generate_programs_of_study():
    """
    Generates synthetic education program data with difficulty correlation to delinquency risk.
    Returns a pandas DataFrame with program records.
    """
    
    # Define program categories with realistic data
    programs = [
        # Difficulty Level 1 (Easiest - Lower Delinquency Risk)
        {"name": "Business Administration", "type": "Bachelor's", "field": "Business", "difficulty": 1, "duration": 4, "tuition": 35000, "employment_rate": 88, "avg_salary": 55000},
        {"name": "Marketing", "type": "Bachelor's", "field": "Business", "difficulty": 1, "duration": 4, "tuition": 32000, "employment_rate": 85, "avg_salary": 48000},
        {"name": "Human Resources", "type": "Bachelor's", "field": "Business", "difficulty": 1, "duration": 4, "tuition": 30000, "employment_rate": 82, "avg_salary": 52000},
        {"name": "Communications", "type": "Bachelor's", "field": "Liberal Arts", "difficulty": 1, "duration": 4, "tuition": 28000, "employment_rate": 75, "avg_salary": 42000},
        {"name": "General Studies", "type": "Bachelor's", "field": "Liberal Arts", "difficulty": 1, "duration": 4, "tuition": 25000, "employment_rate": 70, "avg_salary": 38000},
        {"name": "Early Childhood Education", "type": "Bachelor's", "field": "Education", "difficulty": 1, "duration": 4, "tuition": 27000, "employment_rate": 80, "avg_salary": 45000},
        {"name": "Hospitality Management", "type": "Bachelor's", "field": "Business", "difficulty": 1, "duration": 4, "tuition": 29000, "employment_rate": 78, "avg_salary": 44000},
        {"name": "Sports Management", "type": "Bachelor's", "field": "Business", "difficulty": 1, "duration": 4, "tuition": 31000, "employment_rate": 73, "avg_salary": 41000},
        
        # Difficulty Level 2 (Moderate - Moderate Delinquency Risk)
        {"name": "Computer Science", "type": "Bachelor's", "field": "Technology", "difficulty": 2, "duration": 4, "tuition": 45000, "employment_rate": 92, "avg_salary": 75000},
        {"name": "Nursing", "type": "Bachelor's", "field": "Healthcare", "difficulty": 2, "duration": 4, "tuition": 40000, "employment_rate": 95, "avg_salary": 68000},
        {"name": "Accounting", "type": "Bachelor's", "field": "Business", "difficulty": 2, "duration": 4, "tuition": 36000, "employment_rate": 87, "avg_salary": 58000},
        {"name": "Psychology", "type": "Bachelor's", "field": "Social Sciences", "difficulty": 2, "duration": 4, "tuition": 33000, "employment_rate": 76, "avg_salary": 46000},
        {"name": "Information Technology", "type": "Bachelor's", "field": "Technology", "difficulty": 2, "duration": 4, "tuition": 42000, "employment_rate": 89, "avg_salary": 65000},
        {"name": "Criminal Justice", "type": "Bachelor's", "field": "Social Sciences", "difficulty": 2, "duration": 4, "tuition": 31000, "employment_rate": 79, "avg_salary": 48000},
        {"name": "Social Work", "type": "Bachelor's", "field": "Social Sciences", "difficulty": 2, "duration": 4, "tuition": 29000, "employment_rate": 81, "avg_salary": 47000},
        {"name": "Elementary Education", "type": "Bachelor's", "field": "Education", "difficulty": 2, "duration": 4, "tuition": 28000, "employment_rate": 84, "avg_salary": 50000},
        
        # Difficulty Level 3 (Hardest - Higher Delinquency Risk)
        {"name": "Biomedical Engineering", "type": "Bachelor's", "field": "Engineering", "difficulty": 3, "duration": 4, "tuition": 55000, "employment_rate": 85, "avg_salary": 70000},
        {"name": "Aerospace Engineering", "type": "Bachelor's", "field": "Engineering", "difficulty": 3, "duration": 4, "tuition": 52000, "employment_rate": 82, "avg_salary": 72000},
        {"name": "Chemical Engineering", "type": "Bachelor's", "field": "Engineering", "difficulty": 3, "duration": 4, "tuition": 50000, "employment_rate": 86, "avg_salary": 74000},
        {"name": "Electrical Engineering", "type": "Bachelor's", "field": "Engineering", "difficulty": 3, "duration": 4, "tuition": 48000, "employment_rate": 88, "avg_salary": 73000},
        {"name": "Mechanical Engineering", "type": "Bachelor's", "field": "Engineering", "difficulty": 3, "duration": 4, "tuition": 47000, "employment_rate": 87, "avg_salary": 71000},
        {"name": "Physics", "type": "Bachelor's", "field": "Science", "difficulty": 3, "duration": 4, "tuition": 44000, "employment_rate": 72, "avg_salary": 55000},
        {"name": "Mathematics", "type": "Bachelor's", "field": "Science", "difficulty": 3, "duration": 4, "tuition": 42000, "employment_rate": 74, "avg_salary": 58000},
        {"name": "Chemistry", "type": "Bachelor's", "field": "Science", "difficulty": 3, "duration": 4, "tuition": 43000, "employment_rate": 75, "avg_salary": 56000},
        {"name": "Architecture", "type": "Bachelor's", "field": "Design", "difficulty": 3, "duration": 5, "tuition": 49000, "employment_rate": 70, "avg_salary": 62000},
        {"name": "Pre-Medicine", "type": "Bachelor's", "field": "Science", "difficulty": 3, "duration": 4, "tuition": 50000, "employment_rate": 65, "avg_salary": 45000},  # Lower initially, higher after med school
        
        # Graduate Programs
        {"name": "Master of Business Administration", "type": "Master's", "field": "Business", "difficulty": 2, "duration": 2, "tuition": 65000, "employment_rate": 94, "avg_salary": 95000},
        {"name": "Master of Science in Engineering", "type": "Master's", "field": "Engineering", "difficulty": 3, "duration": 2, "tuition": 55000, "employment_rate": 91, "avg_salary": 85000},
        {"name": "Master of Education", "type": "Master's", "field": "Education", "difficulty": 2, "duration": 2, "tuition": 35000, "employment_rate": 89, "avg_salary": 62000},
        {"name": "Master of Social Work", "type": "Master's", "field": "Social Sciences", "difficulty": 2, "duration": 2, "tuition": 40000, "employment_rate": 86, "avg_salary": 58000},
        {"name": "Juris Doctor (Law)", "type": "Professional", "field": "Law", "difficulty": 3, "duration": 3, "tuition": 75000, "employment_rate": 79, "avg_salary": 78000},
        {"name": "Doctor of Medicine", "type": "Professional", "field": "Medicine", "difficulty": 3, "duration": 4, "tuition": 85000, "employment_rate": 96, "avg_salary": 120000},
        {"name": "Doctor of Pharmacy", "type": "Professional", "field": "Healthcare", "difficulty": 3, "duration": 4, "tuition": 70000, "employment_rate": 93, "avg_salary": 95000},
        
        # Technical/Vocational Programs
        {"name": "Automotive Technology", "type": "Certificate", "field": "Technical", "difficulty": 1, "duration": 2, "tuition": 18000, "employment_rate": 85, "avg_salary": 45000},
        {"name": "HVAC Technology", "type": "Certificate", "field": "Technical", "difficulty": 1, "duration": 2, "tuition": 16000, "employment_rate": 88, "avg_salary": 48000},
        {"name": "Network Administration", "type": "Certificate", "field": "Technology", "difficulty": 2, "duration": 2, "tuition": 22000, "employment_rate": 82, "avg_salary": 52000},
        {"name": "Dental Hygiene", "type": "Associate", "field": "Healthcare", "difficulty": 2, "duration": 2, "tuition": 35000, "employment_rate": 91, "avg_salary": 62000},
        {"name": "Medical Assistant", "type": "Certificate", "field": "Healthcare", "difficulty": 1, "duration": 1, "tuition": 15000, "employment_rate": 86, "avg_salary": 38000},
    ]
    
    # Institution types and accreditation bodies
    institution_types = ["University", "College", "Technical School", "Community College", "Professional School"]
    accreditation_bodies = [
        "Association of Universities and Colleges of Canada", 
        "Canadian Council on Learning", 
        "Professional Engineers Ontario",
        "Canadian Association of University Teachers",
        "Canadian Medical Association",
        "Law Society of Ontario",
        "Canadian Nursing Association",
        "Canadian Council of Professional Engineers"
    ]
    
    # Top 6 universities in Canada
    top_universities = [
        "University of Toronto",
        "University of British Columbia (UBC)", 
        "McGill University",
        "University of Alberta",
        "McMaster University",
        "University of Waterloo"
    ]
    
    program_records = []
    
    for i, program in enumerate(programs, 1):
        # Add some variation to the base data
        tuition_variation = random.uniform(0.9, 1.1)  # ±10% variation
        salary_variation = random.uniform(0.95, 1.05)  # ±5% variation 
        employment_variation = random.uniform(0.95, 1.05)  # ±5% variation
        
        # Select appropriate institution type based on program type
        if program["type"] in ["Professional", "Master's"]:
            institution_type = random.choice(["University", "Professional School"])
        elif program["type"] == "Certificate":
            institution_type = random.choice(["Technical School", "Community College"])
        elif program["type"] == "Associate":
            institution_type = random.choice(["College", "Community College"])
        else:
            institution_type = random.choice(["University", "College"])
        
        # Select university name based on program characteristics
        if institution_type == "University":
            # Assign universities based on program field and difficulty
            if program["field"] == "Medicine":
                university_name = random.choice(["University of Toronto", "McGill University", "University of British Columbia (UBC)"])
            elif program["field"] == "Engineering":
                university_name = random.choice(["University of Waterloo", "University of Toronto", "University of British Columbia (UBC)"])
            elif program["field"] == "Law":
                university_name = random.choice(["University of Toronto", "McGill University", "University of British Columbia (UBC)"])
            elif program["difficulty"] == 3:  # High difficulty programs
                university_name = random.choice(["University of Toronto", "McGill University", "University of British Columbia (UBC)"])
            else:
                university_name = random.choice(top_universities)
        else:
            # Non-university institutions get a generic institution name
            university_name = f"{random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central', 'Metropolitan'])} {institution_type}"
        
        program_records.append({
            'program_id': i,
            'program_name': program["name"],
            'program_type': program["type"],
            'field_of_study': program["field"],
            'program_difficulty': program["difficulty"],
            'duration_years': program["duration"],
            'typical_tuition_cad': round(program["tuition"] * tuition_variation, 2),
            'employment_rate_percent': round(min(100, program["employment_rate"] * employment_variation), 1),
            'avg_starting_salary_cad': round(program["avg_salary"] * salary_variation, 2),
            'accreditation_body': random.choice(accreditation_bodies),
            'institution_type': institution_type,
            'university_name': university_name,
            'requires_licensing': program["field"] in ["Medicine", "Law", "Engineering", "Healthcare"],
            'job_market_outlook': random.choice(["Excellent", "Good", "Fair", "Challenging"])
        })
    
    return pd.DataFrame(program_records)

def save_programs_to_sqlite(df, db_path):
    """
    Save program of study records to SQLite database.
    Check if table exists and only purge data if it does, otherwise create table.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute('''
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='program_of_study'
    ''')
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        # Table exists, drop it and recreate with new schema
        cursor.execute('DROP TABLE program_of_study')
        print("  Existing program_of_study table found, dropped for schema update")
        table_exists = False  # Treat as new table creation
    
    if not table_exists:
        # Table doesn't exist, create it
        cursor.execute('''
        CREATE TABLE program_of_study (
            program_id INTEGER PRIMARY KEY,
            program_name TEXT NOT NULL,
            program_type TEXT NOT NULL,
            field_of_study TEXT NOT NULL,
            program_difficulty INTEGER NOT NULL CHECK (program_difficulty BETWEEN 1 AND 3),
            duration_years REAL NOT NULL,
            typical_tuition_cad REAL NOT NULL,
            employment_rate_percent REAL NOT NULL,
            avg_starting_salary_cad REAL NOT NULL,
            accreditation_body TEXT NOT NULL,
            institution_type TEXT NOT NULL,
            university_name TEXT NOT NULL,
            requires_licensing BOOLEAN NOT NULL,
            job_market_outlook TEXT NOT NULL
        )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX idx_program_difficulty ON program_of_study(program_difficulty)')
        cursor.execute('CREATE INDEX idx_field_of_study ON program_of_study(field_of_study)')
        cursor.execute('CREATE INDEX idx_program_type ON program_of_study(program_type)')
        cursor.execute('CREATE INDEX idx_institution_type ON program_of_study(institution_type)')
        cursor.execute('CREATE INDEX idx_university_name ON program_of_study(university_name)')
        print("  New program_of_study table created with indexes")
    
    # Insert data
    df.to_sql('program_of_study', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()

def generate_program_statistics(df):
    """
    Generate and display statistics about the program data.
    """
    total_programs = len(df)
    
    # Difficulty distribution
    difficulty_counts = df['program_difficulty'].value_counts().sort_index()
    
    # Field distribution
    field_counts = df['field_of_study'].value_counts()
    
    # Program type distribution
    type_counts = df['program_type'].value_counts()
    
    print(f"\\nProgram of Study Statistics:")
    print(f"  Total programs: {total_programs}")
    
    print(f"\\nDifficulty Level Distribution:")
    for difficulty, count in difficulty_counts.items():
        percentage = (count / total_programs) * 100
        risk_level = ["Low Risk", "Moderate Risk", "High Risk"][difficulty-1]
        print(f"  Level {difficulty} ({risk_level}): {count} programs ({percentage:.1f}%)")
    
    print(f"\\nTop Fields of Study:")
    for field, count in field_counts.head().items():
        percentage = (count / total_programs) * 100
        print(f"  {field}: {count} programs ({percentage:.1f}%)")
    
    print(f"\\nProgram Types:")
    for prog_type, count in type_counts.items():
        percentage = (count / total_programs) * 100
        print(f"  {prog_type}: {count} programs ({percentage:.1f}%)")
    
    return {
        'total_programs': total_programs,
        'difficulty_counts': difficulty_counts,
        'field_counts': field_counts,
        'type_counts': type_counts
    }

# This module can be imported and used by run_data_generation.py
# No command line interface - use run_data_generation.py as the main entry point\n    \n    return {\n        'total_programs': total_programs,\n        'difficulty_counts': difficulty_counts,\n        'field_counts': field_counts,\n        'type_counts': type_counts\n    }\n\n# This module can be imported and used by generate_data.py\n# No command line interface - use generate_data.py as the main entry point