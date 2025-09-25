Let me share context for you to understand the background of space planogram optimization work we have done. 


# Beer Space Planogram Optimizer

---

## 1. Purpose

The Beer Space Planogram Optimizer is a **custom-built, constraint-aware allocation engine** for designing beer shelf and VR planograms.  
It helps category/space planners allocate limited shelf space across SKUs while meeting:

- **Business objectives** – revenue maximization, brand share targets, or a balanced approach  
- **Brand/ownership constraints** – e.g., ABI ≥ 80%, Heineken ≤ 20%  
- **Merchandising rules** – mandatory SKUs, singles-on-top-shelf, style adjacency  
- **Style interaction effects** – using a style interaction matrix

The optimizer generates **three optimized planograms**:

1. **Revenue-focused**  
2. **Brand share adherence**  
3. **Balanced (revenue + share)**

---

## 2. Inputs Overview

The optimizer reads several structured files:

| File Name                              | Description                                                                 |
|----------------------------------------|-----------------------------------------------------------------------------|
| **Sales Data File**                    | Historical sales & pricing per SKU                                          |
| **`constraint_type_mapping.xlsx`**     | Master list of all constraints (type, description, % share if any)          |
| **Shelf Constraint Mapping File**      | Shelf/bin geometry and constraints per bin                                  |
| **SKU Constraint Mapping File**        | SKU metadata and flags showing which constraints apply to which SKUs        |

---

### 2.1 Sales Data File

Contains basic SKU performance metrics.

| Column | Description |
|--------|-------------|
| **SKU_ID** | Unique identifier for each SKU |
| **Brand_Family** | Brand grouping (e.g., ABI, Heineken) |
| **Manufacturer** | Manufacturer name |
| **Segment / Style** | Beer style or segment (e.g., Lager, IPA) |
| **Volume** | Historical sales volume |
| **Price** | Average selling price |
| **Other Metrics** | Optional: margin, velocity, etc. |

> Used to rank SKUs for revenue potential and decide placement priority.

---

### 2.2 `constraint_type_mapping.xlsx`

Defines all available constraints.

| Column | Description |
|--------|-------------|
| **constraint_id** | Unique ID (e.g., `constraint_1`, `constraint_2`) |
| **space_percentage** | Required shelf share % (if blank → not a share constraint) |
| **constraint_type** | `SQ_TO_BIN`, `BIN_TO_SQ`, or `OVERALL` |
| **constraint_description** | Business-friendly description |

- **If `space_percentage` has a number** → this is a **space/share constraint**.  
- **`SQ_TO_BIN`** → SKUs can only go to bins with this constraint.  
- **`BIN_TO_SQ`** → Bins can only accept SKUs with this constraint.  
- **`OVERALL`** → A brand/category group must achieve the stated % share.

---

### 2.3 Shelf Constraint Mapping File

Captures **shelf/bin geometry** and their constraints.

| Column | Description |
|--------|-------------|
| **bin_id** | Unique ID for each bin |
| **shelf** | Shelf number |
| **door** | Door or section |
| **height** | Bin height |
| **width** | Bin width |
| **depth** | Bin depth |
| **constraint_x** | Columns for each constraint ID (value `1` = applied) |

Example:

| bin_id | shelf | door | height | width | depth | constraint_2 | constraint_3 |
|--------|-------|------|--------|-------|-------|--------------|--------------|
| BIN_01 | Top   | 1    | 30     | 20    | 18    | 1            | 1            |
| BIN_02 | Mid   | 1    | 30     | 20    | 18    | 0            | 0            |

---

### 2.4 SKU Constraint Mapping File

Maps SKUs to their constraints and metadata.

| Column | Description |
|--------|-------------|
| **sku_id** | SKU identifier |
| **sku_detail** | Description (name, pack, size) |
| **brand_family** | Brand group |
| **segment / style** | Beer style or segment |
| **manufacturer** | Manufacturer name |
| **constraint_x** | Columns for each constraint ID (value `1` = SKU is flagged) |

Example:

| sku_id | brand_family | manufacturer | segment | constraint_1 | constraint_2 |
|--------|--------------|-------------|---------|--------------|--------------|
| ABI_001| ABI          | AB InBev    | Lager   | 1            | 0            |
| ABI_002| ABI          | AB InBev    | Lager   | 1            | 0            |
| HEIN_01| Heineken     | Heineken    | Lager   | 0            | 1            |

---

### 2.5 Constraint Logic Summary

| Type | Meaning | Effect |
|------|---------|--------|
| **SQ_TO_BIN** | SKU → Bin restriction | SKU can only be placed in bins flagged with same constraint |
| **BIN_TO_SQ** | Bin → SKU restriction | Bin can only hold SKUs flagged with same constraint |
| **OVERALL** | Share target | SKUs flagged must collectively meet the % space target |

