# Student Loan Data Generation & Analysis System

A comprehensive Python-based system for generating realistic student loan data and performing machine learning-based delinquency risk analysis with targeted campaign file generation.

## 🎯 System Overview

This system creates a complete student loan database with:
- **User Demographics**: Canadian borrowers with realistic profiles
- **Education Programs**: 42 programs across top 6 Canadian universities  
- **Loan Records**: Complete loan lifecycle with disbursement tracking
- **Payment History**: Individual amortization schedules with risk factors
- **ML Risk Analysis**: Advanced delinquency prediction with 5 algorithms
- **Campaign Generation**: Targeted marketing files for high and medium-risk borrowers

## 📊 Database Schema

### Tables
1. **`user_profile`** - Borrower demographics (age, income, employment, location)
2. **`program_of_study`** - Education programs with difficulty levels and outcomes
3. **`loan_info`** - Loan details with disbursement dates and ML risk scores
4. **`loan_payments`** - Individual payment schedules with principal/interest breakdown

### Key Features
- 🔗 **Foreign key relationships** between all tables
- 💰 **Real amortization calculations** with Canadian loan parameters
- 🎓 **42 education programs** across 3 difficulty levels
- 🏫 **Top 6 Canadian universities** integration
- 🤖 **ML-based risk scoring** with discrete levels (0=Low, 1=Medium, 2=High)
- 📅 **2-year disbursement timeline** (2022-2024)
- 🎯 **Campaign targeting** for marketing and intervention strategies 

## 🚀 Quick Start

### 1. Generate Complete Dataset
```bash
# Create database with all tables and data
python run_data_generation.py

# Generate with CSV exports to database_exports folder
python run_data_generation.py --export_csv
```

### 2. Run ML Risk Analysis  
```bash
# Calculate delinquency risk scores using default percentile algorithm
python run_delinquency_analysis.py

# Use different algorithms for risk scoring
python run_delinquency_analysis.py --algorithm svm
python run_delinquency_analysis.py --algorithm knn
python run_delinquency_analysis.py --algorithm threshold
```

### 3. Generate Campaign Files
```bash
# Create targeted marketing files for high and medium-risk borrowers
python run_campaign_files.py
```

### 5. Run Exploratory Data Analysis
```bash
# Comprehensive EDA with PCA analysis and interactive visualizations
python run_eda_analysis.py

# Advanced EDA with custom parameters
python run_eda_analysis.py --n_clusters 5 --n_components 15
```

### 6. Explore Database
```bash
# Comprehensive database analysis and reporting
python explore_database.py
```

## 📁 File Structure

### Main Entry Points
- **`run_data_generation.py`** - Main data generation orchestrator
- **`run_delinquency_analysis.py`** - ML risk analysis with algorithm selection
- **`run_campaign_files.py`** - Campaign file generation for marketing
- **`run_eda_analysis.py`** - Exploratory Data Analysis with PCA and visualizations
- **`explore_database.py`** - Database reporting and validation

### Package Structure
- **`synthetic_data/`** - Data generation modules
  - `generate_user_profiles.py` - Canadian borrower demographics
  - `generate_programs.py` - Education programs and university assignments
  - `generate_loans.py` - Loan records with disbursement tracking
  - `generate_payments.py` - Payment schedules with risk correlation

- **`delinquency_analysis/`** - ML analysis package
  - `delinquency_analysis.py` - Core ML analysis with 5 algorithms
  - `exploratory_data_analysis.py` - Comprehensive EDA with PCA and visualizations

### Output Folders
- **`database_exports/`** - Timestamped CSV exports of all database tables
- **`campaigns/`** - Targeted marketing files (high_risk_users.csv, medium_risk_users.csv)
- **`eda_outputs/`** - Interactive charts and EDA reports from PCA analysis

### Configuration
- **`.vscode/launch.json`** - VS Code debug configurations for all scripts
- **`requirements.txt`** - Python package dependencies

## 🎓 Educational Programs

### Difficulty Levels & Risk Correlation
- **Level 1 (Low Risk)**: Business, Communications, General Studies
- **Level 2 (Medium Risk)**: Sciences, Engineering, Healthcare  
- **Level 3 (High Risk)**: Arts, Social Sciences, Creative fields

### Universities Included
1. University of Toronto  
2. University of British Columbia
3. McGill University
4. University of Waterloo
5. Queen's University
6. University of Alberta

## 🤖 Machine Learning Features

