# Constraint Analysis Dashboard - Workflow and Components Documentation

## Overview

The Constraint Impact Analyzer is a Streamlit-based web application that analyzes the impact of various constraints on retail optimization scenarios. It compares constrained vs. unconstrained optimization outputs to identify revenue, volume, and unit losses caused by different constraint types.

## Application Architecture

### Core Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **OpenAI**: AI-powered insights generation
- **LangChain**: Interactive data agent functionality

### Configuration & Setup
- Environment variable loading via `dotenv`
- OpenAI API key validation and client initialization
- Custom styling with lemon-themed UI (`#f2da08` accent color)
- Wide layout configuration with collapsed sidebar

## Workflow Components

### 1. File Upload System

The application requires six specific Excel files to function:

| File Type | Description | Key Columns Expected |
|-----------|-------------|---------------------|
| **Constrained Output** | Optimization results with constraints applied | `sku`, `# units`, `primary_price_per_ltr`, `volume_per_unit` |
| **Unconstrained Output** | Optimization results without constraints | `sku`, `# units`, `primary_price_per_ltr`, `volume_per_unit` |
| **Constraint Types** | Metadata about constraint categories | `Constraint_ID`, `Constraint_Type`, `Space_Perc` |
| **Shelf Constraint Mapping** | Maps constraints to shelf locations | `shelf_id`, `bin_id`, `door_id` + constraint flags |
| **SKU Constraint Mapping** | Maps SKUs to constraint flags | `sku` + `Constraint_*` columns |
| **SKU Metadata** | Product information | `sku`, `manufacturer`, `brand_family`, `pack_type`, `ptc_segment` |

**Features:**
- Simultaneous upload interface with 3-column layout
- File replacement functionality
- Upload status tracking in session state
- Validation for required columns

### 2. Data Processing Pipeline

#### A. Data Validation & Cleaning
```python
# Required columns validation
required_core = ["sku", "# units", "primary_price_per_ltr", "volume_per_unit"]

# Numeric conversion with error handling
df["# units"] = pd.to_numeric(df["# units"], errors="coerce").fillna(0)
```

#### B. Revenue & Volume Calculations
- **Price per unit**: `primary_price_per_ltr × volume_per_unit`
- **Revenue**: `price_per_unit × # units`
- **Total volume**: `volume_per_unit × # units`

#### C. SKU-Level Aggregation
- Groups data by SKU for both constrained and unconstrained scenarios
- Calculates sums for units, revenue, and volume
- Merges datasets to compute differences

#### D. Impact Calculation
```python
merged["unit_diff"] = merged["units_uncon"] - merged["units_con"]
merged["revenue_diff"] = merged["revenue_uncon"] - merged["revenue_con"]
merged["volume_diff_ltr"] = merged["volume_uncon"] - merged["volume_con"]
```

### 3. Constraint Analysis Engine

#### Natural Language Profile Generation
The `build_natural_profile()` function creates human-readable descriptions of constraint impacts by analyzing:

- **Metadata patterns**: Manufacturer, brand family, pack type, PTC segment
- **Location mapping**: Shelf ID, bin ID, door ID from constraint mappings
- **Constraint-specific details**: Cross-references with shelf constraint data

**Example Output**: `"Manufacturer = ABC Corp; Brand Family = Premium; Shelf Id = S001"`

#### Impact Assessment
For each constraint flag column (`Constraint_*`):
1. Identifies affected SKUs
2. Calculates total units, revenue, and volume lost
3. Generates natural language profile
4. Retrieves constraint type metadata
5. Creates impact record with all metrics

### 4. User Interface Components

#### A. Breakdown by Constraint Type
- **Expandable sections** for each constraint
- **Sorted by revenue loss** (highest impact first)
- **Sample SKU display** showing affected products
- **Constraint metadata** (type, width limits)

#### B. Summary Metrics Dashboard
Three-column layout displaying:
- **Total Units Lost**: Aggregated unit differences
- **Total Revenue Lost**: Aggregated revenue differences (₹)
- **Total Volume Lost**: Aggregated volume differences (Liters)

