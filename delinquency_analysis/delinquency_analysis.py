import pandas as pd
import numpy as np
import sqlite3
import argparse
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

def load_comprehensive_dataset(db_path="student_loan_data.db"):
    """
    Load and merge all tables for comprehensive delinquency analysis.
    Returns a DataFrame with all relevant features and target variable.
    """
    conn = sqlite3.connect(db_path)
    
    # Comprehensive query joining all 4 tables
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
        pos.duration_years,
        pos.typical_tuition_cad,
        pos.employment_rate_percent,
        pos.avg_starting_salary_cad,
        pos.accreditation_body,
        pos.institution_type,
        pos.university_name,
        pos.requires_licensing,
        pos.job_market_outlook,
        
        -- Payment Behavior Features (Aggregated)
        COUNT(lp.payer_id) as total_payments_made,
        SUM(CASE WHEN lp.status = 'Missed' THEN 1 ELSE 0 END) as missed_payments,
        SUM(CASE WHEN lp.status = 'Paid' THEN 1 ELSE 0 END) as successful_payments,
        AVG(lp.days_late) as avg_days_late,
        SUM(lp.late_fee) as total_late_fees,
        AVG(lp.amount_paid) as avg_payment_amount,
        MAX(lp.days_late) as max_days_late,
        
        -- Delinquency Target Variable
        CASE 
            WHEN SUM(CASE WHEN lp.status = 'Missed' THEN 1 ELSE 0 END) > 0 THEN 1 
            ELSE 0 
        END as is_delinquent
        
    FROM user_profile up
    JOIN loan_info li ON up.payer_id = li.payer_id
    JOIN program_of_study pos ON li.program_id = pos.program_id
    LEFT JOIN loan_payments lp ON up.payer_id = lp.payer_id
    GROUP BY up.payer_id
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"Loaded dataset with {len(df)} records and {len(df.columns)} features")
    print(f"Delinquency rate: {df['is_delinquent'].mean():.2%}")
    
    return df

def engineer_features(df):
    """
    Engineer additional features for better delinquency prediction.
    """
    # Date-based features
    df['origination_date'] = pd.to_datetime(df['origination_date'])
    df['disbursement_date'] = pd.to_datetime(df['disbursement_date'])
    df['maturity_date'] = pd.to_datetime(df['maturity_date'])
    
    current_date = pd.Timestamp.now()
    
    # Time-based features
    df['loan_age_days'] = (current_date - df['origination_date']).dt.days
    df['days_since_disbursement'] = (current_date - df['disbursement_date']).dt.days
    df['days_to_maturity'] = (df['maturity_date'] - current_date).dt.days
    df['loan_progress_pct'] = df['loan_age_days'] / (df['loan_term_years'] * 365)
    
    # Financial ratios
    df['debt_to_income_ratio'] = df['loan_amount'] / np.maximum(df['annual_income_cad'], 1)
    df['payment_to_income_ratio'] = (df['monthly_payment'] * 12) / np.maximum(df['annual_income_cad'], 1)
    df['education_roi'] = df['avg_starting_salary_cad'] / np.maximum(df['typical_tuition_cad'], 1)
    df['loan_to_education_value_ratio'] = df['loan_amount'] / df['education_value']
    
    # Payment behavior features
    df['delinquency_rate'] = df['missed_payments'] / np.maximum(df['total_payments_made'], 1)
    df['payment_consistency'] = df['successful_payments'] / np.maximum(df['total_payments_made'], 1)
    df['avg_late_fee_per_payment'] = df['total_late_fees'] / np.maximum(df['total_payments_made'], 1)
    
    # Risk category features
    df['high_ltv_risk'] = (df['ltv_ratio'] > 80).astype(int)
    df['low_income_risk'] = (df['annual_income_cad'] < 40000).astype(int)
    df['young_borrower_risk'] = (df['age'] < 26).astype(int)
    df['long_term_loan_risk'] = (df['loan_term_years'] > 15).astype(int)
    df['high_difficulty_program'] = (df['program_difficulty'] == 3).astype(int)
    
    # Employment market features
    df['low_employment_rate'] = (df['employment_rate_percent'] < 80).astype(int)
    df['poor_job_outlook'] = (df['job_market_outlook'] == 'Challenging').astype(int)
    
    print(f"Feature engineering complete. Dataset now has {len(df.columns)} features")
    
    return df

