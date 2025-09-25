# Strategic Planning and Memory System Guide

## 🧠 Overview

This guide documents the strategic planning and memory management system that enables systematic, sequential development while maintaining a comprehensive memory of project plans, decisions, and learnings.

## 🎯 Core Concept

The system provides:
- **High-Level Planning**: Strategic decomposition of complex problems
- **Memory Management**: Persistent storage of plans, decisions, and reflections
- **Sequential Development**: Enforced logical progression through project phases
- **Iterative Reflection**: Regular assessment and plan refinement
- **Constraint Enforcement**: User-defined rules and preferences

## 🏗️ System Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│              Strategic Planner Agent                │
│         (Planning & Reflection Coordination)        │
└─────────────────────────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼────────────┐ ┌─────▼────────┐ ┌─────────▼────────┐
│ Memory Manager │ │ Plan Tracker │ │Template System   │
│    Hook        │ │    Hook      │ │   (.md files)    │
└────────────────┘ └──────────────┘ └──────────────────┘
```

### File Structure

```
.claude/
├── agents/
│   └── strategic-planner-agent.md      # Strategic planning specialist
├── hooks/
│   ├── memory-manager.py               # Memory operations
│   └── plan-tracker.py                 # Plan adherence tracking
├── templates/
│   ├── data-science-project-plan.md    # DS project template
│   ├── software-development-plan.md    # Software dev template
│   └── iteration-reflection.md         # Reflection template
└── memory/                             # Project memory storage
    ├── plans/                          # Project plans
    ├── iterations/                     # Iteration reflections
    ├── decisions/                      # Decision records
    └── constraints/                    # User constraints
```

## 🚀 Getting Started

### 1. Create Your First Project Plan

**Trigger the Strategic Planner**:
```bash
# Example request that routes to strategic-planner
echo '{"message": "create a strategic plan for customer segmentation analysis"}' | python .claude/hooks/agent-router.py
```

**Use the Memory Manager to Create Plan**:
```bash
echo '{
  "operation": "create_plan",
  "plan_data": {
    "title": "Customer Segmentation Analysis",
    "description": "Advanced ML-based customer segmentation",
    "project_type": "data_science",
    "business_problem": "Need to better understand customer groups",
    "technical_challenge": "Develop clustering algorithms for customer data",
    "success_criteria": ["Identify 5-7 distinct customer segments", "Achieve >85% segment assignment confidence"],
    "phases": [
      {"name": "Data Collection & EDA", "tasks": ["Load customer data", "Perform EDA"]},
      {"name": "Feature Engineering", "tasks": ["Create customer features", "Feature selection"]},
      {"name": "Model Development", "tasks": ["Test clustering algorithms", "Optimize parameters"]},
      {"name": "Validation & Deployment", "tasks": ["Validate segments", "Deploy model"]}
    ]
  }
}' | python .claude/hooks/memory-manager.py
```

### 2. Start Working with Plan Guidance

**Check Plan Adherence**:
```bash
echo '{
  "operation": "validate",
  "request_data": {
    "message": "analyze customer purchase history data",
    "agent": "data-analyzer"
  }
}' | python .claude/hooks/plan-tracker.py
```

**Get Next Action Suggestions**:
```bash
echo '{
  "operation": "suggest_actions",
  "context": {"current_work": "starting data analysis"}
}' | python .claude/hooks/plan-tracker.py
```

### 3. Track Progress and Reflect

**Update Progress After Completing Work**:
```bash
echo '{
  "operation": "update_progress",
  "plan_id": "plan_20250925_1200_abc123",
  "updates": {
    "completed_tasks": ["Load customer data", "Initial data quality assessment"]
  }
}' | python .claude/hooks/memory-manager.py
```

**Create Iteration Reflection**:
```bash
echo '{
  "operation": "create_reflection",
  "plan_id": "plan_20250925_1200_abc123",
  "iteration_data": {
    "iteration_number": 1,
    "planned_objectives": ["Complete data loading and basic EDA"],
    "achieved_objectives": ["Data loaded successfully", "Found data quality issues"],
    "what_worked": ["Automated data loading pipeline worked well"],
    "what_failed": ["Manual data cleaning was time-consuming"],
    "insights": ["Need better automated data cleaning tools"],
    "next_focus": "Implement automated data cleaning pipeline"
  }
}' | python .claude/hooks/memory-manager.py
```

## 📋 Project Planning Templates

### Data Science Project Template

The system provides a comprehensive template for data science projects:

**Key Sections**:
- **Project Overview**: Problem statement, success criteria
- **Approach & Strategy**: Methodology, data strategy, validation approach
- **Implementation Phases**: 5 standard phases with clear objectives
- **Technical Requirements**: Technology stack, quality standards
- **Risk Management**: Technical and business risks with mitigation
- **User-Defined Constraints**: Hard constraints and preferences

**Usage**:
```bash
# Copy template to start new project
cp .claude/templates/data-science-project-plan.md my-project-plan.md