**Special Case – Singles on Top Shelf:**  
- Top shelf bins flagged with “singles-only” constraint.  
- Single-pack SKUs flagged with the same constraint.  
- Result → only singles go on top shelf.

---

## 3. Algorithm Overview

### Step 1 – Mandatory SKU Placement
- **Priority queue** of mandatory SKUs (ranked by sales/importance).  
- Place one-by-one into compatible bins, preferring least used bins.  
- Guarantees **≥1 facing** per mandatory SKU.

### Step 2 – Dynamic Allocation
- Build **brand/category queues** (e.g., ABI, Heineken, Singles).  
- **Queue Ranking** based on revenue, style adjacency, or blended metrics.  
- At each step: pick the **best queue head** depending on user strategy:  
  - **Revenue:** highest revenue SKU  
  - **Share:** SKU from brand furthest from target %  
  - **Balanced:** hybrid score (revenue + share gap)  
- Place SKU into existing block if possible, otherwise into least-used compatible bin.  
- Update brand shares, space used, and adjacency scores.

### Step 3 – Outputs
Generates three planograms:
1. **Revenue-focused**
2. **Brand-share adherence**
3. **Balanced**

Each output includes:
- Shelf layout (bin → SKU facings)
- Brand share achieved vs. target
- Revenue estimate
- Constraint compliance status

---

## 4. Output Structure

| Shelf Row | Bin | SKU ID | Brand | Facings | Projected Revenue |
|-----------|-----|--------|-------|---------|-------------------|
| Top       | B1  | ABI_001 | ABI | 3 | $1,200 |
| Top       | B2  | HEIN_01 | Heineken | 2 | $800 |
| Mid       | B3  | ABI_002 | ABI | 4 | $1,600 |

---

## 5. Workflow

1. Prepare input files (`sales`, `constraint_type_mapping.xlsx`, shelf mapping, SKU mapping).  
2. Run optimizer with chosen strategy: **Revenue / Share / Balanced**.  
3. Review and compare generated planograms.  
4. Export to visualization or VR tools.

---

## 6. Data Validation Rules

- **ID Consistency**: SKUs and constraints must match across files.  
- **Space %**: Overall share targets must sum ≤100%.  
- **Flags**: Constraint flags should be `0`/`1`.  
- **Geometry**: Bin dimensions must be valid and consistent.  



# Instructions for claude code 

I have 2 outputs from my optimizer . one without taking any constraint into account (file name : unconstrained.xlsx)
another with taking into consideration for all the constraint (file name : output_code_2.xlsx)

I have developped an app  on path: C:\Users\40103061\Anheuser-Busch InBev\Kumarjit Backup - General\codepython\catexpert science\optimizerinsight\constraint_analysis_dashboard - genai -version 2.py

This is just an MVP to analyze all the outputs and constraints and then provide prescriptive suggestions for the planogramer on what are the constraints not working well etc. 

## Sample finding are below based on the output: 

Findings:
Most Damaging Constraints:

Units Lost:
Constraint_1 and Constraint_4 (Pack Qty = 1) have the largest units lost at 2685.11 each.
Revenue Lost:
Constraint_3 (Manufacturer = Heineken) shows significant revenue loss at 1662.45.
Volume Lost:
Constraint_3 (Manufacturer = Heineken) also has the highest volume lost at 554.17 liters.
Patterns Across Manufacturers and Brand Families:

Heineken has the highest revenue loss (424.35 from SKU 6001760003625) and significant volume loss (178.20 liters).
ABI shows a negative unit loss (-178), indicating a gain, which is unusual compared to other manufacturers.
Savanna and Hunters have multiple SKUs with losses, indicating potential issues in their constraints.
Recommendations for Optimization:

Focus on Constraint_3 (Heineken) to address the significant revenue and volume losses. Strategies could include revising pricing or promotional strategies to mitigate losses.
Investigate Pack Qty Constraints (Constraint_1 and Constraint_4) as they are causing substantial unit losses. Consider adjusting pack sizes or configurations to improve sales.
Monitor ABI's performance closely, as the negative unit loss suggests potential opportunities that could be leveraged further.
Anomalies Worth Flagging:

ABI's Constraint_2 shows a negative unit loss (-178), which is atypical and may indicate an area of opportunity rather than a constraint issue.
The high losses in Heineken's constraints (both in revenue and volume) suggest a critical area that requires immediate attention to prevent further losses.
Summary:
The analysis indicates that constraints related to Heineken are the most damaging in terms of revenue and volume loss. There are significant opportunities to optimize pack sizes and monitor ABI's performance closely due to its unusual negative unit loss. Addressing these areas could lead to improved overall performance.