def prepare_ml_features(df):
    """
    Prepare features for machine learning by encoding categorical variables.
    """
    # Create a copy for ML processing
    ml_df = df.copy()
    
    # Categorical features to encode
    categorical_features = [
        'employment_status', 'marital_status', 'province', 'loan_type', 
        'institution_province', 'lender', 'program_type', 'field_of_study',
        'accreditation_body', 'institution_type', 'university_name', 
        'requires_licensing', 'job_market_outlook', 'loan_status'
    ]
    
    # Label encoding for categorical features
    label_encoders = {}
    for feature in categorical_features:
        if feature in ml_df.columns:
            le = LabelEncoder()
            ml_df[feature + '_encoded'] = le.fit_transform(ml_df[feature].fillna('Unknown'))
            label_encoders[feature] = le
    
    # Select numerical and encoded features for ML
    feature_columns = [col for col in ml_df.columns if 
                      (ml_df[col].dtype in ['int64', 'float64'] and 
                       col not in ['payer_id', 'is_delinquent']) or 
                      col.endswith('_encoded')]
    
    # Handle missing values
    ml_df[feature_columns] = ml_df[feature_columns].fillna(ml_df[feature_columns].mean())
    
    # Remove infinite values
    ml_df[feature_columns] = ml_df[feature_columns].replace([np.inf, -np.inf], np.nan)
    ml_df[feature_columns] = ml_df[feature_columns].fillna(ml_df[feature_columns].mean())
    
    X = ml_df[feature_columns]
    y = ml_df['is_delinquent']
    
    print(f"ML dataset prepared with {X.shape[1]} features for {X.shape[0]} samples")
    print(f"Feature list: {X.columns.tolist()}")
    
    return X, y, feature_columns, label_encoders

def train_delinquency_models(X, y):
    """
    Train multiple ML models and select the best performer.
    """
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=6, random_state=42),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
    }
    
    # Train and evaluate models
    model_results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        auc_score = roc_auc_score(y_test, y_pred_proba)
        cv_scores = cross_val_score(model, X_train_scaled if name == 'Logistic Regression' else X_train, 
                                   y_train, cv=5, scoring='roc_auc')
        
        model_results[name] = {
            'model': model,
            'auc_score': auc_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'predictions': y_pred_proba
        }
        
        print(f"AUC Score: {auc_score:.4f}")
        print(f"Cross-validation AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred))
    
    # Select best model
    best_model_name = max(model_results.keys(), key=lambda x: model_results[x]['auc_score'])
    best_model = model_results[best_model_name]['model']
    
    print(f"\nBest performing model: {best_model_name}")
    
    return best_model, model_results, scaler

def analyze_feature_importance(model, feature_columns, model_name):
    """
    Analyze and display feature importance from the trained model.
    """
    print(f"\n{'='*60}")
    print(f"FEATURE IMPORTANCE ANALYSIS - {model_name}")
    print(f"{'='*60}")
    
    if hasattr(model, 'feature_importances_'):
        # Tree-based models
        importance_scores = model.feature_importances_
    elif hasattr(model, 'coef_'):
        # Linear models
        importance_scores = np.abs(model.coef_[0])
    else:
        print("Model does not support feature importance analysis")
        return None
    
    # Create feature importance DataFrame
    feature_importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': importance_scores
    }).sort_values('importance', ascending=False)
    
    print("\nTop 20 Most Influential Features for Delinquency Prediction:")
    print("-" * 70)
    
    for i, (idx, row) in enumerate(feature_importance_df.head(20).iterrows()):
        print(f"{i+1:2d}. {row['feature']:<40} {row['importance']:.4f}")
    
    # Categorize features by table source
    user_features = [f for f in feature_importance_df['feature'] if any(
        prefix in f.lower() for prefix in ['age', 'income', 'employment', 'marital', 'province'])]
    loan_features = [f for f in feature_importance_df['feature'] if any(
        prefix in f.lower() for prefix in ['loan_', 'interest', 'ltv', 'balance', 'payment', 'debt_to'])]
    program_features = [f for f in feature_importance_df['feature'] if any(
        prefix in f.lower() for prefix in ['program_', 'difficulty', 'tuition', 'employment_rate', 'education'])]
    payment_features = [f for f in feature_importance_df['feature'] if any(
        prefix in f.lower() for prefix in ['missed', 'late', 'delinquency_rate', 'consistency'])]
    
    print(f"\nFeature Importance by Data Source:")
    print(f"User Profile Features: {sum(feature_importance_df[feature_importance_df['feature'].isin(user_features)]['importance']):.3f}")
    print(f"Loan Info Features: {sum(feature_importance_df[feature_importance_df['feature'].isin(loan_features)]['importance']):.3f}")
    print(f"Program Features: {sum(feature_importance_df[feature_importance_df['feature'].isin(program_features)]['importance']):.3f}")
    print(f"Payment Behavior Features: {sum(feature_importance_df[feature_importance_df['feature'].isin(payment_features)]['importance']):.3f}")
    
    return feature_importance_df