### Risk Scoring Algorithms Available
1. **percentile** (Default) - Bottom 60%=Low(0), Next 30%=Medium(1), Top 10%=High(2)
2. **threshold** - Fixed probability thresholds: <0.3=Low, 0.3-0.6=Medium, >0.6=High
3. **kmeans** - K-means clustering of probabilities into 3 risk groups
4. **svm** - Support Vector Machine classifier with RBF kernel
5. **knn** - K-Nearest Neighbors with optimal k and distance weighting

### Risk Score System
- **0**: Low Risk - Excellent payment history, strong financials
- **1**: Medium Risk - Some risk factors present, proactive monitoring needed
- **2**: High Risk - Multiple risk factors, immediate intervention required

### ML Models Used
- **Random Forest** - Feature importance analysis
- **Gradient Boosting** - Complex pattern detection  
- **Logistic Regression** - Interpretable linear relationships

### Feature Engineering (40+ Features)
- **Demographics**: Age, income, employment status, location
- **Financial Ratios**: Debt-to-income, payment-to-income, LTV
- **Education**: Program difficulty, employment rates, ROI
- **Payment Behavior**: Missed payments, late fees, consistency
- **Loan Characteristics**: Amount, term, interest rate, maturity

## 🎯 Campaign Generation

### Targeted Marketing Files
- **`campaigns/high_risk_users.csv`** - Risk level 2 borrowers requiring immediate intervention
- **`campaigns/medium_risk_users.csv`** - Risk level 1 borrowers needing proactive monitoring

### Campaign Data Fields
- **User Profile**: Demographics, income categories, age groups
- **Loan Information**: Financial details, payment ratios, remaining balances
- **Program Data**: Education details, career outlook, employment rates
- **Strategy Fields**: Recommended approach, career support flags

### Usage Examples
```bash
# Generate campaign files
python run_campaign_files.py

# Custom database
python run_campaign_files.py --db_path my_database.db
```

## 🔍 Exploratory Data Analysis (EDA)

### Advanced Analytics with PCA
- **Principal Component Analysis**: Dimensionality reduction of 40+ engineered features
- **Interactive Visualizations**: Plotly-based charts for deep data exploration
- **Feature Correlation Analysis**: Identify relationships between risk factors
- **Risk Segmentation**: K-means clustering on principal components
- **Comprehensive Reporting**: Automated insights and business implications

### EDA Outputs Generated
- **PCA Scatter Plots**: Risk distribution across principal components
- **Biplots**: Feature loading vectors overlaid on data points
- **Scree Plots**: Variance explained by each principal component
- **Correlation Heatmaps**: Feature relationship matrices
- **Cluster Analysis**: Natural borrower segments with characteristics
- **Comprehensive Report**: Business insights and recommendations

### Usage Examples
```bash
# Run complete EDA analysis
python run_eda_analysis.py

# Advanced analysis with custom parameters
python run_eda_analysis.py --n_clusters 5 --n_components 15

# Quick test on small dataset
python run_eda_analysis.py --db_path test_data.db --output_dir test_eda
```

## 📈 Sample Output

### Database Statistics
```
=== STUDENT LOAN DATABASE SUMMARY ===
Total Users: 1000+
Total Programs: 42 (across 6 universities) 
Total Loans: 1000+
Total Payments: 24000+ (individual schedules)
Risk Scores: ML-calculated discrete levels (0, 1, 2)
Export Files: Organized CSV exports in database_exports/
Campaign Files: Targeted high_risk_users.csv, medium_risk_users.csv
```

### ML Analysis Results
```
=== DELINQUENCY ANALYSIS RESULTS ===
Algorithm: svm
Models Trained: Random Forest, Gradient Boosting, Logistic Regression
Feature Engineering: 40+ attributes across all tables
Risk Distribution:
  Low Risk (0): 612 borrowers (61.2%)
  Medium Risk (1): 298 borrowers (29.8%)
  High Risk (2): 90 borrowers (9.0%)
Top Risk Factors: Payment history, debt ratios, demographics
Model Performance: Cross-validated AUC scores
```

### Campaign Files Generated
```
🎯 CAMPAIGN FILES SUMMARY
High Risk Borrowers: 90 (immediate intervention needed)
Medium Risk Borrowers: 298 (proactive monitoring)
Files Location: campaigns/
Data Fields: 25+ comprehensive attributes for targeting
```

## 🔧 Configuration Options

