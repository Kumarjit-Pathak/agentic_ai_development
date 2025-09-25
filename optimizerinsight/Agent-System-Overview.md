# Claude Code Sub-Agent System Overview

## 📋 Table of Contents
- [Introduction](#introduction)
- [Architecture](#architecture)
- [Agent Ecosystem](#agent-ecosystem)
- [Hook System](#hook-system)
- [Configuration](#configuration)
- [Implementation Philosophy](#implementation-philosophy)
- [Reference Framework](#reference-framework)

## Introduction

This document provides a comprehensive overview of the multi-agent system created for the Optimizer Insight project using the Claude Code SDK. The system is based on the architectural patterns demonstrated in the [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) repository, implementing specialized sub-agents for retail optimization and constraint analysis tasks.

## Architecture

### System Design Principles

The multi-agent system follows these core principles derived from the reference implementation:

1. **Specialization**: Each agent has a focused domain of expertise
2. **Coordination**: A meta-agent orchestrates complex workflows
3. **Modularity**: Agents can work independently or collaboratively
4. **Extensibility**: New agents can be added without system restructure
5. **Quality Assurance**: Built-in validation and quality control

### Directory Structure

```
.claude/
├── agents/                          # Agent definition files
│   ├── data-analyzer-agent.md       # Data processing specialist
│   ├── dashboard-developer-agent.md # UI/UX development expert
│   ├── optimization-expert-agent.md # Mathematical modeling specialist
│   ├── data-science-researcher-agent.md # Research and advanced modeling specialist
│   ├── ml-concept-tester-agent.md   # ML/DL/GenAI experimentation expert
│   └── meta-orchestrator-agent.md   # Agent coordination manager
├── hooks/                           # Lifecycle management scripts
│   ├── agent-router.py             # Intelligent request routing
│   ├── context-injector.py         # Domain context injection
│   └── validation-guard.py         # Security & quality validation
└── config.json                     # System configuration
```

## Agent Ecosystem

### 🔍 Data Analyzer Agent
**Primary Focus**: Data processing, validation, and constraint analysis

**Domain Expertise**:
- Excel/CSV file processing and manipulation
- Constraint mapping analysis and validation
- Data quality assessment and cleansing
- Statistical analysis of optimization datasets
- Business intelligence data preparation

**Key Technologies**:
- Pandas for data manipulation
- NumPy for numerical computations
- Excel processing libraries
- Data validation frameworks

### 🎨 Dashboard Developer Agent
**Primary Focus**: User interface development and data visualization

**Domain Expertise**:
- Streamlit application development
- Interactive dashboard creation
- Data visualization and charting
- User experience optimization
- Performance optimization for large datasets

**Key Technologies**:
- Streamlit framework
- Plotly/Matplotlib for visualizations
- CSS styling and theming
- Session state management
- Component architecture

### 🔬 Optimization Expert Agent
**Primary Focus**: Mathematical modeling and algorithm development

**Domain Expertise**:
- Constraint satisfaction problems (CSP)
- Linear and integer programming
- Retail space optimization algorithms
- Mathematical model formulation
- Solution validation and analysis

**Key Technologies**:
- Optimization libraries (PuLP, OR-Tools, CVXPY)
- Mathematical modeling frameworks
- Algorithm implementation
- Performance analysis tools

### 🔬 Data Science Researcher Agent
**Primary Focus**: Advanced research and mathematical modeling for data science problems

**Domain Expertise**:
- Advanced statistical modeling and analysis
- Research methodology and experimental design
- Bayesian inference and probabilistic modeling
- Time series analysis and forecasting
- Operations research and decision theory
- Academic-level research and literature review

**Key Technologies**:
- SciPy ecosystem for scientific computing
- Statsmodels for statistical modeling
- PyMC for Bayesian analysis
- Research platforms and academic databases

### 🤖 ML/DL/GenAI Concept Tester Agent
**Primary Focus**: Experimental testing of machine learning, deep learning, and generative AI concepts

**Domain Expertise**:
- Machine learning algorithm experimentation
- Deep learning architecture testing
- Generative AI model evaluation
- AI concept validation and benchmarking
- MLOps and model deployment testing
- Cutting-edge AI research implementation

**Key Technologies**:
- PyTorch/TensorFlow for deep learning
- Scikit-learn for classical ML
- Transformers (Hugging Face) for LLMs
- MLflow for experiment tracking
- Ray for distributed computing

### 🎭 Meta Orchestrator Agent
**Primary Focus**: Agent coordination and workflow management

**Domain Expertise**:
- Multi-agent task coordination
- Complex workflow decomposition
- Agent communication and handoffs
- Quality assurance across agents
- Strategic system guidance

**Key Capabilities**:
- Dynamic agent selection
- Task complexity assessment
- Inter-agent communication
- Result synthesis and integration

## Hook System

### Agent Router Hook (`agent-router.py`)

**Purpose**: Intelligent request routing based on content analysis

**Functionality**:
- Keyword-based agent selection
- Pattern matching for request classification
- Multi-agent recommendation for complex tasks
- Confidence scoring for routing decisions

**Routing Logic**:
```python
# Example routing patterns
data_keywords = ["data", "excel", "csv", "constraint", "analysis"]
dashboard_keywords = ["streamlit", "dashboard", "ui", "visualization"]
optimization_keywords = ["optimization", "algorithm", "mathematical", "model"]
research_keywords = ["research", "statistical", "modeling", "hypothesis", "bayesian"]
ml_keywords = ["machine learning", "deep learning", "neural network", "ml", "dl", "ai", "genai"]
```

### Context Injector Hook (`context-injector.py`)

**Purpose**: Domain-specific context enhancement for agent specialization

**Functionality**:
- Project structure analysis
- Relevant file identification
- Technology stack context
- Domain-specific information injection

**Context Categories**:
- File system context (relevant files, directory structure)
- Technology context (frameworks, libraries, tools)
- Domain context (business rules, constraints, objectives)
- Historical context (previous interactions, decisions)

### Validation Guard Hook (`validation-guard.py`)

**Purpose**: Security validation and quality enforcement

**Security Features**:
- Dangerous pattern detection
- Hardcoded secret identification
- Safe operation validation
- Input sanitization

**Quality Standards**:
- Code quality scoring
- Error handling requirements
- Documentation standards
- Style guide compliance

## Configuration

### System Configuration (`config.json`)

The configuration file defines:

```json
{
  "agents": {
    "data-analyzer": {
      "capabilities": ["excel_processing", "data_validation", "constraint_analysis"],
      "priority": 1
    }
    // ... other agents
  },
  "hooks": {
    "agent-router": {
      "trigger": "pre_request",
      "priority": 1
    }
    // ... other hooks
  },
  "routing_rules": {
    "data_keywords": ["data", "excel", "csv"],
    "complex_task_threshold": 3
  },
  "security": {
    "enable_validation": true,
    "block_dangerous_patterns": true
  }
}
```

## Implementation Philosophy

### Based on claude-code-hooks-mastery Patterns

The implementation follows key patterns from the reference repository:

1. **Markdown Agent Definitions**: Each agent is defined as a markdown file with clear capabilities and responsibilities
2. **Hook-Driven Lifecycle**: Hooks provide deterministic control over agent behavior and interactions
3. **Modular Architecture**: Independent components that can be composed for complex workflows
4. **Security-First Approach**: Built-in validation and security measures
5. **Quality Assurance**: Automated quality checking and enforcement

### Agent Specialization Strategy

Each agent is designed with:
- **Clear Boundaries**: Well-defined scope of responsibility
- **Domain Expertise**: Deep knowledge in specific technical areas
- **Collaborative Interfaces**: Ability to work with other agents
- **Quality Standards**: Consistent output quality and validation

### Workflow Coordination

The system supports:
- **Sequential Workflows**: Step-by-step task execution
- **Parallel Processing**: Concurrent agent execution
- **Hierarchical Coordination**: Meta-agent oversight and management
- **Error Handling**: Graceful failure recovery and reporting

## Reference Framework

This implementation is inspired by and follows patterns from:
- **Repository**: [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery)
- **Author**: disler
- **Key Concepts**: Hook lifecycle management, agent specialization, deterministic control

### Adaptations for Optimizer Insight

The system has been specifically adapted for:
- **Retail Optimization Domain**: Constraint analysis, space optimization
- **Business Intelligence**: Dashboard development, data visualization
- **Mathematical Modeling**: Optimization algorithms, constraint satisfaction
- **Data Processing**: Excel files, constraint mappings, analytics

### Extension Points

The system is designed for easy extension:
- **New Agents**: Add markdown files in `.claude/agents/`
- **New Hooks**: Add Python scripts in `.claude/hooks/`
- **Configuration**: Modify `.claude/config.json`
- **Routing Rules**: Extend keyword and pattern matching

## Next Steps

1. **Agent Testing**: Validate each agent's functionality
2. **Integration Testing**: Test multi-agent workflows
3. **Performance Optimization**: Optimize hook execution and routing
4. **Documentation**: Create detailed usage guides
5. **Extension Development**: Add domain-specific agents as needed

This multi-agent system provides a robust, extensible foundation for complex optimization and analysis workflows while maintaining clean separation of concerns and high code quality standards.