# Edit the template with your specific requirements
# The strategic planner will reference this plan during development
```

### Software Development Template

Similar comprehensive template for software projects:

**Key Sections**:
- **Requirements Analysis**: Functional and non-functional requirements
- **Technical Architecture**: System design, technology stack
- **Development Phases**: Setup, backend, frontend, testing, deployment
- **Quality Standards**: Code quality, testing strategy, definition of done

### Iteration Reflection Template

Structured template for iteration reflections:

**Key Sections**:
- **Iteration Objectives**: Planned vs actual work
- **Work Completed**: Detailed task completion with quality assessment
- **Challenges & Blockers**: Issues encountered and resolutions
- **Learnings & Insights**: What worked, what didn't, key discoveries
- **Future Planning**: Next steps and plan adjustments

## 🎯 Strategic Planner Agent Capabilities

### Core Functions

#### 1. High-Level Planning
- **Problem Decomposition**: Break complex problems into manageable phases
- **Strategic Sequencing**: Define logical order and dependencies
- **Resource Planning**: Identify required skills and agent coordination
- **Risk Assessment**: Anticipate challenges and mitigation strategies

#### 2. Memory Management
- **Plan Persistence**: Maintain comprehensive project memory
- **Progress Tracking**: Monitor completion across iterations
- **Decision History**: Record rationale for key choices
- **Constraint Management**: Track and enforce user rules

#### 3. Reflection and Iteration
- **Post-Iteration Analysis**: Evaluate effectiveness and outcomes
- **Plan Refinement**: Adapt strategies based on results
- **Learning Capture**: Document insights for future projects
- **Quality Assessment**: Ensure deliverables meet standards

### Usage Patterns

**For Data Science Projects**:
```bash
"Create a data science plan for predicting customer churn"
"Plan a machine learning pipeline for demand forecasting"
"Develop a strategy for A/B testing framework"
```

**For Software Development**:
```bash
"Create a development plan for dashboard application"
"Plan the architecture for real-time analytics system"
"Develop a deployment strategy for ML model serving"
```

**For Reflection and Memory**:
```bash
"Reflect on the last iteration and update the plan"
"Review project memory and suggest next actions"
"Track progress against the strategic plan"
```

## 💾 Memory Management System

### Memory Components

#### Project Plans
- **Master Plan**: Complete project roadmap with phases
- **Progress Tracking**: Current status, completed/active/pending tasks
- **Quality Gates**: Checkpoints and validation criteria

#### Iteration Reflections
- **Objectives Assessment**: Planned vs actual work
- **Quality Evaluation**: Deliverable assessment
- **Learning Capture**: Insights and improvements

#### Decision Records
- **Context**: Why decision was needed
- **Options**: Alternatives considered
- **Rationale**: Why specific choice was made
- **Impact**: Consequences and follow-up

#### User Constraints
- **Hard Constraints**: Must follow rules
- **Preferences**: Should consider guidelines
- **Scope**: Global, phase-specific, or agent-specific

### Memory Operations

#### Create Operations
```bash
# Create project plan
echo '{"operation": "create_plan", "plan_data": {...}}' | python .claude/hooks/memory-manager.py

