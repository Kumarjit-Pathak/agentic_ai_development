# Optimizer Insight - Multi-Agent System

A specialized Claude Code sub-agent system for retail optimization and constraint analysis, built using the Claude Code SDK.

## Architecture Overview

This project implements a multi-agent system with specialized sub-agents for different aspects of the optimization workflow:

### 🤖 Specialized Agents

#### 1. **Data Analyzer Agent** (`data-analyzer-agent.md`)
- **Expertise**: Excel/CSV processing, constraint analysis, data validation
- **Capabilities**: Data quality assessment, constraint mapping analysis, statistical insights
- **Use Cases**: Processing constraint files, validating data integrity, generating data reports

#### 2. **Dashboard Developer Agent** (`dashboard-developer-agent.md`)
- **Expertise**: Streamlit development, UI/UX design, data visualization
- **Capabilities**: Interactive dashboard creation, responsive design, performance optimization
- **Use Cases**: Building business intelligence interfaces, creating data visualizations

#### 3. **Optimization Expert Agent** (`optimization-expert-agent.md`)
- **Expertise**: Mathematical modeling, constraint satisfaction, algorithm design
- **Capabilities**: Optimization problem formulation, algorithm implementation, solution validation
- **Use Cases**: Retail space optimization, constraint problem solving, mathematical modeling

#### 4. **Data Science Researcher Agent** (`data-science-researcher-agent.md`)
- **Expertise**: Advanced research, mathematical modeling, statistical analysis
- **Capabilities**: Research methodology, hypothesis testing, Bayesian inference, experimental design
- **Use Cases**: Academic-level research, advanced statistical modeling, literature reviews

#### 5. **ML/DL/GenAI Concept Tester Agent** (`ml-concept-tester-agent.md`)
- **Expertise**: Machine learning experimentation, deep learning, generative AI testing
- **Capabilities**: Algorithm testing, model validation, AI concept evaluation, MLOps
- **Use Cases**: ML model development, AI research validation, performance benchmarking

#### 6. **Meta Orchestrator Agent** (`meta-orchestrator-agent.md`)
- **Expertise**: Agent coordination, workflow management, task decomposition
- **Capabilities**: Multi-agent coordination, complex task breakdown, quality assurance
- **Use Cases**: Managing complex workflows, coordinating agent interactions

### 🔧 Hook System

#### Agent Router (`agent-router.py`)
- Analyzes incoming requests using keyword and pattern matching
- Routes tasks to appropriate specialized agents
- Provides intelligent agent selection based on content analysis

#### Context Injector (`context-injector.py`)
- Injects relevant project context for each agent type
- Provides domain-specific information and file references
- Enhances agent specialization with contextual awareness

#### Validation Guard (`validation-guard.py`)
- Validates security and quality of inputs/outputs
- Enforces coding standards and best practices
- Prevents dangerous operations and ensures code quality

## 🚀 Usage

### Basic Agent Invocation
```bash
# Route a data analysis request
echo '{"message": "Analyze constraint mapping Excel files"}' | python .claude/hooks/agent-router.py

# Inject context for dashboard development
echo '{"message": "Build visualization dashboard", "agent_type": "dashboard-developer"}' | python .claude/hooks/context-injector.py

# Validate request security
echo '{"message": "Process optimization data", "agent_type": "optimization-expert"}' | python .claude/hooks/validation-guard.py
```

### Agent Selection Logic

The system automatically routes requests based on:
- **Data keywords**: `data`, `excel`, `csv`, `constraint`, `analysis` → Data Analyzer
- **UI keywords**: `streamlit`, `dashboard`, `visualization`, `interface` → Dashboard Developer
- **Optimization keywords**: `optimization`, `algorithm`, `mathematical`, `model` → Optimization Expert
- **Research keywords**: `research`, `statistical`, `modeling`, `hypothesis`, `bayesian` → Data Science Researcher
- **ML keywords**: `machine learning`, `deep learning`, `neural network`, `ml`, `ai`, `genai` → ML Concept Tester
- **Complex tasks**: Multiple expertise areas → Meta Orchestrator

### Project Files

```
.claude/
├── agents/
│   ├── data-analyzer-agent.md
│   ├── dashboard-developer-agent.md
│   ├── optimization-expert-agent.md
│   ├── data-science-researcher-agent.md
│   ├── ml-concept-tester-agent.md
│   └── meta-orchestrator-agent.md
├── hooks/
│   ├── agent-router.py
│   ├── context-injector.py
│   └── validation-guard.py
└── config.json
```

## 🛠️ Configuration

The system is configured via `.claude/config.json` with:
- Agent capabilities and priorities
- Hook trigger conditions
- Security and quality standards
- Routing rules and thresholds
- Project context and domain information

## 🔒 Security Features

- Input validation and sanitization
- Dangerous pattern detection
- Secret detection and prevention
- Code quality enforcement
- Safe operation validation

## 📊 Quality Standards

- Minimum quality score requirements
- Error handling enforcement
- Documentation requirements
- PEP 8 compliance checking
- Type safety validation

## 🎯 Use Cases

1. **Data Analysis**: Process constraint mapping files, validate data quality, generate insights
2. **Dashboard Development**: Create interactive Streamlit applications with business intelligence features
3. **Optimization Modeling**: Formulate and solve constraint satisfaction problems
4. **Workflow Coordination**: Manage complex multi-step optimization workflows

## 🔗 Reference

Based on the approach demonstrated in [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) by disler.

## 🏃‍♂️ Getting Started

1. Ensure your project has the `.claude/` directory structure
2. Configure agent specializations in the markdown files
3. Use the hook system for intelligent request routing
4. Leverage specialized agents for domain-specific tasks

The system provides clean, effective sub-agent coordination for complex optimization and analysis workflows.