def calculate_risk_scores(model, X, scaler=None, model_name='', algorithm='percentile'):
    """
    Calculate delinquency risk scores using discrete levels: 0 (low), 1 (medium), 2 (high).
    
    Args:
        model: Trained ML model
        X: Feature matrix
        scaler: Feature scaler (for Logistic Regression)
        model_name: Name of the model
        algorithm: Risk scoring algorithm ('percentile', 'threshold', 'kmeans', 'svm', 'knn')
    
    Returns:
        Array of risk scores (0, 1, or 2)
    """
    if model_name == 'Logistic Regression' and scaler is not None:
        X_scaled = scaler.transform(X)
        risk_probabilities = model.predict_proba(X_scaled)[:, 1]
    else:
        risk_probabilities = model.predict_proba(X)[:, 1]
    
    print(f"\nUsing '{algorithm}' algorithm for risk scoring...")
    
    if algorithm == 'percentile':
        # Percentile-based approach: bottom 60% = 0, next 30% = 1, top 10% = 2
        percentiles = np.percentile(risk_probabilities, [60, 90])
        risk_scores = np.zeros(len(risk_probabilities))
        risk_scores[risk_probabilities > percentiles[0]] = 1
        risk_scores[risk_probabilities > percentiles[1]] = 2
        
    elif algorithm == 'threshold':
        # Fixed threshold approach based on probability values
        risk_scores = np.zeros(len(risk_probabilities))
        risk_scores[risk_probabilities > 0.3] = 1  # Medium risk threshold
        risk_scores[risk_probabilities > 0.6] = 2  # High risk threshold
        
    elif algorithm == 'kmeans':
        # K-means clustering approach
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(risk_probabilities.reshape(-1, 1))
        
        # Map clusters to risk levels based on cluster centers
        cluster_centers = kmeans.cluster_centers_.flatten()
        center_order = np.argsort(cluster_centers)
        
        risk_scores = np.zeros(len(risk_probabilities))
        for i, cluster_idx in enumerate(center_order):
            risk_scores[clusters == cluster_idx] = i
    
    elif algorithm == 'svm':
        # SVM-based risk classification using probability bins
        print("Training SVM classifier for risk level prediction...")
        
        # Create more balanced risk labels using percentiles rather than terciles
        prob_percentiles = np.percentile(risk_probabilities, [40, 80])  # 40-40-20 split instead of 33-33-33
        training_labels = np.zeros(len(risk_probabilities))
        training_labels[risk_probabilities > prob_percentiles[0]] = 1
        training_labels[risk_probabilities > prob_percentiles[1]] = 2
        
        # Verify we have all three classes in training data
        unique_labels, label_counts = np.unique(training_labels, return_counts=True)
        print(f"Training label distribution: {dict(zip(unique_labels.astype(int), label_counts))}")
        
        # Use a more balanced SVM with class weighting
        svm_model = SVC(
            kernel='rbf', 
            probability=True, 
            random_state=42,
            class_weight='balanced',  # Handle class imbalance
            C=1.0,  # Regularization parameter
            gamma='scale'  # Kernel coefficient
        )
        X_for_svm = X if scaler is None else scaler.transform(X)
        
        # Ensure we have sufficient samples for each class
        min_samples_per_class = 10
        for label in [0, 1, 2]:
            count = np.sum(training_labels == label)
            if count < min_samples_per_class:
                print(f"Warning: Only {count} samples for class {label}. Adjusting percentiles...")
                # Fall back to a more conservative split
                prob_percentiles = np.percentile(risk_probabilities, [50, 85])  # 50-35-15 split
                training_labels = np.zeros(len(risk_probabilities))
                training_labels[risk_probabilities > prob_percentiles[0]] = 1
                training_labels[risk_probabilities > prob_percentiles[1]] = 2
                break
        
        # Use stratified split with minimum class representation
        try:
            X_train_svm, X_test_svm, y_train_svm, y_test_svm = train_test_split(
                X_for_svm, training_labels, test_size=0.3, random_state=42, 
                stratify=training_labels
            )
        except ValueError:
            # If stratification fails, use regular split
            X_train_svm, X_test_svm, y_train_svm, y_test_svm = train_test_split(
                X_for_svm, training_labels, test_size=0.3, random_state=42
            )
        
        svm_model.fit(X_train_svm, y_train_svm)
        risk_scores = svm_model.predict(X_for_svm)
        
        # Verify the output distribution
        unique_output, output_counts = np.unique(risk_scores, return_counts=True)
        print(f"SVM Output distribution: {dict(zip(unique_output.astype(int), output_counts))}")
        
        print(f"SVM Training Accuracy: {svm_model.score(X_train_svm, y_train_svm):.3f}")
        print(f"SVM Test Accuracy: {svm_model.score(X_test_svm, y_test_svm):.3f}")
        
        # If SVM still doesn't produce medium risk, force a more balanced distribution
        if 1 not in risk_scores:
            print("SVM didn't produce medium risk. Applying post-processing...")
            # Convert some low-prob high-risk to medium risk
            high_risk_indices = np.where(risk_scores == 2)[0]
            if len(high_risk_indices) > 0:
                # Convert bottom 30% of high-risk to medium risk
                high_risk_probs = risk_probabilities[high_risk_indices]
                medium_threshold = np.percentile(high_risk_probs, 30)
                medium_candidates = high_risk_indices[high_risk_probs <= medium_threshold]
                risk_scores[medium_candidates] = 1
    
    elif algorithm == 'knn':
        # KNN-based risk classification
        print("Training KNN classifier for risk level prediction...")
        
        # Create risk labels based on probability terciles for training
        prob_terciles = np.percentile(risk_probabilities, [40, 80])  # Match SVM approach
        training_labels = np.zeros(len(risk_probabilities))
        training_labels[risk_probabilities > prob_terciles[0]] = 1
        training_labels[risk_probabilities > prob_terciles[1]] = 2
        
        # Verify we have all three classes
        unique_labels, label_counts = np.unique(training_labels, return_counts=True)
        print(f"Training label distribution: {dict(zip(unique_labels.astype(int), label_counts))}")
        
        # Train KNN classifier with optimal k
        optimal_k = min(15, max(3, int(np.sqrt(len(risk_probabilities)))))  # Ensure k >= 3
        knn_model = KNeighborsClassifier(n_neighbors=optimal_k, weights='distance')
        
        X_for_knn = X if scaler is None else scaler.transform(X)
        
        # Use stratified split with error handling
        try:
            X_train_knn, X_test_knn, y_train_knn, y_test_knn = train_test_split(
                X_for_knn, training_labels, test_size=0.3, random_state=42, 
                stratify=training_labels
            )
        except ValueError:
            # If stratification fails, use regular split
            X_train_knn, X_test_knn, y_train_knn, y_test_knn = train_test_split(
                X_for_knn, training_labels, test_size=0.3, random_state=42
            )
        
        knn_model.fit(X_train_knn, y_train_knn)
        risk_scores = knn_model.predict(X_for_knn)
        
        # Verify the output distribution
        unique_output, output_counts = np.unique(risk_scores, return_counts=True)
        print(f"KNN Output distribution: {dict(zip(unique_output.astype(int), output_counts))}")
        
        print(f"KNN Training Accuracy (k={optimal_k}): {knn_model.score(X_train_knn, y_train_knn):.3f}")
        print(f"KNN Test Accuracy: {knn_model.score(X_test_knn, y_test_knn):.3f}")
        
        # If KNN still doesn't produce medium risk, force a more balanced distribution
        if 1 not in risk_scores:
            print("KNN didn't produce medium risk. Applying post-processing...")
            # Use probability-based adjustment
            medium_threshold_low = np.percentile(risk_probabilities, 40)
            medium_threshold_high = np.percentile(risk_probabilities, 80)
            medium_candidates = np.where(
                (risk_probabilities >= medium_threshold_low) & 
                (risk_probabilities <= medium_threshold_high)
            )[0]
            if len(medium_candidates) > 0:
                risk_scores[medium_candidates] = 1
            
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. Choose from 'percentile', 'threshold', 'kmeans', 'svm', 'knn'")
    
    # Convert to integers
    risk_scores = risk_scores.astype(int)
    
    # Distribution summary
    low_risk = np.sum(risk_scores == 0)
    medium_risk = np.sum(risk_scores == 1)
    high_risk = np.sum(risk_scores == 2)
    
    print(f"\nRisk Score Distribution Summary:")
    print(f"  Algorithm: {algorithm}")
    print(f"  Low Risk (0): {low_risk:,} borrowers ({low_risk/len(risk_scores)*100:.1f}%)")
    print(f"  Medium Risk (1): {medium_risk:,} borrowers ({medium_risk/len(risk_scores)*100:.1f}%)")
    print(f"  High Risk (2): {high_risk:,} borrowers ({high_risk/len(risk_scores)*100:.1f}%)")
    
    if algorithm == 'threshold':
        print(f"\nProbability Thresholds Used:")
        print(f"  Low -> Medium: 0.3")
        print(f"  Medium -> High: 0.6")
    elif algorithm == 'percentile':
        print(f"\nPercentile Thresholds Used:")
        print(f"  Low -> Medium: {np.percentile(risk_probabilities, 60):.4f}")
        print(f"  Medium -> High: {np.percentile(risk_probabilities, 90):.4f}")
    elif algorithm in ['svm', 'knn']:
        print(f"\nML Classifier Details:")
        if algorithm == 'svm':
            print(f"  Kernel: RBF (Radial Basis Function)")
            print(f"  Training method: Stratified split with probability-based labels")
        else:
            print(f"  K-value: {optimal_k} (distance-weighted)")
            print(f"  Training method: Stratified split with probability-based labels")
    
    return risk_scores