# Record decision
echo '{"operation": "record_decision", "plan_id": "...", "decision_data": {...}}' | python .claude/hooks/memory-manager.py

# Create reflection
echo '{"operation": "create_reflection", "plan_id": "...", "iteration_data": {...}}' | python .claude/hooks/memory-manager.py
```

#### Update Operations
```bash
# Update progress
echo '{"operation": "update_progress", "plan_id": "...", "updates": {...}}' | python .claude/hooks/memory-manager.py

# Manage constraints
echo '{"operation": "manage_constraints", "plan_id": "...", "constraint_data": {...}}' | python .claude/hooks/memory-manager.py
```

#### Query Operations
```bash
# Get complete memory
echo '{"operation": "get_memory", "plan_id": "..."}' | python .claude/hooks/memory-manager.py

# Query with criteria
echo '{"operation": "query", "query": {"text": "clustering", "date_from": "2025-01-01"}}' | python .claude/hooks/memory-manager.py
```

## 🛡️ Plan Tracking and Enforcement

### Constraint Enforcement

The plan tracker ensures development follows the planned approach:

#### Constraint Types
- **Hard Constraints**: Must be followed (e.g., data security requirements)
- **Preferences**: Should be considered (e.g., prefer simpler models)
- **Guidelines**: Development best practices

#### Validation Process
```bash
# Validate request against plan
echo '{
  "operation": "validate",
  "request_data": {
    "message": "implement neural network for classification",
    "agent": "ml-concept-tester"
  }
}' | python .claude/hooks/plan-tracker.py
```

### Sequential Development

The system enforces logical progression:

#### Phase Gates
- **Prerequisites**: Must be met before proceeding
- **Dependencies**: Required prior work
- **Quality Standards**: Minimum acceptance criteria

#### Development Sequence
```bash
# Check if action fits current phase
echo '{
  "operation": "enforce_sequence",
  "request_data": {
    "action": "deploy model to production",
    "phase": "development"
  }
}' | python .claude/hooks/plan-tracker.py
```

## 📊 Usage Examples

### Example 1: Complete Data Science Workflow

```bash
# 1. Create strategic plan
echo '{
  "operation": "create_plan",
  "plan_data": {
    "title": "Demand Forecasting System",
    "project_type": "data_science",
    "business_problem": "Improve inventory planning accuracy",
    "phases": [
      {"name": "Data Analysis", "tasks": ["Load data", "EDA", "Quality assessment"]},
      {"name": "Model Development", "tasks": ["Feature engineering", "Model testing"]},
      {"name": "Validation", "tasks": ["Cross-validation", "Business validation"]},
      {"name": "Deployment", "tasks": ["Model serving", "Monitoring"]}
    ]
  }
}' | python .claude/hooks/memory-manager.py

# 2. Add user constraints
echo '{
  "operation": "manage_constraints",
  "plan_id": "plan_20250925_1200_forecast",
  "constraint_data": {
    "title": "Model Interpretability Required",
    "description": "All models must be explainable for business users",
    "type": "requirement",
    "enforcement": "strict"
  }
}' | python .claude/hooks/memory-manager.py

# 3. Work on first phase
echo '{"message": "analyze historical sales data for patterns"}' | python .claude/hooks/agent-router.py

# 4. Update progress
echo '{
  "operation": "update_progress",
  "plan_id": "plan_20250925_1200_forecast",
  "updates": {"completed_tasks": ["Load data", "Initial EDA"]}
}' | python .claude/hooks/memory-manager.py

# 5. Create reflection
echo '{
  "operation": "create_reflection",
  "plan_id": "plan_20250925_1200_forecast",
  "iteration_data": {
    "iteration_number": 1,
    "what_worked": ["Data loading pipeline efficient"],
    "what_failed": ["Missing seasonal adjustment in EDA"],
    "insights": ["Strong seasonal patterns in sales data"],
    "next_focus": "Implement seasonal decomposition analysis"
  }
}' | python .claude/hooks/memory-manager.py
```

### Example 2: Adding User Constraints During Development

```bash
# Add new constraint based on business feedback
echo '{
  "operation": "manage_constraints",
  "plan_id": "current_plan_id",
  "constraint_data": {
    "title": "Real-time Performance Requirement",
    "description": "Model predictions must be available within 100ms",
    "type": "requirement",
    "priority": "high",
    "scope": "deployment_phase"
  }
}' | python .claude/hooks/memory-manager.py

