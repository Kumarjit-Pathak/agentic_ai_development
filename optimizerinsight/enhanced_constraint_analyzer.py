"""
Enhanced Constraint Impact Analyzer with Market Intelligence
Provides actionable insights for planogrammers with competitive analysis and strategic recommendations
"""

import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from openai import OpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import warnings
warnings.filterwarnings('ignore')

# ---------------------- Configuration ----------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.warning("⚠️ OPENAI_API_KEY not found. AI-powered insights will be limited.")

# Initialize OpenAI client
openai_client = None
try:
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    st.error(f"OpenAI client initialization failed: {e}")
    openai_client = None

# ---------------------- Page Configuration ----------------------
st.set_page_config(
    layout="wide",
    page_title="Enhanced Constraint Impact Analyzer",
    initial_sidebar_state="expanded",
    page_icon="🎯"
)

# Enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2980b9);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2980b9;
    }
    .insight-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1976d2;
    }
    .alert-high { border-left-color: #f44336; background: #ffebee; }
    .alert-medium { border-left-color: #ff9800; background: #fff3e0; }
    .alert-low { border-left-color: #4caf50; background: #e8f5e9; }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎯 Enhanced Constraint Impact Analyzer</h1>
    <p>Intelligent insights and actionable recommendations for planogrammers</p>
</div>
""", unsafe_allow_html=True)

# ---------------------- Sidebar Configuration ----------------------
with st.sidebar:
    st.header("⚙️ Analysis Configuration")

    # Analysis mode selection
    analysis_mode = st.selectbox(
        "Analysis Mode",
        ["Standard Analysis", "Deep Competitive Analysis", "Strategic Planning Mode"],
        help="Choose analysis depth and focus"
    )

    # Market context settings
    st.subheader("🌍 Market Context")
    include_market_trends = st.checkbox("Include Market Trend Analysis", value=True)
    competitive_focus = st.selectbox(
        "Competitive Focus",
        ["ABI vs Competitors", "Premium vs Mass Market", "Category Mix Optimization"],
        help="Primary competitive analysis focus"
    )

    # Threshold settings
    st.subheader("📊 Alert Thresholds")
    revenue_threshold = st.slider("Revenue Loss Alert (₹)", 100, 5000, 1000)
    volume_threshold = st.slider("Volume Loss Alert (L)", 10, 500, 100)
    unit_threshold = st.slider("Units Loss Alert", 50, 2000, 500)

# ---------------------- File Upload Section ----------------------
st.markdown("## 📁 Data Upload")

with st.expander("Upload Required Files", expanded=not st.session_state.get('files_uploaded', False)):
    upload_cols = st.columns(3)

    FILES = [
        ("constrained", "Constrained Output", "📊"),
        ("unconstrained", "Unconstrained Output", "📈"),
        ("constraint_types", "Constraint Types", "🏷️"),
        ("shelf_constraints", "Shelf Mapping", "🗂️"),
        ("sku_constraints", "SKU Constraints", "📦"),
        ("sku_meta", "SKU Metadata", "ℹ️")
    ]

    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {k: None for k, _, _ in FILES}

    for i, (key, label, icon) in enumerate(FILES):
        col = upload_cols[i % 3]
        with col:
            current = st.session_state.uploaded_files.get(key)
            if current is None:
                uploaded = st.file_uploader(
                    f"{icon} {label}",
                    type=["xlsx", "xls", "csv"],
                    key=f"uploader_{key}"
                )
                if uploaded:
                    st.session_state.uploaded_files[key] = uploaded
                    st.success(f"✅ {uploaded.name}")
            else:
                st.success(f"✅ {current.name}")
                if st.button("🔄 Replace", key=f"replace_{key}"):
                    st.session_state.uploaded_files[key] = None
                    st.rerun()

# ---------------------- Data Processing Functions ----------------------
@st.cache_data
def read_excel_file(file_obj):
    """Cached function to read Excel files"""
    try:
        return pd.read_excel(file_obj)
    except Exception as e:
        st.error(f"Error reading {getattr(file_obj, 'name', 'file')}: {e}")
        return pd.DataFrame()

def calculate_market_metrics(df, competitor_focus="ABI vs Competitors"):
    """Calculate market intelligence metrics"""
    metrics = {}

    if 'brand_family' in df.columns:
        # Market share calculations
        total_revenue = df['revenue_con'].sum()
        brand_share = df.groupby('brand_family').agg({
            'revenue_con': 'sum',
            'units_con': 'sum',
            'volume_con': 'sum'
        }).reset_index()

        brand_share['revenue_share'] = (brand_share['revenue_con'] / total_revenue * 100).round(2)
        brand_share['avg_price_per_unit'] = (brand_share['revenue_con'] / brand_share['units_con']).round(2)

        metrics['brand_performance'] = brand_share
        metrics['premium_brands'] = brand_share[brand_share['avg_price_per_unit'] > brand_share['avg_price_per_unit'].median()]

    return metrics

def generate_strategic_insights(impact_df, market_metrics, threshold_config):
    """Generate strategic business insights"""
    insights = {
        'critical_issues': [],
        'opportunities': [],
        'strategic_recommendations': [],
        'priority_actions': []
    }

    # Critical issues identification
    critical_constraints = impact_df[
        (impact_df['Revenue_Lost'] > threshold_config['revenue']) |
        (impact_df['Volume_Lost_Ltr'] > threshold_config['volume'])
    ]

    for _, constraint in critical_constraints.iterrows():
        insights['critical_issues'].append({
            'constraint': constraint['Profile'],
            'impact': f"₹{constraint['Revenue_Lost']:.0f} revenue, {constraint['Volume_Lost_Ltr']:.0f}L volume lost",
            'severity': 'HIGH' if constraint['Revenue_Lost'] > threshold_config['revenue'] * 2 else 'MEDIUM'
        })

    # Opportunity identification
    negative_impact = impact_df[impact_df['Revenue_Lost'] < 0]
    for _, opp in negative_impact.iterrows():
        insights['opportunities'].append({
            'constraint': opp['Profile'],
            'gain': f"₹{abs(opp['Revenue_Lost']):.0f} revenue gain potential",
            'recommendation': "Consider expanding this constraint implementation"
        })

    return insights

# ---------------------- Main Analysis Logic ----------------------
files_ready = all(v is not None for v in st.session_state.uploaded_files.values())
if not files_ready:
    missing = [label for (k, label, _) in FILES if st.session_state.uploaded_files.get(k) is None]
    st.warning(f"⏳ Waiting for files: {', '.join(missing)}")
    st.stop()

# Load and process data
with st.spinner("🔄 Processing data files..."):
    data_files = {}
    for key in st.session_state.uploaded_files:
        data_files[key] = read_excel_file(st.session_state.uploaded_files[key])

    constrained = data_files['constrained']
    unconstrained = data_files['unconstrained']
    constraint_types = data_files['constraint_types']
    shelf_constraints = data_files['shelf_constraints']
    sku_constraints = data_files['sku_constraints']
    sku_meta = data_files['sku_meta']

# Data validation - flexible column mapping
st.subheader("🔍 Data Inspection")

# Show available columns for debugging
with st.expander("Available Columns in Uploaded Files"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Constrained file columns:**")
        st.write(list(constrained.columns))
    with col2:
        st.write("**Unconstrained file columns:**")
        st.write(list(unconstrained.columns))

# Flexible column mapping
column_mapping = {}

# Try to find SKU column
sku_candidates = ['sku', 'SKU', 'sku_id', 'SKU_ID', 'Product_ID', 'product_id']
sku_col = None
for candidate in sku_candidates:
    if candidate in constrained.columns:
        sku_col = candidate
        break

if not sku_col:
    st.error("❌ Could not find SKU/Product ID column. Please ensure your file has one of: sku, SKU, sku_id, SKU_ID, Product_ID")
    st.stop()

column_mapping['sku'] = sku_col

# Try to find units column
units_candidates = ['# units', 'units', 'Units', 'quantity', 'Quantity', 'facings', 'Facings']
units_col = None
for candidate in units_candidates:
    if candidate in constrained.columns:
        units_col = candidate
        break

if not units_col:
    st.error("❌ Could not find Units/Quantity column. Please ensure your file has one of: # units, units, Units, quantity, Quantity, facings")
    st.stop()

column_mapping['units'] = units_col

# Try to find price column
price_candidates = ['primary_price_per_ltr', 'price_per_ltr', 'price', 'Price', 'unit_price', 'Unit_Price']
price_col = None
for candidate in price_candidates:
    if candidate in constrained.columns:
        price_col = candidate
        break

if not price_col:
    st.error("❌ Could not find Price column. Please ensure your file has one of: primary_price_per_ltr, price_per_ltr, price, Price, unit_price")
    st.stop()

column_mapping['price'] = price_col

# Try to find volume column
volume_candidates = ['volume_per_unit', 'volume', 'Volume', 'size', 'Size', 'pack_size', 'Pack_Size']
volume_col = None
for candidate in volume_candidates:
    if candidate in constrained.columns:
        volume_col = candidate
        break

if not volume_col:
    st.error("❌ Could not find Volume/Size column. Please ensure your file has one of: volume_per_unit, volume, Volume, size, Size, pack_size")
    st.stop()

column_mapping['volume'] = volume_col

st.success(f"✅ Column mapping successful: SKU={sku_col}, Units={units_col}, Price={price_col}, Volume={volume_col}")

# Standardize column names
for df_name, df in [("constrained", constrained), ("unconstrained", unconstrained)]:
    df.rename(columns={
        column_mapping['sku']: 'sku',
        column_mapping['units']: '# units',
        column_mapping['price']: 'primary_price_per_ltr',
        column_mapping['volume']: 'volume_per_unit'
    }, inplace=True)

# Data preprocessing
for df in [constrained, unconstrained]:
    df["# units"] = pd.to_numeric(df["# units"], errors="coerce").fillna(0)
    df["primary_price_per_ltr"] = pd.to_numeric(df["primary_price_per_ltr"], errors="coerce").fillna(0)
    df["volume_per_unit"] = pd.to_numeric(df["volume_per_unit"], errors="coerce").fillna(0)
    df["price_per_unit"] = df["primary_price_per_ltr"] * df["volume_per_unit"]
    df["revenue"] = df["price_per_unit"] * df["# units"]
    df["volume_total_ltr"] = df["volume_per_unit"] * df["# units"]

# Aggregate and calculate differences
sku_uncon = unconstrained.groupby("sku").agg({
    "# units": "sum", "revenue": "sum", "volume_total_ltr": "sum"
}).reset_index()
sku_uncon.columns = ["sku", "units_uncon", "revenue_uncon", "volume_uncon"]

sku_con = constrained.groupby("sku").agg({
    "# units": "sum", "revenue": "sum", "volume_total_ltr": "sum"
}).reset_index()
sku_con.columns = ["sku", "units_con", "revenue_con", "volume_con"]

# Merge and calculate differences
merged_df = pd.merge(sku_uncon, sku_con, on="sku", how="outer").fillna(0)
merged_df["unit_diff"] = merged_df["units_uncon"] - merged_df["units_con"]
merged_df["revenue_diff"] = merged_df["revenue_uncon"] - merged_df["revenue_con"]
merged_df["volume_diff_ltr"] = merged_df["volume_uncon"] - merged_df["volume_con"]

# Add metadata
final_df = merged_df.merge(sku_meta, on="sku", how="left")
final_df = final_df.merge(sku_constraints, on="sku", how="left")

# ---------------------- Build impact_df with natural-language profile (CORE LOGIC) ----------------------
def build_natural_profile(flagged_df, constraint_col=None):
    """
    Create a short natural-language profile for a flagged subset of SKUs.
    Checks manufacturer, brand_family, pack_type, ptc_segment (constant or small sets)
    and shelf/bin/door fields if present. If `constraint_col` is provided and
    `shelf_constraints` DataFrame is available, also inspect the shelf_constraints
    mapping to detect which shelf/bin/door are flagged for that constraint.
    """
    if flagged_df.empty:
        return "No SKUs flagged."
    parts = []
    # metadata columns to inspect
    for col in ["manufacturer", "brand_family", "pack_qty", "ptc_segment"]:
        if col in flagged_df.columns:
            vals = flagged_df[col].dropna().unique()
            if len(vals) == 1:
                parts.append(f"{col.replace('_',' ').title()} = {vals[0]}")
    #         elif 1 < len(vals) <= 3:
    #             parts.append(f"{col.replace('_',' ').title()} ∈ [{', '.join(map(str, vals))}]")
    # # shelf/bin/door present directly on SKU mapping
    shelf_parts = []
    for s in ["shelf_id", "shelf", "bin_id", "bin", "door_id", "door"]:
        if s in flagged_df.columns:
            vals = flagged_df[s].dropna().unique()
            if len(vals) == 1:
                shelf_parts.append(f"{s.replace('_',' ').title()} = {vals[0]}")
            elif 1 < len(vals) <= 4:
                shelf_parts.append(f"{s.replace('_',' ').title()} ∈ [{', '.join(map(str, vals))}]")
    if shelf_parts:
        parts.extend(shelf_parts)

    # If a constraint column name was provided, consult shelf_constraints (if available)
    # to detect which shelves/bins/doors are flagged for this constraint.
    if constraint_col is not None and 'shelf_constraints' in globals() and not shelf_constraints.empty:
        if constraint_col in shelf_constraints.columns:
            sc = shelf_constraints[shelf_constraints.get(constraint_col, 0) == 1]
            # Look for common shelf/bin/door fields in the shelf_constraints mapping
            sc_parts = []
            for s in ["shelf_id", "shelf", "bin_id", "bin", "door_id", "door"]:
                if s in sc.columns:
                    vals = sc[s].dropna().unique()
                    if len(vals) == 1:
                        sc_parts.append(f"{s.replace('_',' ').title()} = {vals[0]}")
                    elif 1 < len(vals) <= 4:
                        sc_parts.append(f"{s.replace('_',' ').title()} ∈ [{', '.join(map(str, vals))}]")
            if sc_parts:
                parts.append("Shelf mapping: " + "; ".join(sc_parts))

    if parts:
        return "; ".join(parts)
    else:
        return f"Applies to {len(flagged_df)} SKU(s); no single-value metadata profile detected."

# Build constraint impact dataframe using ORIGINAL LOGIC
constraint_cols = [c for c in sku_constraints.columns if c.startswith("Constraint_")]
constraint_impact = []

for col in constraint_cols:
    flagged_skus = final_df[final_df.get(col, 0) == 1]
    if not flagged_skus.empty:
        units_lost = float(flagged_skus["unit_diff"].sum())
        revenue_lost = float(flagged_skus["revenue_diff"].sum())
        volume_lost = float(flagged_skus["volume_diff_ltr"].sum())
        # Use original build_natural_profile function
        natural_profile = build_natural_profile(flagged_skus, constraint_col=col)
        # constraint_types metadata if exists
        c_row = constraint_types[constraint_types.get("Constraint_ID", "") == col] if "Constraint_ID" in constraint_types.columns else pd.DataFrame()
        c_type = c_row["Constraint_Type"].values[0] if not c_row.empty and "Constraint_Type" in c_row.columns else "-"
        space_perc = c_row["Space_Perc"].values[0] if not c_row.empty and "Space_Perc" in c_row.columns else ""

        constraint_impact.append({
            "Constraint_ID": col,
            "Profile": natural_profile,  # This matches original 'Constraint_Profile' logic
            "Type": c_type,
            "Space_Limit_%": space_perc,
            "Units_Lost": units_lost,
            "Revenue_Lost": revenue_lost,
            "Volume_Lost_Ltr": volume_lost,
            "SKUs_Affected": len(flagged_skus)
        })

impact_df = pd.DataFrame(constraint_impact).sort_values("Revenue_Lost", ascending=False) if constraint_impact else pd.DataFrame()

# ---------------------- Enhanced Analytics Dashboard ----------------------
st.markdown("## 📊 Executive Dashboard")

# Key metrics in enhanced layout
col1, col2, col3, col4 = st.columns(4)

total_revenue_lost = final_df["revenue_diff"].sum()
total_units_lost = final_df["unit_diff"].sum()
total_volume_lost = final_df["volume_diff_ltr"].sum()
skus_affected = (final_df["revenue_diff"] > 0).sum()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>💰 Revenue Impact</h3>
        <h2>₹{total_revenue_lost:,.0f}</h2>
        <p>Total lost due to constraints</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📦 Units Impact</h3>
        <h2>{total_units_lost:,.0f}</h2>
        <p>Units lost to constraints</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🥤 Volume Impact</h3>
        <h2>{total_volume_lost:,.0f}L</h2>
        <p>Volume lost to constraints</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 SKUs Affected</h3>
        <h2>{skus_affected}</h2>
        <p>Products impacted negatively</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------- Market Intelligence Analysis ----------------------
if include_market_trends:
    st.markdown("## 🌍 Market Intelligence")

    market_metrics = calculate_market_metrics(final_df, competitive_focus)

    if 'brand_performance' in market_metrics:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Brand Performance")
            brand_perf = market_metrics['brand_performance'].sort_values('revenue_share', ascending=False)

            fig = px.pie(
                brand_perf,
                values='revenue_share',
                names='brand_family',
                title="Market Share by Brand (Constrained Scenario)",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("💵 Price Positioning")
            fig = px.scatter(
                brand_perf,
                x='units_con',
                y='avg_price_per_unit',
                size='revenue_con',
                hover_name='brand_family',
                title="Volume vs Price Positioning",
                labels={'units_con': 'Units Sold', 'avg_price_per_unit': 'Avg Price per Unit (₹)'}
            )
            st.plotly_chart(fig, use_container_width=True)

# ---------------------- Constraint Impact Analysis ----------------------
st.markdown("## 🔍 Constraint Impact Analysis")

# Build constraint impact dataframe
constraint_cols = [c for c in sku_constraints.columns if c.startswith("Constraint_")]
constraint_impact = []

for col in constraint_cols:
    flagged_skus = final_df[final_df.get(col, 0) == 1]
    if not flagged_skus.empty:
        # Build natural language profile
        profile_parts = []
        for meta_col in ["manufacturer", "brand_family", "pack_qty"]:
            if meta_col in flagged_skus.columns:
                unique_vals = flagged_skus[meta_col].dropna().unique()
                if len(unique_vals) == 1:
                    profile_parts.append(f"{meta_col.replace('_', ' ').title()}: {unique_vals[0]}")

        profile = "; ".join(profile_parts) if profile_parts else f"{len(flagged_skus)} SKUs affected"

        # Get constraint details
        constraint_info = constraint_types[
            constraint_types.get("Constraint_ID", "") == col
        ] if "Constraint_ID" in constraint_types.columns else pd.DataFrame()

        constraint_type = constraint_info["Constraint_Type"].iloc[0] if not constraint_info.empty else "Unknown"
        space_limit = constraint_info.get("Space_Perc", pd.Series([None])).iloc[0] if not constraint_info.empty else None

        constraint_impact.append({
            "Constraint_ID": col,
            "Profile": profile,
            "Type": constraint_type,
            "Space_Limit_%": space_limit,
            "Units_Lost": flagged_skus["unit_diff"].sum(),
            "Revenue_Lost": flagged_skus["revenue_diff"].sum(),
            "Volume_Lost_Ltr": flagged_skus["volume_diff_ltr"].sum(),
            "SKUs_Affected": len(flagged_skus)
        })

impact_df = pd.DataFrame(constraint_impact).sort_values("Revenue_Lost", ascending=False)

# Enhanced constraint visualization
if not impact_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💸 Revenue Impact by Constraint")
        fig = px.bar(
            impact_df.head(10),
            x="Revenue_Lost",
            y="Profile",
            orientation='h',
            title="Top 10 Constraints by Revenue Loss",
            color="Revenue_Lost",
            color_continuous_scale="Reds"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📦 Volume Impact by Constraint")
        fig = px.bar(
            impact_df.head(10),
            x="Volume_Lost_Ltr",
            y="Profile",
            orientation='h',
            title="Top 10 Constraints by Volume Loss",
            color="Volume_Lost_Ltr",
            color_continuous_scale="Blues"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ---------------------- Brand-Level Executive Summary Generation ----------------------
def generate_brand_executive_summary(final_df, impact_df):
    """Generate brand-level executive summary with market intelligence"""
    summary = {
        'brand_analysis': [],
        'recommendations': [],
        'anomalies': [],
        'overall_summary': ""
    }

    if 'manufacturer' not in final_df.columns and 'brand_family' not in final_df.columns:
        return summary

    # Brand-level analysis
    brand_col = 'manufacturer' if 'manufacturer' in final_df.columns else 'brand_family'
    brand_analysis = final_df.groupby(brand_col).agg({
        'revenue_diff': ['sum', 'count'],
        'unit_diff': 'sum',
        'volume_diff_ltr': 'sum'
    }).round(2)

    brand_analysis.columns = ['revenue_loss_total', 'sku_count', 'unit_loss_total', 'volume_loss_total']
    brand_analysis = brand_analysis.reset_index().sort_values('revenue_loss_total', ascending=False)

    # Find top losing SKU per brand
    top_losing_skus = final_df.loc[final_df.groupby(brand_col)['revenue_diff'].idxmax()].dropna()

    for _, brand_row in brand_analysis.iterrows():
        brand_name = brand_row[brand_col]
        revenue_loss = brand_row['revenue_loss_total']
        unit_loss = brand_row['unit_loss_total']
        volume_loss = brand_row['volume_loss_total']
        sku_count = int(brand_row['sku_count'])

        # Find top losing SKU for this brand
        brand_top_sku = top_losing_skus[top_losing_skus[brand_col] == brand_name]
        top_sku_info = ""
        if not brand_top_sku.empty:
            top_sku_row = brand_top_sku.iloc[0]
            if 'sku' in top_sku_row and top_sku_row['revenue_diff'] > 0:
                top_sku_info = f" (₹{top_sku_row['revenue_diff']:.2f} from SKU {top_sku_row['sku']})"

        if abs(revenue_loss) > 50 or abs(unit_loss) > 10:  # Significant impact
            analysis_text = f"**{brand_name}** has "

            if revenue_loss > 0:
                analysis_text += f"revenue loss of ₹{revenue_loss:.2f}{top_sku_info}"
            elif revenue_loss < 0:
                analysis_text += f"revenue gain of ₹{abs(revenue_loss):.2f}"

            if volume_loss > 0:
                analysis_text += f" and volume loss of {volume_loss:.2f} liters"
            elif volume_loss < 0:
                analysis_text += f" and volume gain of {abs(volume_loss):.2f} liters"

            if unit_loss < 0:
                analysis_text += f". Shows unit gain of {abs(unit_loss):.0f}, indicating potential opportunities"
            elif unit_loss > 0:
                analysis_text += f". Unit loss of {unit_loss:.0f} across {sku_count} SKUs"

            analysis_text += "."
            summary['brand_analysis'].append(analysis_text)

    # Generate recommendations based on patterns
    top_loser = brand_analysis.iloc[0] if not brand_analysis.empty else None
    if top_loser is not None and top_loser['revenue_loss_total'] > 100:
        brand_name = top_loser[brand_col]
        summary['recommendations'].append(
            f"**Focus on {brand_name}** to address significant revenue and volume losses. "
            f"Strategies could include revising pricing, promotional strategies, or shelf allocation to mitigate ₹{top_loser['revenue_loss_total']:.0f} loss."
        )

    # Pack-related recommendations from constraint analysis
    if not impact_df.empty:
        pack_constraints = impact_df[impact_df['Profile'].str.contains('Pack|pack', case=False, na=False)]
        if not pack_constraints.empty and pack_constraints['Revenue_Lost'].sum() > 100:
            summary['recommendations'].append(
                f"**Investigate Pack Size Constraints** causing substantial losses. "
                f"Consider adjusting pack sizes or configurations to improve sales and recover ₹{pack_constraints['Revenue_Lost'].sum():.0f}."
            )

    # Identify anomalies (gains)
    gaining_brands = brand_analysis[brand_analysis['revenue_loss_total'] < 0]
    for _, brand_row in gaining_brands.iterrows():
        brand_name = brand_row[brand_col]
        revenue_gain = abs(brand_row['revenue_loss_total'])
        unit_change = brand_row['unit_loss_total']

        anomaly_text = f"**{brand_name}** shows revenue gain of ₹{revenue_gain:.0f}"
        if unit_change < 0:
            anomaly_text += f" and unit gain of {abs(unit_change):.0f}, which is atypical and may indicate optimization opportunities"
        anomaly_text += " rather than constraint issues."

        summary['anomalies'].append(anomaly_text)

    # Generate overall summary
    if not brand_analysis.empty:
        most_impacted = brand_analysis.iloc[0][brand_col]
        total_loss = brand_analysis[brand_analysis['revenue_loss_total'] > 0]['revenue_loss_total'].sum()
        gaining_count = len(gaining_brands)

        summary['overall_summary'] = f"The analysis indicates that constraints related to **{most_impacted}** are the most damaging in terms of revenue loss (₹{brand_analysis.iloc[0]['revenue_loss_total']:.0f}). "

        if gaining_count > 0:
            summary['overall_summary'] += f"There are {gaining_count} brand(s) showing gains, indicating optimization opportunities. "

        summary['overall_summary'] += "Addressing these priority areas through strategic shelf allocation and constraint optimization could lead to improved overall performance."

    return summary

def generate_executive_summary(impact_df, final_df, threshold_config):
    """Generate detailed executive summary similar to previous version"""
    summary = {
        'units_analysis': [],
        'revenue_analysis': [],
        'volume_analysis': [],
        'manufacturer_patterns': [],
        'recommendations': [],
        'anomalies': []
    }

    if impact_df.empty:
        return summary

    # Units Analysis
    top_units_lost = impact_df.nlargest(3, 'Units_Lost')
    for _, row in top_units_lost.iterrows():
        if row['Units_Lost'] > 0:
            summary['units_analysis'].append({
                'constraint': row['Profile'],
                'constraint_id': row['Constraint_ID'],
                'units_lost': row['Units_Lost'],
                'description': f"{row['Constraint_ID']} ({row['Profile']}) has units lost of {row['Units_Lost']:.2f}"
            })

    # Revenue Analysis
    top_revenue_lost = impact_df.nlargest(3, 'Revenue_Lost')
    for _, row in top_revenue_lost.iterrows():
        if row['Revenue_Lost'] > 0:
            summary['revenue_analysis'].append({
                'constraint': row['Profile'],
                'constraint_id': row['Constraint_ID'],
                'revenue_lost': row['Revenue_Lost'],
                'description': f"{row['Constraint_ID']} ({row['Profile']}) shows significant revenue loss of ₹{row['Revenue_Lost']:.2f}"
            })

    # Volume Analysis
    top_volume_lost = impact_df.nlargest(3, 'Volume_Lost_Ltr')
    for _, row in top_volume_lost.iterrows():
        if row['Volume_Lost_Ltr'] > 0:
            summary['volume_analysis'].append({
                'constraint': row['Profile'],
                'constraint_id': row['Constraint_ID'],
                'volume_lost': row['Volume_Lost_Ltr'],
                'description': f"{row['Constraint_ID']} ({row['Profile']}) has the highest volume lost at {row['Volume_Lost_Ltr']:.2f} liters"
            })

    # Manufacturer/Brand Patterns
    if 'manufacturer' in final_df.columns:
        mfg_analysis = final_df.groupby('manufacturer').agg({
            'revenue_diff': 'sum',
            'unit_diff': 'sum',
            'volume_diff_ltr': 'sum'
        }).reset_index().sort_values('revenue_diff', ascending=False)

        for _, mfg in mfg_analysis.iterrows():
            if abs(mfg['revenue_diff']) > threshold_config['revenue'] * 0.1:  # 10% of threshold
                pattern_desc = f"{mfg['manufacturer']} shows "
                if mfg['revenue_diff'] > 0:
                    pattern_desc += f"revenue loss of ₹{mfg['revenue_diff']:.2f}"
                else:
                    pattern_desc += f"revenue gain of ₹{abs(mfg['revenue_diff']):.2f}"

                if mfg['unit_diff'] < 0:
                    pattern_desc += f" and unit gain of {abs(mfg['unit_diff']):.0f}, indicating potential opportunities"
                elif mfg['unit_diff'] > 0:
                    pattern_desc += f" and unit loss of {mfg['unit_diff']:.0f}"

                summary['manufacturer_patterns'].append(pattern_desc)

    # Generate Recommendations
    critical_revenue = impact_df[impact_df['Revenue_Lost'] > threshold_config['revenue']].nlargest(2, 'Revenue_Lost')
    for _, row in critical_revenue.iterrows():
        if 'Heineken' in row['Profile'] or 'heineken' in row['Profile'].lower():
            summary['recommendations'].append(
                f"Focus on {row['Constraint_ID']} ({row['Profile']}) to address significant revenue and volume losses. "
                f"Strategies could include revising pricing or promotional strategies to mitigate ₹{row['Revenue_Lost']:.0f} loss."
            )
        elif 'Pack' in row['Profile'] or 'pack' in row['Profile'].lower():
            summary['recommendations'].append(
                f"Investigate {row['Constraint_ID']} ({row['Profile']}) causing substantial losses. "
                f"Consider adjusting pack sizes or configurations to improve sales and recover ₹{row['Revenue_Lost']:.0f}."
            )
        else:
            summary['recommendations'].append(
                f"Address {row['Constraint_ID']} ({row['Profile']}) showing ₹{row['Revenue_Lost']:.0f} revenue loss. "
                f"Review constraint implementation and optimization strategies."
            )

    # Identify Anomalies (negative losses = gains)
    gains = impact_df[impact_df['Revenue_Lost'] < 0]
    for _, row in gains.iterrows():
        summary['anomalies'].append(
            f"{row['Constraint_ID']} ({row['Profile']}) shows revenue gain of ₹{abs(row['Revenue_Lost']):.0f}, "
            f"which indicates an opportunity area rather than a constraint issue. Consider expanding this constraint implementation."
        )

    # Check for unusual patterns
    unusual_units = impact_df[impact_df['Units_Lost'] < -100]  # Large unit gains
    for _, row in unusual_units.iterrows():
        summary['anomalies'].append(
            f"{row['Constraint_ID']} shows unusual unit gain of {abs(row['Units_Lost']):.0f}, "
            f"which may indicate optimization opportunities that could be leveraged further."
        )

    return summary

# ---------------------- Strategic Insights Generation ----------------------
st.markdown("## 📋 Executive Summary")

threshold_config = {
    'revenue': revenue_threshold,
    'volume': volume_threshold,
    'units': unit_threshold
}

# Generate brand-level executive summary
brand_summary = generate_brand_executive_summary(final_df, impact_df)

# Display Brand-Level Executive Summary
if brand_summary['brand_analysis'] or brand_summary['recommendations'] or brand_summary['anomalies']:
    st.subheader("📈 Brand-Level Market Intelligence")

    # Brand Analysis
    if brand_summary['brand_analysis']:
        st.markdown("**Brand Performance Analysis:**")
        for analysis in brand_summary['brand_analysis']:
            st.markdown(f"• {analysis}")
        st.markdown("")

    # Recommendations
    if brand_summary['recommendations']:
        st.markdown("**Recommendations for Optimization:**")
        for recommendation in brand_summary['recommendations']:
            st.markdown(f"• {recommendation}")
        st.markdown("")

    # Anomalies
    if brand_summary['anomalies']:
        st.markdown("**Anomalies Worth Flagging:**")
        for anomaly in brand_summary['anomalies']:
            st.markdown(f"• {anomaly}")
        st.markdown("")

    # Overall Summary
    if brand_summary['overall_summary']:
        st.markdown("**Summary:**")
        st.markdown(f"{brand_summary['overall_summary']}")

    st.markdown("---")

# Generate detailed executive summary
exec_summary = generate_executive_summary(impact_df, final_df, threshold_config)

# Display Detailed Executive Summary
if not impact_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        # Units Lost Analysis
        if exec_summary['units_analysis']:
            st.subheader("📦 Units Lost Analysis")
            for analysis in exec_summary['units_analysis']:
                st.markdown(f"• **{analysis['constraint_id']}** ({analysis['constraint']}): **{analysis['units_lost']:,.0f} units lost**")

        # Revenue Lost Analysis
        if exec_summary['revenue_analysis']:
            st.subheader("💰 Revenue Lost Analysis")
            for analysis in exec_summary['revenue_analysis']:
                st.markdown(f"• **{analysis['constraint_id']}** ({analysis['constraint']}): **₹{analysis['revenue_lost']:,.0f} revenue lost**")

        # Volume Lost Analysis
        if exec_summary['volume_analysis']:
            st.subheader("🥤 Volume Lost Analysis")
            for analysis in exec_summary['volume_analysis']:
                st.markdown(f"• **{analysis['constraint_id']}** ({analysis['constraint']}): **{analysis['volume_lost']:,.0f}L volume lost**")

    with col2:
        # Manufacturer Patterns
        if exec_summary['manufacturer_patterns']:
            st.subheader("🏭 Patterns Across Manufacturers")
            for pattern in exec_summary['manufacturer_patterns']:
                st.markdown(f"• {pattern}")

        # Anomalies
        if exec_summary['anomalies']:
            st.subheader("⚠️ Anomalies Worth Flagging")
            for anomaly in exec_summary['anomalies']:
                st.markdown(f"• {anomaly}")

    # Recommendations (full width)
    if exec_summary['recommendations']:
        st.subheader("🎯 Recommendations for Optimization")
        for i, recommendation in enumerate(exec_summary['recommendations'], 1):
            st.markdown(f"""
            <div class="recommendation-card">
                <h4>Recommendation {i}</h4>
                <p>{recommendation}</p>
            </div>
            """, unsafe_allow_html=True)

    # Overall Summary
    st.subheader("📊 Summary")

    # Generate dynamic summary based on data
    top_revenue_constraint = impact_df.nlargest(1, 'Revenue_Lost').iloc[0] if not impact_df.empty else None
    top_volume_constraint = impact_df.nlargest(1, 'Volume_Lost_Ltr').iloc[0] if not impact_df.empty else None

    if top_revenue_constraint is not None:
        summary_text = f"""
        The analysis indicates that **{top_revenue_constraint['Profile']}** constraints are the most damaging
        in terms of revenue loss (₹{top_revenue_constraint['Revenue_Lost']:,.0f}).
        """

        if top_volume_constraint is not None and top_volume_constraint['Constraint_ID'] == top_revenue_constraint['Constraint_ID']:
            summary_text += f"This same constraint also causes the highest volume loss ({top_volume_constraint['Volume_Lost_Ltr']:,.0f}L). "

        gains_count = len(impact_df[impact_df['Revenue_Lost'] < 0])
        if gains_count > 0:
            summary_text += f"There are {gains_count} constraint(s) showing gains, indicating optimization opportunities. "

        summary_text += "Addressing these priority areas could lead to improved overall performance."

        st.markdown(f"""
        <div class="insight-box">
            <p style="font-size: 16px; line-height: 1.6;">{summary_text}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Continue with existing strategic insights
insights = generate_strategic_insights(impact_df, market_metrics, threshold_config)

# Critical Issues
if insights['critical_issues']:
    st.subheader("🚨 Critical Issues Requiring Immediate Attention")
    for issue in insights['critical_issues']:
        severity_class = f"alert-{issue['severity'].lower()}"
        st.markdown(f"""
        <div class="recommendation-card {severity_class}">
            <h4>⚠️ {issue['constraint']}</h4>
            <p><strong>Impact:</strong> {issue['impact']}</p>
            <p><strong>Severity:</strong> {issue['severity']}</p>
        </div>
        """, unsafe_allow_html=True)

# Opportunities
if insights['opportunities']:
    st.subheader("🌟 Identified Opportunities")
    for opp in insights['opportunities']:
        st.markdown(f"""
        <div class="recommendation-card alert-low">
            <h4>💡 {opp['constraint']}</h4>
            <p><strong>Potential:</strong> {opp['gain']}</p>
            <p><strong>Action:</strong> {opp['recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------- AI-Powered Insights ----------------------
if openai_client and st.button("🤖 Generate AI-Powered Strategic Analysis"):
    with st.spinner("🔮 Analyzing patterns and generating insights..."):
        try:
            # Prepare data summary for AI analysis
            top_constraints = impact_df.head(5).to_dict('records')
            brand_summary = final_df.groupby('brand_family').agg({
                'revenue_diff': 'sum',
                'unit_diff': 'sum',
                'volume_diff_ltr': 'sum'
            }).reset_index().to_dict('records')

            prompt = f"""
            As a senior retail optimization consultant for AB InBev, analyze this planogram constraint data and provide strategic insights.

            BUSINESS CONTEXT:
            - This is beer planogram optimization analysis
            - Comparing unconstrained vs constrained scenarios
            - Positive values = losses due to constraints
            - Focus on actionable recommendations for planogrammers

            KEY METRICS:
            - Total Revenue Lost: ₹{total_revenue_lost:,.0f}
            - Total Units Lost: {total_units_lost:,.0f}
            - Total Volume Lost: {total_volume_lost:,.0f}L

            TOP CONSTRAINT IMPACTS:
            {top_constraints}

            BRAND PERFORMANCE:
            {brand_summary}

            PROVIDE:
            1. Executive Summary (2-3 sentences)
            2. Top 3 Strategic Priorities
            3. Specific Action Items for Planogrammers
            4. Competitive Implications
            5. ROI-focused Recommendations

            Format as markdown with clear sections and bullet points.
            """

            response = openai_client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior retail optimization consultant specializing in beer category management and planogram optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            st.markdown("### 🎯 AI Strategic Analysis")
            st.markdown(response.choices[0].message.content)

        except Exception as e:
            st.error(f"AI analysis failed: {e}")

# ---------------------- Interactive Data Explorer ----------------------
st.markdown("## 🔍 Interactive Data Explorer")

# Enhanced agent with business context
if OPENAI_API_KEY:
    try:
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.1, model="gpt-4o-mini")
        agent = create_pandas_dataframe_agent(
            llm,
            final_df,
            verbose=False,
            max_iterations=5,
            allow_dangerous_code=True,
            prefix="""
You are analyzing beer planogram constraint data for AB InBev. Answer questions directly and concisely.

Key columns:
- unit_diff, revenue_diff, volume_diff_ltr: unconstrained minus constrained (positive = loss)
- Constraint_X columns: binary flags (1 = SKU affected by constraint)
- brand_family, manufacturer: Brand information

Rules:
1. Answer questions directly without excessive iteration
2. Use simple pandas operations
3. Provide business context
4. If you can't answer in 3 iterations, say "insufficient data"
            """
        )

        col1, col2 = st.columns([1, 3])

        with col1:
            st.subheader("Quick Queries")
            quick_queries = [
                "Which brands have highest revenue losses?",
                "Show top 10 SKUs by revenue impact",
                "What's the total impact by manufacturer?",
                "Find all constraints affecting premium brands",
                "Which constraints cause volume losses > 100L?"
            ]

            for query in quick_queries:
                if st.button(query, key=f"quick_{query}"):
                    st.session_state['agent_query'] = query

        with col2:
            user_query = st.text_input(
                "Ask about the data:",
                value=st.session_state.get('agent_query', ''),
                placeholder="e.g., Which constraints affect ABI products the most?"
            )

            if st.button("🔍 Analyze") and user_query:
                with st.spinner("Analyzing..."):
                    try:
                        result = agent.run(user_query)
                        st.markdown("### Analysis Result")
                        st.write(result)
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

    except Exception as e:
        st.error(f"Agent initialization failed: {e}")
        st.info("Interactive data explorer not available")

# ---------------------- Export & Actions ----------------------
st.markdown("## 📤 Export & Next Steps")

col1, col2, col3 = st.columns(3)

with col1:
    # Export detailed analysis
    export_df = final_df.copy()

    # Add constraint profiles
    for _, row in impact_df.iterrows():
        constraint_id = row['Constraint_ID']
        profile = row['Profile']
        export_df[f"{constraint_id}_Profile"] = export_df.get(constraint_id, 0).apply(
            lambda x: profile if x == 1 else ""
        )

    csv_data = export_df.to_csv(index=False)
    st.download_button(
        "📊 Download Detailed Analysis",
        csv_data,
        "enhanced_constraint_analysis.csv",
        "text/csv"
    )

with col2:
    # Export executive summary
    summary_data = {
        'Metric': ['Revenue Lost', 'Units Lost', 'Volume Lost', 'SKUs Affected'],
        'Value': [f"₹{total_revenue_lost:,.0f}", f"{total_units_lost:,.0f}",
                 f"{total_volume_lost:,.0f}L", f"{skus_affected}"],
        'Status': ['Critical' if total_revenue_lost > 5000 else 'Monitor',
                  'Critical' if total_units_lost > 1000 else 'Monitor',
                  'Critical' if total_volume_lost > 500 else 'Monitor',
                  'Review']
    }
    summary_df = pd.DataFrame(summary_data)
    summary_csv = summary_df.to_csv(index=False)

    st.download_button(
        "📈 Download Executive Summary",
        summary_csv,
        "executive_summary.csv",
        "text/csv"
    )

with col3:
    # Export top recommendations
    if not impact_df.empty:
        reco_df = impact_df[['Profile', 'Revenue_Lost', 'Volume_Lost_Ltr', 'SKUs_Affected']].head(10)
        reco_df['Priority'] = ['High' if x > revenue_threshold else 'Medium'
                              for x in reco_df['Revenue_Lost']]
        reco_csv = reco_df.to_csv(index=False)

        st.download_button(
            "🎯 Download Recommendations",
            reco_csv,
            "priority_recommendations.csv",
            "text/csv"
        )

# ---------------------- Footer ----------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🎯 Enhanced Constraint Impact Analyzer | Built for AB InBev Planogram Optimization</p>
    <p>💡 Powered by AI-driven insights and market intelligence</p>
</div>
""", unsafe_allow_html=True)