def update_loan_info_table(df, risk_scores, db_path="student_loan_data.db"):
    """
    Add delinquency_risk column to loan_info table and update with calculated scores.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add the delinquency_risk column if it doesn't exist (INTEGER for 0, 1, 2)
    try:
        cursor.execute("ALTER TABLE loan_info ADD COLUMN delinquency_risk INTEGER")
        print("Added delinquency_risk column to loan_info table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("delinquency_risk column already exists")
        else:
            raise e
    
    # Update risk scores for each payer
    for payer_id, risk_score in zip(df['payer_id'], risk_scores):
        cursor.execute(
            "UPDATE loan_info SET delinquency_risk = ? WHERE payer_id = ?", 
            (int(risk_score), int(payer_id))
        )
    
    conn.commit()
    conn.close()
    
    print(f"Updated {len(risk_scores)} risk scores in loan_info table")
    print(f"Risk score statistics:")
    print(f"  Low Risk (0): {np.sum(risk_scores == 0):,} borrowers")
    print(f"  Medium Risk (1): {np.sum(risk_scores == 1):,} borrowers")
    print(f"  High Risk (2): {np.sum(risk_scores == 2):,} borrowers")

def generate_analysis_report(df, feature_importance_df, model_results, risk_scores):
    """
    Generate comprehensive delinquency analysis report.
    """
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE DELINQUENCY ANALYSIS REPORT")
    print(f"{'='*80}")
    
    print(f"\nDataset Overview:")
    print(f"- Total borrowers analyzed: {len(df):,}")
    print(f"- Delinquent borrowers: {df['is_delinquent'].sum():,}")
    print(f"- Overall delinquency rate: {df['is_delinquent'].mean():.2%}")
    
    print(f"\nModel Performance Summary:")
    for name, results in model_results.items():
        print(f"- {name}: AUC = {results['auc_score']:.4f}")
    
    print(f"\nTop 10 Risk Factors for Delinquency:")
    for i, (_, row) in enumerate(feature_importance_df.head(10).iterrows()):
        print(f"{i+1:2d}. {row['feature']}")
    
    # Risk score distribution with discrete levels
    risk_labels = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}
    
    # Create risk categories based on the actual risk scores
    df_with_risk = df.copy()
    df_with_risk['calculated_risk'] = risk_scores
    df_with_risk['risk_category'] = df_with_risk['calculated_risk'].map(risk_labels)
    
    print(f"\nRisk Score Distribution:")
    for risk_level in [0, 1, 2]:
        count = np.sum(risk_scores == risk_level)
        pct = count / len(risk_scores) * 100
        print(f"- {risk_labels[risk_level]} ({risk_level}): {count:,} borrowers ({pct:.1f}%)")
    
    # Correlation with actual delinquency - improved analysis
    print(f"\nRisk Score Validation (Actual Delinquency Rates by Risk Level):")
    for risk_level in [0, 1, 2]:
        level_data = df_with_risk[df_with_risk['calculated_risk'] == risk_level]
        if len(level_data) > 0:
            actual_delinq_rate = level_data['is_delinquent'].mean()
            print(f"- {risk_labels[risk_level]} ({risk_level}):")
            print(f"    Actual Delinquency Rate: {actual_delinq_rate:.1%}")
            print(f"    Borrowers in Level: {len(level_data):,}")
    
    # Show examples by risk level
    for risk_level in [2, 1, 0]:  # Start with highest risk
        level_data = df_with_risk[df_with_risk['calculated_risk'] == risk_level]
        if len(level_data) > 0:
            sample_size = min(5, len(level_data))
            samples = level_data.sample(n=sample_size, random_state=42)[['payer_id', 'calculated_risk', 'is_delinquent']]
            print(f"\n{sample_size} Sample {risk_labels[risk_level]} Borrowers:")
            for _, row in samples.iterrows():
                status = "DELINQUENT" if row['is_delinquent'] else "Current"
                print(f"  Payer {row['payer_id']}: Risk Level {int(row['calculated_risk'])} - {status}")

def parse_arguments():
    """
    Parse command line arguments for delinquency analysis.
    """
    parser = argparse.ArgumentParser(
        description="Comprehensive Delinquency Risk Analysis with Discrete Risk Scores",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Risk Scoring Algorithms:
  percentile  - Bottom 60% = Low(0), Next 30% = Medium(1), Top 10% = High(2)
  threshold   - Fixed probability thresholds: <0.3=Low, 0.3-0.6=Medium, >0.6=High
  kmeans      - K-means clustering of probabilities into 3 risk groups
  svm         - Support Vector Machine classifier trained on probability-based risk labels
  knn         - K-Nearest Neighbors classifier with optimal k and distance weighting

Examples:
  python delinquency_analysis.py --algorithm percentile
  python delinquency_analysis.py --algorithm svm --db_path my_data.db
  python delinquency_analysis.py --algorithm knn
        """
    )
    
    parser.add_argument(
        "--algorithm",
        choices=['percentile', 'threshold', 'kmeans', 'svm', 'knn'],
        default='percentile',
        help="Risk scoring algorithm to use (default: percentile)"
    )
    
    parser.add_argument(
        "--db_path",
        default="student_loan_data.db",
        help="Path to SQLite database (default: student_loan_data.db)"
    )
    
    return parser.parse_args()

