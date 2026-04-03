import pandas as pd
import sqlite3
import random
from datetime import datetime, date

def generate_user_profile(num_payers):
    """
    Generates synthetic user profiles for payer IDs.
    Returns a pandas DataFrame with user profile data.
    """
    
    # Lists of English-sounding names
    first_names_male = [
        "James", "John", "Robert", "Michael", "David", "William", "Richard", "Joseph", 
        "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark", 
        "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian",
        "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob",
        "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott",
        "Brandon", "Benjamin", "Samuel", "Gregory", "Alexander", "Frank", "Raymond"
    ]
    
    first_names_female = [
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", 
        "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Helen", "Sandra",
        "Donna", "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Sarah", "Kimberly",
        "Deborah", "Dorothy", "Lisa", "Nancy", "Karen", "Betty", "Helen", "Sandra",
        "Donna", "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Emily", "Ashley",
        "Amanda", "Stephanie", "Melissa", "Nicole", "Jessica", "Elizabeth", "Rebecca",
        "Kelly", "Christina", "Rachel", "Lauren", "Amy", "Catherine", "Frances"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
        "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
        "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey"
    ]
    
    # Canadian provinces and cities (5 provinces, 20 cities total)
    cities_provinces = [
        # Ontario (6 cities)
        ("Toronto", "Ontario"), ("Ottawa", "Ontario"), ("Hamilton", "Ontario"),
        ("London", "Ontario"), ("Mississauga", "Ontario"), ("Brampton", "Ontario"),
        
        # British Columbia (4 cities)
        ("Vancouver", "British Columbia"), ("Victoria", "British Columbia"),
        ("Burnaby", "British Columbia"), ("Surrey", "British Columbia"),
        
        # Alberta (4 cities)
        ("Calgary", "Alberta"), ("Edmonton", "Alberta"), 
        ("Red Deer", "Alberta"), ("Lethbridge", "Alberta"),
        
        # Quebec (3 cities)
        ("Montreal", "Quebec"), ("Quebec City", "Quebec"), ("Laval", "Quebec"),
        
        # Manitoba (3 cities)
        ("Winnipeg", "Manitoba"), ("Brandon", "Manitoba"), ("Steinbach", "Manitoba")
    ]
    
    # Employment statuses
    employment_statuses = ["Unemployed", "Part-time", "Full-time"]
    
    # Marital statuses
    marital_statuses = ["Single", "Married", "Divorced", "Widowed", "Common-law"]
    
    # Street names for addresses
    street_names = [
        "Main St", "First Ave", "Second Ave", "Park Ave", "Oak St", "Maple Ave",
        "Elm St", "Pine St", "Cedar Ave", "King St", "Queen St", "Church St",
        "Mill St", "Water St", "High St", "School St", "Spring St", "Washington Ave",
        "Franklin St", "Clinton St", "Madison Ave", "Jefferson St", "Lincoln Ave",
        "Jackson St", "Adams St", "Wilson Ave", "Johnson St", "Smith St"
    ]
    
    profiles = []
    current_year = datetime.now().year
    
    for payer_id in range(1, num_payers + 1):
        # Generate random gender for name selection
        is_male = random.choice([True, False])
        first_name = random.choice(first_names_male if is_male else first_names_female)
        last_name = random.choice(last_names)
        
        # Generate date of birth (ages 18-44)
        age = random.randint(18, 44)
        birth_year = current_year - age
        birth_month = random.randint(1, 12)
        # Ensure valid day for the month
        if birth_month in [1, 3, 5, 7, 8, 10, 12]:
            max_day = 31
        elif birth_month in [4, 6, 9, 11]:
            max_day = 30
        else:  # February
            # Simple leap year check
            if birth_year % 4 == 0 and (birth_year % 100 != 0 or birth_year % 400 == 0):
                max_day = 29
            else:
                max_day = 28
        birth_day = random.randint(1, max_day)
        date_of_birth = date(birth_year, birth_month, birth_day)
        
        # Generate address
        house_number = random.randint(1, 9999)
        street_name = random.choice(street_names)
        city, province = random.choice(cities_provinces)
        # Canadian postal code format: A1A 1A1
        postal_code = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(0,9)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')} {random.randint(0,9)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(0,9)}"
        address = f"{house_number} {street_name}, {city}, {province} {postal_code}"
        
        # Generate employment status and corresponding income
        employment_status = random.choice(employment_statuses)
        
        if employment_status == "Unemployed":
            annual_income = 0
        elif employment_status == "Part-time":
            annual_income = random.randint(15000, 25000)
        else:  # Full-time
            annual_income = random.randint(40000, 75000)
        
        # Generate marital status
        marital_status = random.choice(marital_statuses)
        
        profiles.append({
            'payer_id': payer_id,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
            'age': age,
            'address': address,
            'city': city,
            'province': province,
            'employment_status': employment_status,
            'annual_income_cad': annual_income,
            'marital_status': marital_status
        })
    
    return pd.DataFrame(profiles)

def save_profiles_to_sqlite(df, db_path):
    """
    Save user profiles to SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the user_profile table
    cursor.execute('''
    CREATE TABLE user_profile (
        payer_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        age INTEGER NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        province TEXT NOT NULL,
        employment_status TEXT NOT NULL,
        annual_income_cad INTEGER NOT NULL,
        marital_status TEXT NOT NULL
    )
    ''')
    
    # Insert data
    df.to_sql('user_profile', conn, if_exists='append', index=False)
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX idx_payer_id ON user_profile(payer_id)')
    cursor.execute('CREATE INDEX idx_city_province ON user_profile(city, province)')
    cursor.execute('CREATE INDEX idx_employment ON user_profile(employment_status)')
    
    conn.commit()
    conn.close()

# This module can be imported and used by run_data_generation.py
# No command line interface - use run_data_generation.py as the main entry point