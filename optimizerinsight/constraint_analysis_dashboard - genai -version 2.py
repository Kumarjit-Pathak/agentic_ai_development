# app.py
import os
from dotenv import load_dotenv

import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI

# LangChain agent imports (experimental)
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

# ---------------------- Config ----------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.warning("OPENAI_API_KEY not found in environment. AI features will be disabled.")

# Initialize OpenAI client (used for batch insights/refinement)
openai_client = None
try:
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception:
    openai_client = None

# ---------------------- Page & Theme (small & clean) ----------------------
st.set_page_config(layout="wide", page_title="Constraint Impact Analyzer", initial_sidebar_state="collapsed")
LEMON = "#f2da08"
ACCENT = LEMON
BG = "#ffffff"
TEXT = "#111111"

st.markdown(
    f"""
    <style>
    :root {{
        --accent: {ACCENT};
    }}
    .title {{ color: var(--accent); font-weight:800; font-size:24px; }}
    .muted {{ color: #666; font-size:13px; }}
    .card {{ background: #fff; border-radius:10px; padding:10px; border:1px solid #eee; box-shadow:0 6px 18px rgba(0,0,0,0.03); }}
    .small-upload button {{ padding:6px 10px; border-radius:8px; background: linear-gradient(90deg,var(--accent), #ffd94d); border:none; font-weight:700; }}
    .small-btn {{ padding:6px 10px; border-radius:8px; border:1px solid var(--accent); color:var(--accent); background:transparent; font-weight:700; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='title'> Constraint Impact Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='muted'>Upload files, get constraint impact, and ask the agent.</div>", unsafe_allow_html=True)
st.write("")

# ---------------------- Simple simultaneous upload UI ----------------------
st.markdown("# Upload files")
upload_cols = st.columns([1,1,1])  # three per row

# Mapping of keys -> labels (kept simple)
FILES = [
    ("constrained", "Constrained Output XLSX"),
    ("unconstrained", "Unconstrained Output XLSX"),
    ("constraint_types", "Constraint Types XLSX"),
    ("shelf_constraints", "Shelf Constraint Mapping XLSX"),
    ("sku_constraints", "SKU Constraint Mapping XLSX"),
    ("sku_meta", "SKU Metadata XLSX")
]

# ensure session state for uploaded files
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {k: None for k, _ in FILES}

# render uploaders in 2 rows of 3
for i, (key, label) in enumerate(FILES):
    col = upload_cols[i % 3]
    with col:
        current = st.session_state.uploaded_files.get(key)
        if current is None:
            up = st.file_uploader(label, type=["xlsx", "xls", "csv"], key=f"uploader_{key}", label_visibility="visible")
            if up is not None:
                st.session_state.uploaded_files[key] = up
                st.success(f"{label} uploaded: {up.name}")
        else:
            st.markdown(f"**{label}**")
            st.markdown(f"<div style='background:#fffbe6;padding:6px;border-radius:8px;border:1px solid var(--accent)'><b style='color:var(--accent)'>{current.name}</b></div>", unsafe_allow_html=True)
            if st.button("Replace", key=f"replace_{key}", help="Replace this file"):
                st.session_state.uploaded_files[key] = None
                # clear widget (user will re-upload)

st.write("")  # spacing

# ---------------------- Helper read function ----------------------
def read_blob(file_like):
    try:
        if hasattr(file_like, "read"):
            return pd.read_excel(file_like)
        else:
            return pd.read_excel(file_like)
    except Exception as e:
        st.error(f"Failed to read {getattr(file_like,'name',str(file_like))}: {e}")
        return pd.DataFrame()

# ---------------------- Process when all files present ----------------------
files_ready = all(v is not None for v in st.session_state.uploaded_files.values())
if not files_ready:
    missing = [label for (k, label) in FILES if st.session_state.uploaded_files.get(k) is None]
    st.warning(f"Waiting for files: {missing}")
    st.stop()

# Read all files
constrained = read_blob(st.session_state.uploaded_files["constrained"])
unconstrained = read_blob(st.session_state.uploaded_files["unconstrained"])
constraint_types = read_blob(st.session_state.uploaded_files["constraint_types"])
# shelf_constraints read but not shown
shelf_constraints = read_blob(st.session_state.uploaded_files["shelf_constraints"])
sku_constraints = read_blob(st.session_state.uploaded_files["sku_constraints"])
sku_meta = read_blob(st.session_state.uploaded_files["sku_meta"])

# ---------------------- Validate required columns ----------------------
required_core = ["sku", "# units", "primary_price_per_ltr", "volume_per_unit"]
for name, df in [("constrained", constrained), ("unconstrained", unconstrained)]:
    missing = [c for c in required_core if c not in df.columns]
    if missing:
        st.error(f"Missing required columns in {name}: {missing}. Fix and re-upload.")
        st.stop()

# ---------------------- Numeric conversions & revenue/volume ----------------------
for df in (constrained, unconstrained):
    df["# units"] = pd.to_numeric(df["# units"], errors="coerce").fillna(0)
    df["primary_price_per_ltr"] = pd.to_numeric(df["primary_price_per_ltr"], errors="coerce").fillna(0)
    df["volume_per_unit"] = pd.to_numeric(df["volume_per_unit"], errors="coerce").fillna(0)
    # assume volume_per_unit is in liters; if ml, divide by 1000 before upload
    df["price_per_unit"] = df["primary_price_per_ltr"] * df["volume_per_unit"]
    df["revenue"] = df["price_per_unit"] * df["# units"]
    df["volume_total_ltr"] = df["volume_per_unit"] * df["# units"]

# ---------------------- Aggregate to SKU and diffs ----------------------
sku_uncon = unconstrained.groupby("sku").agg(
    units_uncon=("# units", "sum"),
    revenue_uncon=("revenue", "sum"),
    volume_uncon=("volume_total_ltr", "sum")
).reset_index()

sku_con = constrained.groupby("sku").agg(
    units_con=("# units", "sum"),
    revenue_con=("revenue", "sum"),
    volume_con=("volume_total_ltr", "sum")
).reset_index()

merged = pd.merge(sku_uncon, sku_con, on="sku", how="outer").fillna(0)
merged["unit_diff"] = merged["units_uncon"] - merged["units_con"]
merged["revenue_diff"] = merged["revenue_uncon"] - merged["revenue_con"]
merged["volume_diff_ltr"] = merged["volume_uncon"] - merged["volume_con"]

sku_level_diff = merged[[
    "sku", "units_uncon", "units_con", "unit_diff",
    "revenue_uncon", "revenue_con", "revenue_diff",
    "volume_uncon", "volume_con", "volume_diff_ltr"
]].copy()

# merge metadata & flags
sku_level_diff = sku_level_diff.merge(sku_meta, on="sku", how="left")
sku_level_diff = sku_level_diff.merge(sku_constraints, on="sku", how="left")

# ---------------------- Build impact_df with natural-language profile ----------------------
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

constraint_flag_cols = [c for c in sku_constraints.columns if str(c).startswith("Constraint_")]
records = []
for col in constraint_flag_cols:
    flagged = sku_level_diff[sku_level_diff.get(col, 0) == 1]
    units_lost = float(flagged["unit_diff"].sum())
    revenue_lost = float(flagged["revenue_diff"].sum())
    volume_lost = float(flagged["volume_diff_ltr"].sum())
    # pass the constraint column name so the profile builder can consult shelf_constraints
    natural_profile = build_natural_profile(flagged, constraint_col=col)
    # constraint_types metadata if exists
    c_row = constraint_types[constraint_types.get("Constraint_ID", "") == col] if "Constraint_ID" in constraint_types.columns else pd.DataFrame()
    c_type = c_row["Constraint_Type"].values[0] if not c_row.empty and "Constraint_Type" in c_row.columns else "-"
    space_perc = c_row["Space_Perc"].values[0] if not c_row.empty and "Space_Perc" in c_row.columns else ""
    # NOTE: we store the human readable profile as 'Constraint_Profile' for display everywhere
    records.append({
        "Constraint_Profile": natural_profile,
        "Constraint_ID_Internal": col,
        "Constraint_Type": c_type,
        "Width_%_Limit": space_perc,
        "Units_Lost": units_lost,
        "Revenue_Lost": revenue_lost,
        "Volume_Lost_Ltr": volume_lost,
    })

impact_df = pd.DataFrame(records).sort_values(by="Revenue_Lost", ascending=False) if records else pd.DataFrame()


# ---------------------- Compact display: breakdown as expanders ----------------------
st.markdown("## 🔍 Breakdown by Constraint Type (compact)")
if impact_df.empty:
    st.info("No constraint flags (Constraint_...) found in SKU constraints mapping.")
else:
    for _, r in impact_df.iterrows():
        # Use the human readable profile in the expander title instead of a Constraint_ID
        profile_label = r["Constraint_Profile"]
        with st.expander(f"{profile_label} — ₹{r['Revenue_Lost']:.2f} lost — {int(round(r['Units_Lost']))} units"):
            st.markdown(f"**Type:** {r['Constraint_Type']}")
            st.markdown(f"**Width Limit %:** {r['Width_%_Limit']}")
            st.markdown(f"**Profile:** {profile_label}")
            sample_flagged = sku_level_diff[sku_level_diff.get(r['Constraint_ID_Internal'], 0) == 1][["sku"] + ([c for c in ["manufacturer", "brand_family"] if c in sku_level_diff.columns])].head(8)
            if not sample_flagged.empty:
                st.markdown("**Sample SKUs affected:**")
                st.dataframe(sample_flagged, use_container_width=True)
            else:
                st.markdown("_No SKUs flagged for this constraint._")

# ---------------------- Totals and CSV download ----------------------
st.markdown("## Summary")
total_lost_units = sku_level_diff["unit_diff"].sum()
total_lost_revenue = sku_level_diff["revenue_diff"].sum()
total_lost_volume = sku_level_diff["volume_diff_ltr"].sum()
c1, c2, c3 = st.columns([1,1,1])
c1.metric("Total Units Lost", int(round(total_lost_units)))
c2.metric("Total Revenue Lost (₹)", float(round(total_lost_revenue,2)))
c3.metric("Total Volume Lost (L)", float(round(total_lost_volume,3)))

st.markdown("### Export")
# Export the SKU-level diff plus the readable constraint profile mapping
export_df = sku_level_diff.copy()
# attach profile per constraint as separate columns for reference (if needed)
for _, r in impact_df.iterrows():
    export_df[r['Constraint_ID_Internal'] + "_Profile"] = np.where(export_df.get(r['Constraint_ID_Internal'], 0) == 1, r['Constraint_Profile'], "")

csv_bytes = export_df.to_csv(index=False).encode("utf-8")
st.download_button("Download SKU-level Diff CSV", data=csv_bytes, file_name="sku_level_diff.csv", mime="text/csv")

# ---------------------- Interactive Agent (presets in main area) ----------------------
st.markdown("## 🧠 Interactive Data Agent")
preset_queries = [
    "Top 10 SKUs by revenue_diff",
    "Top 10 SKUs by unit_diff",
    "Which constraints cause the largest revenue loss?",
    "Correlation between revenue_diff and unit_diff",
    "List manufacturers with highest revenue loss"
]
pcol, qcol = st.columns([1,3])
with pcol:
    st.markdown("**Presets**")
    for pq in preset_queries:
        if st.button(pq, key=f"preset_{pq}"):
            st.session_state.agent_query = pq
with qcol:
    user_query = st.text_input("Agent query (type or click a preset)", value=st.session_state.get("agent_query", "Top 10 SKUs by revenue_diff"))
    st.write("Tip: ask crisp questions like 'Top 5 SKUs by revenue_diff' or 'Show constraints with revenue_loss > 10000'")

# prepare agent_view
agent_df = sku_level_diff.copy()
flag_cols = [c for c in agent_df.columns if str(c).startswith("Constraint_")]
meta_cols = [c for c in ["sku", "manufacturer", "brand_family", "pack_type", "ptc_segment"] if c in agent_df.columns]
numeric_cols = [c for c in ["units_uncon", "units_con", "unit_diff", "revenue_uncon", "revenue_con", "revenue_diff", "volume_uncon", "volume_con", "volume_diff_ltr"] if c in agent_df.columns]
agent_view_cols = meta_cols + numeric_cols + flag_cols
agent_view = agent_df[agent_view_cols].copy()
# st.dataframe(agent_view.head(6), use_container_width=True)

# init agent
agent = None
if OPENAI_API_KEY:
    try:
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.0, model="openai/gpt-4o-mini")
        agent = create_pandas_dataframe_agent(llm, agent_view, verbose=False, max_iterations=3, allow_dangerous_code=True)
    except Exception as e:
        st.error(f"LangChain agent initialization failed: {e}")
        agent = None
else:
    st.info("No OPENAI_API_KEY: agent disabled")

if st.button("Run Agent Query"):
    if not user_query.strip():
        st.warning("Enter a query.")
    elif agent is None:
        st.error("Agent not available.")
    else:
        guard = f"""
You are an analytical assistant with access ONLY to a pandas DataFrame named `agent_view`.
Column context:
- `units_uncon`, `revenue_uncon`, `volume_uncon`: unconstrained scenario
- `units_con`, `revenue_con`, `volume_con`: constrained scenario
- `unit_diff`, `revenue_diff`, `volume_diff_ltr`: unconstrained minus constrained (positive means loss)
Rules:
1) Use ONLY columns from `agent_view`.
2) If a table/list is requested, return Python pandas code using `agent_view` and then the result.
3) If you cannot answer, return exactly: "insufficient data to answer".
User: {user_query}
"""
        try:
            with st.spinner("Agent running..."):
                resp = agent.run(guard)
            st.markdown("**Agent response**")
            st.write(resp)
        except Exception as e:
            st.error(f"Agent run failed: {e}")

# ---------------------- Batch GPT Insights (guarded) ----------------------
st.markdown("## 🤖 Gen AI Insights")
if st.button("Generate Insights"):
    if openai_client is None:
        st.error("OpenAI client not configured.")
    else:
        sample_impact = impact_df.head(30).fillna("").to_string(index=False) if not impact_df.empty else "no impact rows"
        sample_top = sku_level_diff[["sku", "brand_family", "unit_diff", "revenue_diff", "volume_diff_ltr"]].sort_values(by="unit_diff", ascending=False).head(20).to_string(index=False)
        prompt = f"""
