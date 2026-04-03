
# 🔍 Exploratory Data Analysis Report
## Student Loan Delinquency Risk Assessment

**Generated on:** 2026-04-02 06:20:59
**Database:** student_loan_data.db

## 📊 Dataset Overview

- **Total Borrowers:** 899
- **Total Features:** 51 (engineered)
- **Delinquency Rate:** 6.01%
- **Data Quality:** Complete records after feature engineering

## 🧮 Principal Component Analysis Results

### Variance Explanation
- **PC1:** 11.42% of total variance
- **PC2:** 9.96% of total variance
- **PC3:** 8.72% of total variance
- **First 5 PCs:** 42.40% of total variance
- **Components for 80% variance:** 17
- **Components for 95% variance:** 27

### Key Insights from PCA

1. **Dimensionality Reduction:** The dataset's 51 features can be effectively 
   reduced to a smaller number of components while retaining most variance.

2. **Feature Relationships:** PCA reveals underlying relationships between different risk factors
   and borrower characteristics.

3. **Risk Patterns:** The principal components help identify natural groupings of borrowers
   based on their risk profiles.

## 📈 Generated Visualizations

All interactive charts have been saved to the `eda_outputs` directory:

1. **pca_scree_plot.html** - Variance explained by each component
2. **pca_scatter_plot.html** - PC1 vs PC2 scatter plot colored by risk
3. **pca_biplot_pc1_vs_pc2.html** - Biplot showing feature loading vectors
4. **pca_feature_contributions.html** - Feature contributions to each PC
5. **feature_correlation_heatmap.html** - Correlation matrix of original features
6. **pca_clustering_k3.html** - K-means clustering on PCA components

## 🎯 Business Implications

### Risk Segmentation
The PCA analysis reveals natural risk segments that can be used for:
- Targeted intervention strategies
- Customized loan products
- Proactive risk management

### Feature Importance
The principal components identify the most important combinations of features
for delinquency prediction, enabling more efficient risk assessment.

### Portfolio Management
Understanding the principal components helps in:
- Diversification strategies
- Risk concentration analysis
- Performance monitoring

---
*This report was generated automatically by the Exploratory Data Analysis system.*
