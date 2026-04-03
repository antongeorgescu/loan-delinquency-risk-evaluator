#!/usr/bin/env python3
"""
Delinquency Analysis Runner Script
==================================

This script provides a simple interface to run the comprehensive delinquency analysis
and update the database with ML-based risk scores.

Usage:
    python run_delinquency_analysis.py [--db_path path_to_database]
    
Example:
    python run_delinquency_analysis.py --db_path student_loan_data.db
"""

import argparse
import sys
import os
from datetime import datetime

def main():
    """
    Main entry point for running delinquency analysis.
    """
    parser = argparse.ArgumentParser(
        description="Run comprehensive delinquency analysis and update loan risk scores",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Risk Scoring Algorithms:
  percentile  - Bottom 60% = Low(0), Next 30% = Medium(1), Top 10% = High(2)
  threshold   - Fixed probability thresholds: <0.3=Low, 0.3-0.6=Medium, >0.6=High
  kmeans      - K-means clustering of probabilities into 3 risk groups
  svm         - Support Vector Machine classifier trained on probability-based risk labels
  knn         - K-Nearest Neighbors classifier with optimal k and distance weighting

Examples:
  python run_delinquency_analysis.py
  python run_delinquency_analysis.py --algorithm svm
  python run_delinquency_analysis.py --algorithm knn --db_path my_database.db
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
        help="Path to the SQLite database file (default: student_loan_data.db)"
    )
    
    args = parser.parse_args()
    
    # Check if database exists
    if not os.path.exists(args.db_path):
        print(f"Error: Database file '{args.db_path}' not found.")
        print(f"Please run 'python run_data_generation.py' first to create the database.")
        sys.exit(1)
    
    # Check if required Python packages are available
    try:
        import pandas as pd
        import numpy as np
        import sklearn
        print("✓ Required packages (pandas, numpy, scikit-learn) are available")
    except ImportError as e:
        print(f"Error: Required package not found - {e}")
        print("Please install required packages:")
        print("  pip install pandas numpy scikit-learn")
        sys.exit(1)
    
    print(f"🚀 Starting Delinquency Analysis")
    print(f"   Database: {args.db_path}")
    print(f"   Algorithm: {args.algorithm}")
    print(f"   Risk Levels: 0 (Low), 1 (Medium), 2 (High)")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Import and run the analysis
        # Set up arguments for the main analysis script
        sys.argv = ['delinquency_analysis.py', '--algorithm', args.algorithm, '--db_path', args.db_path]
        
        from delinquency_analysis import main as run_analysis
        
        # Run the analysis
        run_analysis()
        
        print("=" * 60)
        print("✅ Delinquency analysis completed successfully!")
        print(f"📊 The database '{args.db_path}' has been updated with ML-based risk scores.")
        print(f"🤖 Algorithm used: {args.algorithm}")
        print(f"📈 Risk levels: 0 (Low), 1 (Medium), 2 (High)")
        print("📈 You can now explore the enhanced data using:")
        print(f"   python explore_database.py --db_path {args.db_path}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("\n🔍 Troubleshooting tips:")
        print("1. Ensure the database has been populated with data")
        print("2. Check that all required tables exist (user_profile, loan_info, program_of_study, loan_payments)")
        print("3. Verify you have sufficient data for machine learning (recommended: 100+ borrowers)")
        print("4. For SVM/KNN algorithms, ensure you have enough diverse data for training")
        print(f"5. Try a different algorithm if '{args.algorithm}' fails (e.g., --algorithm percentile)")
        sys.exit(1)

if __name__ == "__main__":
    main()