"""
Exploratory Data Analysis (EDA) with Principal Component Analysis (PCA)
for Student Loan Delinquency Risk Assessment

This script performs comprehensive exploratory data analysis including:
- PCA dimensionality reduction and visualization
- Feature correlation analysis
- Risk distribution analysis across principal components
- Interactive charts and statistical insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime
import argparse
import os

# Import existing data processing functions
from delinquency_analysis.delinquency_analysis import load_comprehensive_dataset, engineer_features, prepare_ml_features

warnings.filterwarnings('ignore')

class ExploratoryDataAnalysis:
    """
    Comprehensive EDA class with PCA analysis and visualization capabilities.
    """
    
    def __init__(self, db_path="student_loan_data.db", output_dir="eda_outputs"):
        """
        Initialize EDA with database path and output directory.
        
        Args:
            db_path: Path to SQLite database
            output_dir: Directory to save charts and analysis results
        """
        self.db_path = db_path
        self.output_dir = output_dir
        self.create_output_directory()
        
        # Data containers
        self.raw_df = None
        self.processed_df = None
        self.X_scaled = None
        self.y = None
        self.feature_columns = None
        self.pca = None
        self.pca_components = None
        self.explained_variance = None
        
        print(f"🔍 Exploratory Data Analysis initialized")
        print(f"📊 Output directory: {self.output_dir}")
    
    def create_output_directory(self):
        """Create output directory for charts and analysis results."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created output directory: {self.output_dir}")
    
    def load_and_process_data(self):
        """
        Load data from database and apply feature engineering.
        """
        print("📥 Loading comprehensive dataset...")
        self.raw_df = load_comprehensive_dataset(self.db_path)
        
        print("🔧 Engineering features...")
        self.processed_df = engineer_features(self.raw_df)
        
        print("🎯 Preparing ML features...")
        X, self.y, self.feature_columns, self.label_encoders = prepare_ml_features(self.processed_df)
        
        # Standardize features for PCA
        print("📏 Standardizing features...")
        scaler = StandardScaler()
        self.X_scaled = scaler.fit_transform(X)
        self.scaler = scaler
        
        print(f"✅ Data processing complete:")
        print(f"   • Sample size: {len(self.processed_df):,} borrowers")
        print(f"   • Features: {len(self.feature_columns)} engineered features")
        print(f"   • Delinquency rate: {self.y.mean():.2%}")
        
        return self.processed_df
    
    def perform_pca_analysis(self, n_components=None):
        """
        Perform Principal Component Analysis on the standardized features.
        
        Args:
            n_components: Number of components to keep (None for all)
        """
        if self.X_scaled is None:
            raise ValueError("Data must be loaded and processed first!")
        
        print("🧮 Performing Principal Component Analysis...")
        
        # Determine optimal number of components if not specified
        if n_components is None:
            n_components = min(len(self.feature_columns), len(self.processed_df)) - 1
        
        # Fit PCA
        self.pca = PCA(n_components=n_components, random_state=42)
        self.pca_components = self.pca.fit_transform(self.X_scaled)
        
        # Calculate explained variance
        self.explained_variance = self.pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(self.explained_variance)
        
        print(f"🎯 PCA Analysis Results:")
        print(f"   • Components extracted: {len(self.explained_variance)}")
        print(f"   • Variance explained by PC1: {self.explained_variance[0]:.2%}")
        print(f"   • Variance explained by PC2: {self.explained_variance[1]:.2%}")
        print(f"   • Cumulative variance (first 5 PCs): {cumulative_variance[4]:.2%}")
        print(f"   • Components for 80% variance: {np.argmax(cumulative_variance >= 0.8) + 1}")
        print(f"   • Components for 95% variance: {np.argmax(cumulative_variance >= 0.95) + 1}")
        
        return self.pca_components
    
    def create_scree_plot(self):
        """
        Create scree plot showing explained variance by each principal component.
        """
        if self.pca is None:
            raise ValueError("PCA must be performed first!")
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Individual Explained Variance', 'Cumulative Explained Variance'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Individual variance
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(self.explained_variance) + 1)),
                y=self.explained_variance * 100,
                mode='lines+markers',
                name='Explained Variance',
                line=dict(color='royalblue', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Cumulative variance
        cumulative_variance = np.cumsum(self.explained_variance) * 100
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(cumulative_variance) + 1)),
                y=cumulative_variance,
                mode='lines+markers',
                name='Cumulative Variance',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        # Add 80% and 95% reference lines
        fig.add_hline(y=80, line_dash="dash", line_color="green", row=1, col=2)
        fig.add_hline(y=95, line_dash="dash", line_color="orange", row=1, col=2)
        
        fig.update_xaxes(title_text="Principal Component", row=1, col=1)
        fig.update_xaxes(title_text="Principal Component", row=1, col=2)
        fig.update_yaxes(title_text="Explained Variance (%)", row=1, col=1)
        fig.update_yaxes(title_text="Cumulative Variance (%)", row=1, col=2)
        
        fig.update_layout(
            title="📊 PCA Scree Plot: Explained Variance Analysis",
            height=500,
            showlegend=False
        )
        
        # Save plot
        output_path = os.path.join(self.output_dir, "pca_scree_plot.html")
        fig.write_html(output_path)
        print(f"📊 Scree plot saved: {output_path}")
        
        return fig
    
    def create_pca_scatter_plot(self):
        """
        Create interactive scatter plot of first two principal components colored by delinquency risk.
        """
        if self.pca_components is None:
            raise ValueError("PCA must be performed first!")
        
        # Create DataFrame for plotting
        plot_df = pd.DataFrame({
            'PC1': self.pca_components[:, 0],
            'PC2': self.pca_components[:, 1],
            'Risk_Level': ['High Risk' if x == 1 else 'Low Risk' for x in self.y],
            'Loan_Amount': self.processed_df['loan_amount'],
            'Annual_Income': self.processed_df['annual_income_cad'],
            'Age': self.processed_df['age'],
            'Delinquency_Rate': self.processed_df['delinquency_rate'].fillna(0)
        })
        
        # Create interactive scatter plot
        fig = px.scatter(
            plot_df,
            x='PC1',
            y='PC2',
            color='Risk_Level',
            size='Loan_Amount',
            hover_data=['Annual_Income', 'Age', 'Delinquency_Rate'],
            title=f"🎯 PCA Analysis: Principal Components 1 vs 2<br>PC1 explains {self.explained_variance[0]:.1%}, PC2 explains {self.explained_variance[1]:.1%}",
            labels={
                'PC1': f'First Principal Component ({self.explained_variance[0]:.1%} variance)',
                'PC2': f'Second Principal Component ({self.explained_variance[1]:.1%} variance)'
            },
            color_discrete_map={'High Risk': 'red', 'Low Risk': 'blue'}
        )
        
        fig.update_layout(
            height=600,
            width=800
        )
        
        # Save plot
        output_path = os.path.join(self.output_dir, "pca_scatter_plot.html")
        fig.write_html(output_path)
        print(f"📊 PCA scatter plot saved: {output_path}")
        
        return fig
    
    def create_biplot(self, pc1=0, pc2=1, top_features=15):
        """
        Create PCA biplot showing both data points and feature loading vectors.
        
        Args:
            pc1: First principal component index (default 0)
            pc2: Second principal component index (default 1) 
            top_features: Number of top contributing features to show (default 15)
        """
        if self.pca is None:
            raise ValueError("PCA must be performed first!")
        
        # Get feature loadings (components)
        loadings = self.pca.components_.T * np.sqrt(self.pca.explained_variance_)
        
        # Create figure
        fig = go.Figure()
        
        # Add data points
        risk_colors = ['blue' if x == 0 else 'red' for x in self.y]
        
        fig.add_trace(go.Scatter(
            x=self.pca_components[:, pc1],
            y=self.pca_components[:, pc2],
            mode='markers',
            marker=dict(
                color=risk_colors,
                size=6,
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            name='Borrowers',
            hovertemplate=f'PC{pc1+1}: %{{x:.2f}}<br>PC{pc2+1}: %{{y:.2f}}<extra></extra>'
        ))
        
        # Calculate feature importance for the selected components
        feature_importance = np.abs(loadings[:, pc1]) + np.abs(loadings[:, pc2])
        top_indices = np.argsort(feature_importance)[-top_features:]
        
        # Add feature vectors for top contributing features
        scale_factor = 3  # Scale factor for visibility
        
        for i in top_indices:
            feature_name = self.feature_columns[i]
            
            # Shorten long feature names
            if len(feature_name) > 20:
                display_name = feature_name[:17] + "..."
            else:
                display_name = feature_name
            
            fig.add_trace(go.Scatter(
                x=[0, loadings[i, pc1] * scale_factor],
                y=[0, loadings[i, pc2] * scale_factor],
                mode='lines+text',
                line=dict(color='green', width=2),
                text=['', display_name],
                textposition='top center',
                textfont=dict(size=10, color='darkgreen'),
                name=display_name,
                showlegend=False,
                hovertemplate=f'{feature_name}<br>PC{pc1+1} loading: {loadings[i, pc1]:.3f}<br>PC{pc2+1} loading: {loadings[i, pc2]:.3f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=f"🎯 PCA Biplot: Components {pc1+1} vs {pc2+1}<br>Top {top_features} Contributing Features",
            xaxis_title=f'PC{pc1+1} ({self.explained_variance[pc1]:.1%} variance)',
            yaxis_title=f'PC{pc2+1} ({self.explained_variance[pc2]:.1%} variance)',
            height=700,
            width=900,
            hovermode='closest'
        )
        
        # Save plot
        output_path = os.path.join(self.output_dir, f"pca_biplot_pc{pc1+1}_vs_pc{pc2+1}.html")
        fig.write_html(output_path)
        print(f"📊 PCA biplot saved: {output_path}")
        
        return fig
    
    def analyze_feature_contributions(self, top_n=20):
        """
        Analyze and visualize which original features contribute most to each principal component.
        
        Args:
            top_n: Number of top features to display for each component
        """
        if self.pca is None:
            raise ValueError("PCA must be performed first!")
        
        # Create feature contribution analysis for first few components
        n_components_to_analyze = min(5, len(self.explained_variance))
        
        fig = make_subplots(
            rows=n_components_to_analyze, cols=1,
            subplot_titles=[f'PC{i+1} Feature Contributions ({self.explained_variance[i]:.1%} variance)' 
                          for i in range(n_components_to_analyze)],
            vertical_spacing=0.08
        )
        
        for pc in range(n_components_to_analyze):
            # Get loadings for this component
            loadings = self.pca.components_[pc]
            
            # Get top positive and negative loadings
            loading_df = pd.DataFrame({
                'Feature': self.feature_columns,
                'Loading': loadings,
                'Abs_Loading': np.abs(loadings)
            })
            
            top_features = loading_df.nlargest(top_n, 'Abs_Loading')
            
            # Create horizontal bar chart
            colors = ['red' if x < 0 else 'blue' for x in top_features['Loading']]
            
            fig.add_trace(
                go.Bar(
                    x=top_features['Loading'],
                    y=top_features['Feature'],
                    orientation='h',
                    marker_color=colors,
                    name=f'PC{pc+1}',
                    showlegend=False
                ),
                row=pc+1, col=1
            )
        
        fig.update_layout(
            title="🔍 Feature Contributions to Principal Components",
            height=300 * n_components_to_analyze,
            showlegend=False
        )
        
        # Update x-axis labels
        for i in range(n_components_to_analyze):
            fig.update_xaxes(title_text="Feature Loading", row=i+1, col=1)
        
        # Save plot
        output_path = os.path.join(self.output_dir, "pca_feature_contributions.html")
        fig.write_html(output_path)
        print(f"📊 Feature contributions analysis saved: {output_path}")
        
        return fig
    
    def create_correlation_heatmap(self):
        """
        Create correlation heatmap of original features.
        """
        if self.processed_df is None:
            raise ValueError("Data must be loaded first!")
        
        # Select only numerical features that exist in processed_df
        available_numerical_cols = []
        for col in self.processed_df.columns:
            if self.processed_df[col].dtype in ['int64', 'float64'] and col != 'payer_id':
                available_numerical_cols.append(col)
        
        numerical_features = self.processed_df[available_numerical_cols]
        
        # Calculate correlation matrix
        correlation_matrix = numerical_features.corr()
        
        # Create interactive heatmap
        fig = px.imshow(
            correlation_matrix,
            title="🌡️ Feature Correlation Heatmap",
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        fig.update_layout(
            height=800,
            width=800
        )
        
        # Save plot
        output_path = os.path.join(self.output_dir, "feature_correlation_heatmap.html")
        fig.write_html(output_path)
        print(f"📊 Correlation heatmap saved: {output_path}")
        
        return fig
    
    def perform_clustering_analysis(self, n_clusters=3):
        """
        Perform K-means clustering on PCA components and visualize results.
        
        Args:
            n_clusters: Number of clusters for K-means
        """
        if self.pca_components is None:
            raise ValueError("PCA must be performed first!")
        
        print(f"🎯 Performing K-means clustering with {n_clusters} clusters...")
        
        # Use first few principal components for clustering
        pca_for_clustering = self.pca_components[:, :5]  # First 5 components
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(pca_for_clustering)
        
        # Create DataFrame for plotting
        plot_df = pd.DataFrame({
            'PC1': self.pca_components[:, 0],
            'PC2': self.pca_components[:, 1],
            'Cluster': [f'Cluster {i+1}' for i in cluster_labels],
            'Risk_Level': ['High Risk' if x == 1 else 'Low Risk' for x in self.y],
            'Loan_Amount': self.processed_df['loan_amount'],
            'Annual_Income': self.processed_df['annual_income_cad']
        })
        
        # Create clustering visualization
        fig = px.scatter(
            plot_df,
            x='PC1',
            y='PC2',
            color='Cluster',
            symbol='Risk_Level',
            size='Loan_Amount',
            hover_data=['Annual_Income'],
            title=f"🎯 K-means Clustering Analysis on PCA Components<br>({n_clusters} clusters identified)",
            labels={
                'PC1': f'PC1 ({self.explained_variance[0]:.1%} variance)',
                'PC2': f'PC2 ({self.explained_variance[1]:.1%} variance)'
            }
        )
        
        fig.update_layout(height=600, width=800)
        
        # Save plot
        output_path = os.path.join(self.output_dir, f"pca_clustering_k{n_clusters}.html")
        fig.write_html(output_path)
        print(f"📊 Clustering analysis saved: {output_path}")
        
        # Analyze cluster characteristics
        cluster_analysis = self.analyze_cluster_characteristics(cluster_labels)
        
        return fig, cluster_labels, cluster_analysis
    
    def analyze_cluster_characteristics(self, cluster_labels):
        """
        Analyze characteristics of each cluster.
        
        Args:
            cluster_labels: Cluster assignments for each data point
        """
        cluster_df = self.processed_df.copy()
        cluster_df['Cluster'] = cluster_labels
        
        # Analysis by cluster
        cluster_stats = []
        
        for cluster_id in sorted(cluster_df['Cluster'].unique()):
            cluster_data = cluster_df[cluster_df['Cluster'] == cluster_id]
            
            stats = {
                'Cluster': f'Cluster {cluster_id + 1}',
                'Size': len(cluster_data),
                'Size_Pct': len(cluster_data) / len(cluster_df) * 100,
                'Delinquency_Rate': cluster_data['is_delinquent'].mean() * 100,
                'Avg_Age': cluster_data['age'].mean(),
                'Avg_Income': cluster_data['annual_income_cad'].mean(),
                'Avg_Loan_Amount': cluster_data['loan_amount'].mean(),
                'Avg_Payment_Ratio': cluster_data['payment_to_income_ratio'].mean()
            }
            cluster_stats.append(stats)
        
        cluster_analysis_df = pd.DataFrame(cluster_stats)
        
        print("\\n🎯 Cluster Analysis Summary:")
        print(cluster_analysis_df.round(2))
        
        # Save cluster analysis
        output_path = os.path.join(self.output_dir, "cluster_analysis_summary.csv")
        cluster_analysis_df.to_csv(output_path, index=False)
        print(f"📊 Cluster analysis saved: {output_path}")
        
        return cluster_analysis_df
    
    def generate_comprehensive_report(self):
        """
        Generate a comprehensive EDA report with all analyses and insights.
        """
        print("📋 Generating comprehensive EDA report...")
        
        report = f"""
# 🔍 Exploratory Data Analysis Report
## Student Loan Delinquency Risk Assessment

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** {self.db_path}

## 📊 Dataset Overview

- **Total Borrowers:** {len(self.processed_df):,}
- **Total Features:** {len(self.feature_columns)} (engineered)
- **Delinquency Rate:** {self.y.mean():.2%}
- **Data Quality:** Complete records after feature engineering

## 🧮 Principal Component Analysis Results

### Variance Explanation
- **PC1:** {self.explained_variance[0]:.2%} of total variance
- **PC2:** {self.explained_variance[1]:.2%} of total variance
- **PC3:** {self.explained_variance[2]:.2%} of total variance
- **First 5 PCs:** {np.sum(self.explained_variance[:5]):.2%} of total variance
- **Components for 80% variance:** {np.argmax(np.cumsum(self.explained_variance) >= 0.8) + 1}
- **Components for 95% variance:** {np.argmax(np.cumsum(self.explained_variance) >= 0.95) + 1}

### Key Insights from PCA

1. **Dimensionality Reduction:** The dataset's {len(self.feature_columns)} features can be effectively 
   reduced to a smaller number of components while retaining most variance.

2. **Feature Relationships:** PCA reveals underlying relationships between different risk factors
   and borrower characteristics.

3. **Risk Patterns:** The principal components help identify natural groupings of borrowers
   based on their risk profiles.

## 📈 Generated Visualizations

All interactive charts have been saved to the `{self.output_dir}` directory:

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
"""
        
        # Save report
        output_path = os.path.join(self.output_dir, "eda_comprehensive_report.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📋 Comprehensive report saved: {output_path}")
        return report

def main():
    """
    Main function to run the complete exploratory data analysis.
    """
    parser = argparse.ArgumentParser(description='Exploratory Data Analysis with PCA')
    parser.add_argument('--db_path', default='student_loan_data.db', 
                       help='Path to SQLite database')
    parser.add_argument('--output_dir', default='eda_outputs', 
                       help='Output directory for charts and reports')
    parser.add_argument('--n_components', type=int, default=None,
                       help='Number of PCA components (default: auto)')
    parser.add_argument('--n_clusters', type=int, default=3,
                       help='Number of clusters for K-means analysis')
    
    args = parser.parse_args()
    
    print("🚀 Starting Exploratory Data Analysis with PCA...")
    print(f"📂 Database: {args.db_path}")
    print(f"📊 Output directory: {args.output_dir}")
    
    # Initialize EDA
    eda = ExploratoryDataAnalysis(args.db_path, args.output_dir)
    
    try:
        # Step 1: Load and process data
        print("\\n" + "="*60)
        print("STEP 1: DATA LOADING AND PROCESSING")
        print("="*60)
        eda.load_and_process_data()
        
        # Step 2: Perform PCA analysis
        print("\\n" + "="*60)
        print("STEP 2: PRINCIPAL COMPONENT ANALYSIS")
        print("="*60)
        eda.perform_pca_analysis(args.n_components)
        
        # Step 3: Create visualizations
        print("\\n" + "="*60)
        print("STEP 3: CREATING VISUALIZATIONS")
        print("="*60)
        
        # Scree plot
        print("📊 Creating scree plot...")
        eda.create_scree_plot()
        
        # PCA scatter plot
        print("📊 Creating PCA scatter plot...")
        eda.create_pca_scatter_plot()
        
        # Biplot
        print("📊 Creating PCA biplot...")
        eda.create_biplot()
        
        # Feature contributions
        print("📊 Analyzing feature contributions...")
        eda.analyze_feature_contributions()
        
        # Correlation heatmap
        print("📊 Creating correlation heatmap...")
        eda.create_correlation_heatmap()
        
        # Step 4: Clustering analysis
        print("\\n" + "="*60)
        print("STEP 4: CLUSTERING ANALYSIS")
        print("="*60)
        eda.perform_clustering_analysis(args.n_clusters)
        
        # Step 5: Generate comprehensive report
        print("\\n" + "="*60)
        print("STEP 5: GENERATING REPORT")
        print("="*60)
        eda.generate_comprehensive_report()
        
        print("\\n" + "="*60)
        print("✅ ANALYSIS COMPLETE!")
        print("="*60)
        print(f"📊 All visualizations and reports saved to: {args.output_dir}")
        print("🔍 Open the HTML files in your browser to explore the interactive charts.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    main()