You are a retail optimization analyst. Use ONLY the facts provided below. If asked to compute something impossible from the facts, reply exactly "insufficient data".

Summary:
- Total Units Lost: {int(round(total_lost_units))}
- Total Revenue Lost: {round(total_lost_revenue,2)}
- Total Volume Lost (L): {round(total_lost_volume,3)}

Constraint breakdown (sample):
{sample_impact}

Top SKU Losses (sample):
{sample_top}

Rules:
- The column `unit_diff` is unconstrained minus constrained units. Positive means loss due to constraint, negative means gain.
- The column `revenue_diff` is unconstrained minus constrained revenue. Positive means loss, negative means gain.
- The column `volume_diff_ltr` is unconstrained minus constrained volume (liters). Positive means loss, negative means gain.

Provide insights such as:
1. Which constraint types are most damaging (largest positive values for units, revenue, or volume lost)?
2. Patterns across manufacturers, brand families, or ptc segments for all three metrics.
3. Recommendations for where to focus optimization to reduce the most harmful constraints (for units, revenue, and volume).
4. Any anomalies worth flagging (e.g., constraints with negative values that show gains, or unexpected high losses in any metric).

Findings, Patterns, Correlations, Recommendations, Anomalies.
"""
        with st.spinner("Generating insights..."):
            try:
                gresp = openai_client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a concise retail optimization analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                st.markdown("**Insights**")
                st.write(gresp.choices[0].message.content)
            except Exception as e:
                st.error(f"LLM insights failed: {e}")

st.markdown("---")