### Command Line Arguments
```bash
# Data generation with options
python run_data_generation.py --num_payers 500 --export_csv

# ML analysis with algorithm selection
python run_delinquency_analysis.py --algorithm svm --db_path my_data.db

# Campaign generation
python run_campaign_files.py --db_path student_loan_data.db
```

### Available Algorithms
- `percentile` (default): Statistical percentile-based distribution
- `threshold`: Fixed probability cut-offs
- `kmeans`: Unsupervised clustering approach
- `svm`: Support Vector Machine classification
- `knn`: K-Nearest Neighbors classification

### Debug Configurations (VS Code)
- Generate Data (1000/100/5000 users, custom dates)
- Delinquency Analysis (with algorithm selection)
- Generate Campaign Files
- EDA Analysis (default, advanced, quick test)
- Python: Current File (with arguments)

## 📊 Business Applications

### Risk Management
- **Loan Origination**: Screen applications with ML risk scores (0, 1, 2)
- **Portfolio Monitoring**: Track borrower risk levels over time
- **Collection Strategy**: Prioritize outreach using campaign files
- **Regulatory Compliance**: Comprehensive risk documentation

### Marketing & Campaigns
- **Targeted Outreach**: Use campaign CSV files for personalized marketing
- **Intervention Programs**: Identify high-risk borrowers for proactive support
- **Product Recommendations**: Tailor offers based on risk profiles and education data
- **Retention Strategies**: Proactive engagement with medium-risk borrowers

### Analytics & Insights
- **Market Analysis**: Education program performance trends across universities
- **Regional Risk**: Geographic delinquency patterns by province/city
- **Demographic Studies**: Age, income, employment risk correlations
- **Algorithm Comparison**: Test different ML approaches for risk assessment

## 🛠️ Technical Requirements

### Python Packages
```bash
pip install -r requirements.txt
# Includes: pandas, numpy, scikit-learn, sqlite3 (built-in)
```

### System Requirements
- Python 3.7+
- Windows/macOS/Linux
- 100MB+ free disk space
- 2GB+ RAM for large datasets (5000+ users)

## 🔍 Validation & Quality

### Data Quality Assurance
- ✅ **Referential Integrity**: All foreign keys validated across tables
- ✅ **Realistic Values**: Canadian addresses, proper financial ratios  
- ✅ **Temporal Consistency**: Payments start after disbursement dates
- ✅ **Risk Correlation**: Multi-factor delinquency modeling with 4 algorithms

### ML Model Validation
- ✅ **Cross-Validation**: 5-fold CV for model stability across all algorithms
- ✅ **Algorithm Comparison**: Test multiple approaches (percentile, SVM, KNN, etc.)
- ✅ **Feature Analysis**: Correlation and importance ranking across 40+ features
- ✅ **Risk Distribution**: Realistic discrete score distribution (0, 1, 2)

### Campaign File Validation
- ✅ **Data Completeness**: All required fields populated for marketing campaigns
- ✅ **Risk Accuracy**: Campaign targeting based on validated ML risk scores
- ✅ **Business Logic**: Recommended approaches aligned with risk levels

## 📚 Advanced Usage

### Extending the System  
1. **Add New Algorithms**: Extend `delinquency_analysis/delinquency_analysis.py`
2. **Custom Risk Models**: Modify algorithm implementations for specific business rules
3. **Additional Tables**: Follow foreign key pattern in `synthetic_data/` modules
4. **Campaign Customization**: Extend `run_campaign_files.py` for additional risk tiers
5. **Export Formats**: Enhance export functionality in `run_data_generation.py`

### Integration Points
- **APIs**: Deploy risk scoring endpoints for real-time loan decisioning
- **Dashboards**: Connect BI tools via CSV exports in `database_exports/`
- **CRM Systems**: Import campaign files for targeted marketing automation
- **Regulatory Systems**: Automated compliance reporting with risk score documentation
- **Testing Frameworks**: Use synthetic data for application and integration testing

## 📞 Support & Development

### Common Issues
- **Database Locks**: Ensure no other SQLite connections
- **Memory Usage**: Use smaller datasets or sampling for large generations  
- **ML Performance**: Minimum 100+ borrowers needed for reliable training
- **Package Dependencies**: Update to latest pandas/scikit-learn versions

### Future Enhancements
- Real-time API endpoints for risk scoring
- Advanced ensemble ML models  
- Economic indicator integration
- Automated model retraining pipelines
- Interactive web dashboard

---

**Created by**: Agent-driven development system  
**Version**: 1.0 (ML-Enhanced)  
**Last Updated**: Latest with comprehensive ML analysis integration