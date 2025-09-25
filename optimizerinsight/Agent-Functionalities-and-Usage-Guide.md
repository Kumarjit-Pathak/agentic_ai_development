# Agent Functionalities and Usage Guide

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Data Analyzer Agent](#data-analyzer-agent)
- [Dashboard Developer Agent](#dashboard-developer-agent)
- [Optimization Expert Agent](#optimization-expert-agent)
- [Data Science Researcher Agent](#data-science-researcher-agent)
- [ML/DL/GenAI Concept Tester Agent](#mldlgenai-concept-tester-agent)
- [Meta Orchestrator Agent](#meta-orchestrator-agent)
- [Hook System Usage](#hook-system-usage)
- [Workflow Examples](#workflow-examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

### System Requirements
- Python 3.8+
- Claude Code SDK
- Required packages: `pandas`, `numpy`, `streamlit`, `openai`, `langchain`

### Basic Usage
```bash
# Test agent routing
echo '{"message": "analyze constraint data"}' | python .claude/hooks/agent-router.py

# Inject context for specific agent
echo '{"message": "build dashboard", "agent_type": "dashboard-developer"}' | python .claude/hooks/context-injector.py

# Validate request security
echo '{"message": "optimize shelf layout"}' | python .claude/hooks/validation-guard.py
```

---

## Data Analyzer Agent

### 🎯 Core Functionalities

#### 1. Excel/CSV Data Processing
**Capability**: Process and analyze Excel files with constraint mappings

**Usage Examples**:
```python
# Trigger phrases for routing:
"Analyze the constraint mapping Excel files"
"Process SKU data from CSV"
"Validate data quality in the spreadsheet"
"Extract insights from constraint_type_mapping.xlsx"
```

**Specific Functions**:
- Load and parse Excel files (`constraint_type_mapping.xlsx`, `sku_constraint_mapping.xlsx`)
- Handle multiple sheets and complex data structures
- Data type validation and conversion
- Missing data identification and handling

#### 2. Constraint Analysis
**Capability**: Analyze retail optimization constraints and relationships

**Usage Examples**:
```python
# Request patterns:
"What constraints apply to SKU placement?"
"Analyze shelf constraint mappings"
"Identify constraint conflicts in the data"
"Generate constraint analysis report"
```

**Specific Functions**:
- Constraint relationship mapping
- Conflict detection between constraints
- Constraint precedence analysis
- Impact assessment of constraint changes

#### 3. Data Quality Assessment
**Capability**: Comprehensive data validation and quality reporting

**Usage Examples**:
```python
# Quality check requests:
"Validate data integrity across all files"
"Check for data inconsistencies"
"Generate data quality report"
"Identify outliers in the constraint data"
```

**Specific Functions**:
- Data completeness checking
- Consistency validation across files
- Outlier detection and flagging
- Data distribution analysis

#### 4. Statistical Analysis
**Capability**: Statistical insights on optimization datasets

**Usage Examples**:
```python
# Statistical analysis requests:
"Provide statistical summary of SKU dimensions"
"Analyze distribution of constraint types"
"Calculate correlation between shelf and SKU constraints"
```

**Specific Functions**:
- Descriptive statistics generation
- Correlation analysis
- Distribution analysis
- Trend identification

### 🔧 Technical Specifications

**Input Formats Supported**:
- Excel files (.xlsx, .xls)
- CSV files (.csv)
- JSON data structures
- Pandas DataFrames

**Output Formats**:
- Structured analysis reports (JSON/Dict)
- Cleaned datasets (DataFrame)
- Validation summaries
- Statistical insights

**Performance Characteristics**:
- Handles files up to 100MB efficiently
- Processes up to 1M rows with optimization
- Memory-efficient streaming for large datasets

---

## Dashboard Developer Agent

### 🎨 Core Functionalities

#### 1. Streamlit Application Development
**Capability**: Build interactive business intelligence dashboards

**Usage Examples**:
```python
# Development requests:
"Create a Streamlit dashboard for constraint analysis"
"Build an interactive visualization interface"
"Develop a dashboard with file upload functionality"
"Create a multi-page Streamlit application"
```

**Specific Functions**:
- Multi-page application structure
- Session state management
- Component layout and organization
- Responsive design implementation

#### 2. Data Visualization
**Capability**: Create compelling charts and interactive visualizations

**Usage Examples**:
```python
# Visualization requests:
"Create charts showing constraint distributions"
"Build interactive plots for SKU analysis"
"Design visualization for shelf optimization results"
"Generate dashboard with KPI metrics"
```

**Specific Functions**:
- Plotly interactive charts
- Matplotlib static visualizations
- Custom chart components
- Real-time data updates

#### 3. User Interface Design
**Capability**: Design intuitive, user-friendly interfaces

**Usage Examples**:
```python
# UI design requests:
"Design clean interface for data upload"
"Create user-friendly control panels"
"Implement intuitive navigation system"
"Build responsive layout for business users"
```

**Specific Functions**:
- Custom CSS styling and theming
- Component styling and branding
- User experience optimization
- Accessibility considerations

#### 4. Performance Optimization
**Capability**: Optimize dashboard performance for large datasets

**Usage Examples**:
```python
# Performance requests:
"Optimize dashboard for large Excel files"
"Implement caching for better performance"
"Add loading states for slow operations"
"Optimize memory usage for data processing"
```

**Specific Functions**:
- Data caching strategies
- Lazy loading implementation
- Memory optimization techniques
- Progressive data loading

### 🔧 Technical Specifications

**Frameworks and Libraries**:
- Streamlit (primary framework)
- Plotly (interactive charts)
- Matplotlib/Seaborn (static charts)
- Custom CSS/HTML components

**UI Components**:
- File upload widgets
- Data tables and grids
- Interactive filters and controls
- Progress indicators and loading states

**Performance Features**:
- Session state caching
- Data memoization
- Asynchronous operations
- Progressive loading

---

## Optimization Expert Agent

### 🔬 Core Functionalities

#### 1. Mathematical Modeling
**Capability**: Formulate mathematical models for optimization problems

**Usage Examples**:
```python
# Modeling requests:
"Create mathematical model for shelf optimization"
"Formulate constraint satisfaction problem"
"Design linear programming model for SKU placement"
"Model multi-objective optimization problem"
```

**Specific Functions**:
- Problem formulation and variable definition
- Constraint equation development
- Objective function design
- Model validation and testing

#### 2. Algorithm Implementation
**Capability**: Implement and customize optimization algorithms

**Usage Examples**:
```python
# Algorithm requests:
"Implement genetic algorithm for shelf layout"
"Create custom constraint solver"
"Develop heuristic optimization approach"
"Build metaheuristic for complex constraints"
```

**Specific Functions**:
- Classical optimization algorithms
- Metaheuristic implementations
- Custom algorithm development
- Algorithm parameter tuning

#### 3. Constraint Problem Solving
**Capability**: Solve complex constraint satisfaction problems

**Usage Examples**:
```python
# Problem solving requests:
"Solve shelf space allocation problem"
"Optimize SKU placement with constraints"
"Find feasible solutions for constraint conflicts"
"Generate optimal layout configurations"
```

**Specific Functions**:
- Constraint satisfaction solving
- Feasibility analysis
- Solution space exploration
- Multi-objective optimization

#### 4. Solution Validation
**Capability**: Validate and analyze optimization solutions

**Usage Examples**:
```python
# Validation requests:
"Validate optimization solution quality"
"Analyze solution robustness"
"Compare different optimization approaches"
"Assess solution sensitivity to parameter changes"
```

**Specific Functions**:
- Solution quality assessment
- Sensitivity analysis
- Robustness testing
- Performance benchmarking

### 🔧 Technical Specifications

**Optimization Libraries**:
- PuLP (linear programming)
- OR-Tools (constraint programming)
- CVXPY (convex optimization)
- SciPy (scientific optimization)

**Problem Types Supported**:
- Linear Programming (LP)
- Integer Programming (IP)
- Constraint Satisfaction Problems (CSP)
- Multi-objective optimization

**Solution Methods**:
- Exact algorithms (branch-and-bound, simplex)
- Heuristic methods (genetic algorithms, simulated annealing)
- Hybrid approaches (matheuristics)

---

## Data Science Researcher Agent

### 🔬 Core Functionalities

#### 1. Advanced Mathematical Modeling
**Capability**: Develop sophisticated mathematical models for complex data science problems

**Usage Examples**:
```python
# Trigger phrases for routing:
"Research advanced statistical models for demand forecasting"
"Develop Bayesian inference model for constraint optimization"
"Create stochastic model for inventory management"
"Design experimental framework for A/B testing"
```

**Specific Functions**:
- Stochastic modeling and probabilistic analysis
- Bayesian inference and statistical modeling
- Time series analysis and forecasting
- Advanced regression techniques and mixed-effects models
- Experimental design and hypothesis testing

#### 2. Research Methodology
**Capability**: Apply rigorous research methodologies to business problems

**Usage Examples**:
```python
# Research methodology requests:
"Conduct literature review on retail optimization methods"
"Design experimental study for pricing optimization"
"Perform meta-analysis of demand forecasting approaches"
"Develop research framework for constraint analysis"
```

**Specific Functions**:
- Literature review and state-of-the-art analysis
- Research question formulation and hypothesis development
- Statistical significance testing and power analysis
- Causal inference and econometric methods
- Reproducible research practices

#### 3. Advanced Statistical Analysis
**Capability**: Perform sophisticated statistical analysis beyond traditional methods

**Usage Examples**:
```python
# Advanced statistics requests:
"Perform survival analysis on customer retention data"
"Apply non-parametric methods to constraint data"
"Conduct multivariate statistical analysis"
"Implement bootstrap confidence intervals"
```

**Specific Functions**:
- Advanced regression techniques (Ridge, Lasso, Elastic Net)
- Generalized Linear Models and Mixed Effects Models
- Survival analysis and hazard modeling
- Non-parametric methods and robust statistics
- Bootstrap and permutation testing

#### 4. Academic-Level Documentation
**Capability**: Produce peer-review quality research documentation

**Usage Examples**:
```python
# Documentation requests:
"Create research report with mathematical rigor"
"Document methodology for reproducible research"
"Prepare academic-style analysis with citations"
"Generate statistical validation report"
```

**Specific Functions**:
- Mathematical notation and formal proofs
- Statistical methodology documentation
- Peer-review quality writing and analysis
- Reproducibility requirements and validation

### 🔧 Technical Specifications

**Research Frameworks**:
- SciPy ecosystem for scientific computing
- Statsmodels for statistical modeling
- PyMC for Bayesian analysis
- NetworkX for graph analysis
- SymPy for symbolic mathematics

**Research Output Types**:
- Comprehensive research reports
- Statistical validation frameworks
- Mathematical model specifications
- Reproducible research notebooks
- Academic-quality documentation

**Validation Standards**:
- Statistical significance testing
- Cross-validation and out-of-sample testing
- Sensitivity analysis and robustness checks
- Peer review methodology validation

---

## ML/DL/GenAI Concept Tester Agent

### 🤖 Core Functionalities

#### 1. Machine Learning Experimentation
**Capability**: Test and validate machine learning concepts and algorithms

**Usage Examples**:
```python
# ML experimentation requests:
"Test XGBoost vs Random Forest for demand prediction"
"Experiment with ensemble methods for constraint optimization"
"Compare classical ML approaches for retail analytics"
"Validate feature selection techniques"
```

**Specific Functions**:
- Classical ML algorithm evaluation and comparison
- Feature engineering and selection optimization
- Hyperparameter tuning and optimization
- Cross-validation and model selection
- Ensemble methods and model stacking

#### 2. Deep Learning Innovation
**Capability**: Experiment with neural networks and deep learning architectures

**Usage Examples**:
```python
# Deep learning requests:
"Test LSTM networks for time series forecasting"
"Experiment with transformer models for sequence data"
"Compare CNN architectures for image-based analytics"
"Validate attention mechanisms for constraint modeling"
```

**Specific Functions**:
- Neural network architecture design and testing
- Transfer learning and fine-tuning strategies
- Computer vision and image processing applications
- Natural language processing and text analytics
- Reinforcement learning for optimization problems

#### 3. Generative AI Applications
**Capability**: Test and implement cutting-edge generative AI solutions

**Usage Examples**:
```python
# GenAI testing requests:
"Test LLM for automated report generation"
"Experiment with RAG systems for business intelligence"
"Validate prompt engineering approaches"
"Test AI agents for workflow automation"
```

**Specific Functions**:
- Large Language Model integration and fine-tuning
- Prompt engineering and chain-of-thought reasoning
- Retrieval Augmented Generation (RAG) systems
- AI agent orchestration and tool usage
- Creative problem-solving with generative models

#### 4. Model Validation and MLOps
**Capability**: Comprehensive model testing and production readiness assessment

**Usage Examples**:
```python
# MLOps and validation requests:
"Validate model performance across different datasets"
"Test model deployment pipeline"
"Assess model drift detection systems"
"Benchmark model serving performance"
```

**Specific Functions**:
- Multi-metric model assessment
- Business metric alignment
- Computational efficiency analysis
- Robustness testing and adversarial validation
- Production deployment testing

### 🔧 Technical Specifications

**ML Frameworks**:
- Scikit-learn for classical ML
- XGBoost/LightGBM/CatBoost for gradient boosting
- Optuna/Hyperopt for hyperparameter optimization
- MLflow for experiment tracking
- SHAP/LIME for model interpretability

**Deep Learning Frameworks**:
- PyTorch for dynamic neural networks
- TensorFlow/Keras for production deployment
- Transformers (Hugging Face) for pre-trained models
- Lightning for scalable training
- Ray for distributed computing

**GenAI Platforms**:
- OpenAI API for GPT models
- Anthropic Claude for advanced reasoning
- LangChain for LLM applications
- LlamaIndex for data retrieval systems
- Streamlit for interactive AI apps

**Validation Methods**:
- Cross-validation (K-fold, stratified, time series)
- Holdout testing with separate test sets
- Bootstrap sampling for confidence intervals
- Ablation studies and sensitivity analysis
- A/B testing frameworks for production validation

---

## Meta Orchestrator Agent

### 🎭 Core Functionalities

#### 1. Agent Coordination
**Capability**: Coordinate multiple specialized agents for complex workflows

**Usage Examples**:
```python
# Coordination requests:
"Coordinate data analysis and dashboard creation"
"Manage workflow from data processing to optimization"
"Orchestrate multi-step analysis pipeline"
"Coordinate agents for comprehensive solution"
```

**Specific Functions**:
- Agent selection and routing
- Task decomposition and assignment
- Inter-agent communication management
- Workflow execution coordination

#### 2. Complex Task Management
**Capability**: Break down and manage complex multi-step tasks

**Usage Examples**:
```python
# Complex task requests:
"Complete end-to-end optimization analysis"
"Build comprehensive constraint analysis system"
"Create full business intelligence solution"
"Implement complete optimization workflow"
```

**Specific Functions**:
- Task complexity assessment
- Sequential and parallel task planning
- Dependency management
- Progress tracking and reporting

#### 3. Quality Assurance
**Capability**: Ensure consistency and quality across all agent outputs

**Usage Examples**:
```python
# Quality assurance requests:
"Validate integrated solution quality"
"Ensure consistency across agent outputs"
"Review and synthesize agent recommendations"
"Coordinate quality checks across workflow"
```

**Specific Functions**:
- Cross-agent validation
- Output consistency checking
- Quality metric aggregation
- Integration testing coordination

#### 4. Strategic Guidance
**Capability**: Provide high-level strategic guidance and decision support

**Usage Examples**:
```python
# Strategic requests:
"Recommend optimal approach for constraint analysis"
"Guide technology selection for optimization project"
"Provide strategic roadmap for system development"
"Advise on agent ecosystem improvements"
```

**Specific Functions**:
- Technology selection guidance
- Architecture decision support
- Strategic planning assistance
- System evolution recommendations

### 🔧 Technical Specifications

**Coordination Capabilities**:
- Multi-agent task orchestration
- Dynamic agent selection
- Workflow state management
- Error handling and recovery

**Communication Protocols**:
- Agent-to-agent messaging
- Result aggregation and synthesis
- Context sharing mechanisms
- Status reporting systems

---

## Hook System Usage

### Agent Router Hook

**Purpose**: Automatically route requests to appropriate agents

**Input Format**:
```json
{
  "message": "Your request message here",
  "context": "Optional context information"
}
```

**Output Format**:
```json
{
  "agent_routing": {
    "primary_agent": "data-analyzer",
    "secondary_agents": ["optimization-expert"],
    "reasoning": "Detected data analysis and optimization needs"
  },
  "timestamp": "2025-09-25",
  "hook": "agent-router"
}
```

**Usage Examples**:
```bash
# Data analysis routing
echo '{"message": "analyze Excel constraint files"}' | python .claude/hooks/agent-router.py

# Dashboard development routing
echo '{"message": "create Streamlit visualization"}' | python .claude/hooks/agent-router.py

# Optimization routing
echo '{"message": "solve constraint satisfaction problem"}' | python .claude/hooks/agent-router.py
```

### Context Injector Hook

**Purpose**: Inject relevant project context for agent specialization

**Input Format**:
```json
{
  "message": "Your request message",
  "agent_type": "target_agent_type"
}
```

**Output Format**:
```json
{
  "enhanced_message": "Context + original message",
  "context_injected": true,
  "agent_type": "dashboard-developer",
  "hook": "context-injector"
}
```

**Usage Examples**:
```bash
# Inject context for data analysis
echo '{"message": "process constraints", "agent_type": "data-analyzer"}' | python .claude/hooks/context-injector.py

# Inject context for dashboard development
echo '{"message": "build interface", "agent_type": "dashboard-developer"}' | python .claude/hooks/context-injector.py
```

### Validation Guard Hook

**Purpose**: Validate security and quality of requests and responses

**Input Format**:
```json
{
  "message": "Content to validate",
  "type": "request",
  "agent_type": "target_agent"
}
```

**Output Format**:
```json
{
  "valid": true,
  "security": {"secure": true, "issues": []},
  "requirements": {"valid": true, "missing_fields": []},
  "agent_type": "data-analyzer"
}
```

**Usage Examples**:
```bash
# Validate request security
echo '{"message": "process data files", "type": "request"}' | python .claude/hooks/validation-guard.py

# Validate response quality
echo '{"response": "generated code", "type": "response", "agent_type": "dashboard-developer"}' | python .claude/hooks/validation-guard.py
```

---

## Workflow Examples

### Complete Data Analysis Workflow

```bash
# Step 1: Route request
echo '{"message": "analyze constraint mapping files and create dashboard"}' | python .claude/hooks/agent-router.py

# Step 2: Process with data analyzer
echo '{"message": "analyze constraint_type_mapping.xlsx", "agent_type": "data-analyzer"}' | python .claude/hooks/context-injector.py

# Step 3: Create dashboard
echo '{"message": "create dashboard for constraint analysis", "agent_type": "dashboard-developer"}' | python .claude/hooks/context-injector.py

# Step 4: Validate outputs
echo '{"response": "dashboard code", "type": "response", "agent_type": "dashboard-developer"}' | python .claude/hooks/validation-guard.py
```

### Optimization Problem Solving Workflow

```bash
# Step 1: Route complex optimization request
echo '{"message": "solve shelf space optimization with multiple constraints"}' | python .claude/hooks/agent-router.py

# Step 2: Coordinate multiple agents
echo '{"message": "coordinate optimization workflow", "agent_type": "meta-orchestrator"}' | python .claude/hooks/context-injector.py

# Step 3: Data analysis phase
echo '{"message": "analyze constraint data for optimization", "agent_type": "data-analyzer"}' | python .claude/hooks/context-injector.py

# Step 4: Optimization modeling
echo '{"message": "create mathematical model for shelf optimization", "agent_type": "optimization-expert"}' | python .claude/hooks/context-injector.py

# Step 5: Results visualization
echo '{"message": "visualize optimization results", "agent_type": "dashboard-developer"}' | python .claude/hooks/context-injector.py
```

### Advanced AI/ML Research Workflow

```bash
# Step 1: Research problem identification
echo '{"message": "research advanced ML methods for retail optimization"}' | python .claude/hooks/agent-router.py

# Step 2: Literature review and methodology
echo '{"message": "conduct literature review on deep learning for optimization", "agent_type": "data-science-researcher"}' | python .claude/hooks/context-injector.py

# Step 3: Concept testing and experimentation
echo '{"message": "test neural networks for constraint optimization", "agent_type": "ml-concept-tester"}' | python .claude/hooks/context-injector.py

# Step 4: Statistical validation
echo '{"message": "validate ML results with statistical significance tests", "agent_type": "data-science-researcher"}' | python .claude/hooks/context-injector.py

# Step 5: Implementation and deployment
echo '{"message": "create production ML pipeline", "agent_type": "ml-concept-tester"}' | python .claude/hooks/context-injector.py
```

### Multi-Agent AI Research Pipeline

```bash
# Step 1: Coordinate comprehensive AI research project
echo '{"message": "coordinate AI research for retail optimization", "agent_type": "meta-orchestrator"}' | python .claude/hooks/context-injector.py

# Step 2: Research foundation
echo '{"message": "establish theoretical foundation for AI-driven optimization", "agent_type": "data-science-researcher"}' | python .claude/hooks/context-injector.py

# Step 3: Data preparation
echo '{"message": "prepare data for AI model training", "agent_type": "data-analyzer"}' | python .claude/hooks/context-injector.py

# Step 4: AI experimentation
echo '{"message": "experiment with GenAI for automated optimization", "agent_type": "ml-concept-tester"}' | python .claude/hooks/context-injector.py

# Step 5: Mathematical validation
echo '{"message": "validate AI results with mathematical rigor", "agent_type": "optimization-expert"}' | python .claude/hooks/context-injector.py

# Step 6: Interactive demonstration
echo '{"message": "create AI demonstration dashboard", "agent_type": "dashboard-developer"}' | python .claude/hooks/context-injector.py
```

---

## Troubleshooting

### Common Issues and Solutions

#### Agent Routing Problems

**Issue**: Agent router not selecting appropriate agent
```bash
# Solution: Check keyword matching
echo '{"message": "your request"}' | python .claude/hooks/agent-router.py
# Review output and adjust keywords in agent-router.py
```

#### Context Injection Failures

**Issue**: Context not being injected properly
```bash
# Solution: Verify agent type and file paths
echo '{"message": "test", "agent_type": "data-analyzer"}' | python .claude/hooks/context-injector.py
# Check if .claude directory structure exists
```

#### Validation Errors

**Issue**: Security validation failing
```bash
# Solution: Review validation rules
echo '{"message": "your code", "type": "request"}' | python .claude/hooks/validation-guard.py
# Adjust security patterns in validation-guard.py
```

### Performance Optimization

**Large File Processing**:
- Use data streaming for files >50MB
- Implement chunked processing
- Enable caching for repeated operations

**Dashboard Performance**:
- Use st.cache_data for expensive operations
- Implement lazy loading for large datasets
- Optimize chart rendering with sampling

**Hook Execution**:
- Profile hook execution time
- Optimize pattern matching algorithms
- Use parallel processing for independent validations

### Error Recovery

**Agent Failure Handling**:
```python
# Implement fallback routing
if primary_agent_fails:
    route_to_meta_orchestrator()
    decompose_task_differently()
```

**Hook Chain Failures**:
```python
# Graceful degradation
try:
    run_all_hooks()
except HookFailure:
    run_essential_hooks_only()
    log_failure_for_analysis()
```

### Configuration Updates

**Adding New Keywords**:
1. Edit `.claude/hooks/agent-router.py`
2. Update keyword lists for each agent
3. Test routing with new keywords
4. Update documentation

**Modifying Quality Standards**:
1. Edit `.claude/hooks/validation-guard.py`
2. Adjust quality scoring parameters
3. Test with sample requests
4. Document changes

This comprehensive guide provides everything needed to effectively use and maintain the multi-agent system for your optimizer insight project.