# System will now validate future requests against this constraint
echo '{
  "operation": "validate",
  "request_data": {
    "message": "implement complex ensemble model with 10 algorithms"
  }
}' | python .claude/hooks/plan-tracker.py
# Would warn about potential performance impact
```

## 🔧 Advanced Features

### Custom Plan Templates

You can create custom templates for specific domains:

```markdown
# Custom Template: Retail Optimization Plan

## Business Context
- Store layout optimization
- Product placement strategies
- Customer flow analysis

## Specialized Phases
1. **Store Analysis**: Layout assessment, customer journey mapping
2. **Data Collection**: Transaction data, customer behavior, space utilization
3. **Optimization Modeling**: Constraint programming, space allocation
4. **Testing & Validation**: A/B testing, ROI analysis

## Domain Constraints
- Must comply with accessibility regulations
- Cannot exceed budget of $X for changes
- Implementation must be completed during off-peak hours
```

### Memory Querying

Advanced queries for project insights:

```bash
# Find all decisions related to model selection
echo '{
  "operation": "query",
  "query": {
    "text": "model selection",
    "type": "decision",
    "date_from": "2025-01-01"
  }
}' | python .claude/hooks/memory-manager.py

# Find patterns in what worked across iterations
echo '{
  "operation": "query",
  "query": {
    "text": "what worked",
    "type": "iteration"
  }
}' | python .claude/hooks/memory-manager.py
```

### Integration with Other Agents

The strategic planner coordinates with other agents:

**With Data Science Researcher**:
- Validates research methodologies against plan requirements
- Ensures academic rigor meets project standards

**With ML Concept Tester**:
- Guides experiment prioritization based on plan objectives
- Ensures testing aligns with validation strategy

**With Dashboard Developer**:
- Coordinates UI development with user requirements
- Ensures deliverables meet acceptance criteria

## 📈 Benefits

### For Development Teams
- **Systematic Approach**: No missed steps or random development
- **Clear Progress Tracking**: Always know where you are in the project
- **Learning Preservation**: Insights preserved for future projects
- **Quality Assurance**: Built-in checkpoints and validation

### For Project Management
- **Visibility**: Clear view of project status and progress
- **Risk Management**: Early identification of issues and blockers
- **Resource Planning**: Better allocation of specialized agents
- **Stakeholder Communication**: Regular updates based on actual progress

### For Long-term Success
- **Organizational Learning**: Best practices captured and reused
- **Process Improvement**: Continuous refinement based on reflections
- **Knowledge Management**: Centralized project memory
- **Consistency**: Standardized approaches across projects

## 🚀 Best Practices

### Planning
1. **Start with Clear Objectives**: Define success criteria upfront
2. **Break Down Complex Problems**: Use manageable phases and milestones
3. **Consider Dependencies**: Plan logical sequence of work
4. **Plan for Iteration**: Build in reflection and adjustment points

### Execution
1. **Follow the Plan**: Use plan tracker validation before major decisions
2. **Update Progress Regularly**: Keep memory current with actual work
3. **Respect Constraints**: Honor user-defined rules and preferences
4. **Collaborate Effectively**: Use agent coordination for complex tasks

### Reflection
1. **Regular Reflection**: Conduct iteration reviews frequently
2. **Honest Assessment**: Acknowledge both successes and failures
3. **Capture Insights**: Document learnings for future benefit
4. **Adapt Plans**: Modify approach based on new information

This strategic planning and memory system transforms ad-hoc development into systematic, learning-oriented project execution that builds organizational capability over time.

**Ready to plan your next project systematically! 🎯**