def main():
    """
    Main execution function for delinquency analysis.
    """
    args = parse_arguments()
    
    print("Starting Comprehensive Delinquency Risk Analysis...")
    print("=" * 60)
    print(f"Database: {args.db_path}")
    print(f"Algorithm: {args.algorithm}")
    print(f"Risk Levels: 0 (Low), 1 (Medium), 2 (High)")
    print("=" * 60)
    
    # Load and prepare data
    df = load_comprehensive_dataset(args.db_path)
    df = engineer_features(df)
    X, y, feature_columns, label_encoders = prepare_ml_features(df)
    
    # Train models
    best_model, model_results, scaler = train_delinquency_models(X, y)
    
    # Analyze feature importance
    best_model_name = max(model_results.keys(), key=lambda x: model_results[x]['auc_score'])
    feature_importance_df = analyze_feature_importance(best_model, feature_columns, best_model_name)
    
    # Calculate risk scores using specified algorithm
    risk_scores = calculate_risk_scores(best_model, X, scaler, best_model_name, args.algorithm)
    
    # Update database
    update_loan_info_table(df, risk_scores, args.db_path)
    
    # Generate report
    generate_analysis_report(df, feature_importance_df, model_results, risk_scores)
    
    print(f"\nDelinquency analysis complete!")
    print(f"The loan_info table has been updated with delinquency_risk scores.")
    print(f"Risk scores: 0 (Low Risk), 1 (Medium Risk), 2 (High Risk)")
    print(f"Algorithm used: {args.algorithm}")

if __name__ == "__main__":
    main()