#### C. Data Export
- **CSV download** of complete SKU-level analysis
- **Profile mapping** attached as additional columns
- **Full constraint flagging** preserved

### 5. AI-Powered Analytics

#### A. Interactive Data Agent
**Technology**: LangChain + OpenAI GPT-4o-mini

**Features:**
- **Preset queries** for common analyses
- **Natural language** data exploration
- **Pandas DataFrame** operations
- **Safety guardrails** to prevent unauthorized operations

**Sample Queries:**
- "Top 10 SKUs by revenue_diff"
- "Which constraints cause the largest revenue loss?"
- "Correlation between revenue_diff and unit_diff"

**Agent Context:**
```python
agent_view_cols = meta_cols + numeric_cols + flag_cols
agent_view = agent_df[agent_view_cols].copy()
```

#### B. Batch Insights Generation
**Technology**: OpenAI Chat Completions API

**Process:**
1. Samples top 30 constraint impacts
2. Samples top 20 SKU losses
3. Generates comprehensive prompt with data context
4. Requests structured analysis covering:
   - Most damaging constraint types
   - Patterns across manufacturers/brands
   - Optimization recommendations
   - Anomaly detection

**Safety Measures:**
- Data sampling to manage token limits
- Explicit instructions to use only provided data
- Error handling for API failures

## Key Features

### 1. Robust Data Handling
- **Error-tolerant** file reading with fallback mechanisms
- **Flexible column** detection and validation
- **Missing data** handling with appropriate defaults
- **Type conversion** with error management

### 2. Scalable Architecture
- **Session state** management for file persistence
- **Modular functions** for reusable components
- **Efficient aggregation** using pandas groupby operations
- **Memory-conscious** data processing

### 3. User Experience
- **Clean, modern UI** with custom CSS styling
- **Progressive disclosure** through expandable sections
- **Real-time feedback** on file upload status
- **Intuitive navigation** with clear section headers

### 4. Analysis Capabilities
- **Multi-dimensional impact** assessment (units, revenue, volume)
- **Constraint profiling** with natural language descriptions
- **Interactive exploration** through AI agent
- **Automated insights** generation
- **Export functionality** for further analysis

## Technical Implementation Details

### Data Flow
1. **Upload** → File validation → Session storage
2. **Processing** → Numeric conversion → Revenue/volume calculation
3. **Aggregation** → SKU grouping → Difference calculation
4. **Analysis** → Constraint profiling → Impact assessment
5. **Visualization** → UI rendering → Export generation
6. **AI Integration** → Agent queries → Insight generation

### Error Handling
- **File reading** errors with user-friendly messages
- **Column validation** with specific missing field reporting
- **API failures** with graceful degradation
- **Agent errors** with detailed error reporting

### Performance Considerations
- **Lazy loading** of AI components only when needed
- **Efficient pandas** operations for large datasets
- **Memory management** through selective column processing
- **Caching** via Streamlit session state

## Usage Scenarios

### 1. Retail Space Optimization
- Analyze impact of shelf space constraints on product placement
- Identify high-value products affected by space limitations
- Optimize constraint parameters to maximize revenue

### 2. Supply Chain Analysis
- Evaluate constraint effects on inventory levels
- Assess volume impacts across product categories
- Plan constraint relaxation strategies

### 3. Strategic Planning
- Compare constraint scenarios for business planning
- Identify constraint types with highest business impact
- Generate data-driven recommendations for constraint management

## Future Enhancement Opportunities

1. **Real-time data** integration capabilities
2. **Advanced visualization** with interactive charts
3. **Constraint simulation** tools
4. **Multi-period analysis** support
5. **Automated reporting** generation
6. **Custom constraint** definition interface

This application provides a comprehensive solution for analyzing constraint impacts in retail optimization scenarios, combining robust data processing with AI-powered insights to support data-driven decision making.
