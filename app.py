import base64
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
from scipy import stats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="STI Knowledge Research Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def set_background_image(image_file):
    image_path = Path(image_file)
    if not image_path.is_absolute():
        image_path = Path(__file__).parent / image_path

    if not image_path.exists():
        st.warning(f"Background image not found: {image_path}")
        return

    image_ext = image_path.suffix.lstrip(".").lower() or "jpg"
    encoded_image = base64.b64encode(image_path.read_bytes()).decode()

    st.markdown(
        f"""
<style>
.stApp {{
    background-image:
        linear-gradient(rgba(10, 10, 46, 0.82), rgba(10, 10, 46, 0.9)),
        url("data:image/{image_ext};base64,{encoded_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
.main,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {{
    background: transparent !important;
}}
</style>
""",
        unsafe_allow_html=True
    )

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Glassmorphism sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
    color: white !important;
    backdrop-filter: blur(12px) saturate(120%) !important;
    -webkit-backdrop-filter: blur(12px) saturate(120%) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.37) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    margin: 8px !important;
}

/* Ensure inner elements remain legible */
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label { color: white !important; }

/* Let the app background show through the glass */
[data-testid="stAppViewContainer"] > div:first-child > div { background: transparent !important; }

.stApp { background-color: #0a0a2e; }
.main  { background-color: #0a0a2e; }
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px;
    padding: 12px 16px;
    color: white !important;
}
div[data-testid="metric-container"] * { color: white !important; }
h1, h2, h3, h4 { color: white !important; }
p, li, label   { color: #ccc !important; }
hr { border-color: rgba(255,255,255,0.15) !important; }
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
}
.stTabs [data-baseweb="tab"] { color: white !important; }
.stTabs [aria-selected="true"] {
    background: rgba(74,144,217,0.35) !important;
    border-radius: 6px;
}
details { background: rgba(255,255,255,0.05); border-radius: 8px; }
.legend-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 12px;
}
.legend-row {
    display: flex; align-items: center; gap: 10px; margin: 4px 0;
}
.legend-dot {
    width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0;
}
/* Make styles apply when the sidebar is collapsed into a dialog (mobile/small screens) */
div[role="dialog"] section[data-testid="stSidebar"],
div[role="dialog"] section[data-testid="stSidebar"] * {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
    color: white !important;
    backdrop-filter: blur(12px) saturate(120%) !important;
    -webkit-backdrop-filter: blur(12px) saturate(120%) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.37) !important;
    border-radius: 14px !important;
}

/* Global fallbacks to ensure root background and text colors apply on all clients */
html, body, .stApp, .main, [data-testid="stAppViewContainer"] {
    background-color: #0a0a2e !important;
    color: #fff !important;
}

/* Ensure upload area and buttons remain visible */
div[data-testid="stFileUploader"], div[data-testid="stFileUploader"] * { color: white !important; background: rgba(255,255,255,0.02) !important; }
.stButton>button { background-color: #4A90D9 !important; color: white !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

set_background_image("Background.jpg")

PLOT_BG    = "#0a0a2e"
PAPER_BG   = "#0a0a2e"
FONT_CLR   = "white"
MALE_CLR   = "#4A90D9"
FEMALE_CLR = "#E05C8A"
PLOTLY_CONFIG = {
    "scrollZoom": True,
    "displayModeBar": True,
    "modeBarButtonsToAdd": ["zoom2d", "pan2d", "select2d", "lasso2d"],
    "displaylogo": False,
}

# Lock a Plotly template so colors/backgrounds are deterministic on Streamlit Cloud
pio.templates["sti_dark"] = go.layout.Template(layout=go.Layout(
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PAPER_BG,
    font=dict(color=FONT_CLR),
    colorway=[MALE_CLR, FEMALE_CLR]
))
pio.templates.default = "sti_dark"

def dark_layout(**kwargs):
    base = dict(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_CLR),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", color=FONT_CLR),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", color=FONT_CLR),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_CLR)),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    base.update(kwargs)
    return base

# ── Indicator labels from Chapter 4 ──────────────────────────────────────────
INDICATOR_LABELS = {
    # Table 3 – Causes & Transmission
    "CT1": "STIs can be transmitted through unprotected sexual intercourse",
    "CT2": "Sharing needles or syringes can spread STIs",
    "CT3": "STIs can be transmitted through oral sex",
    "CT4": "A person can have an STI without showing any symptoms",
    "CT5": "Some STIs can be transmitted through contact with infected blood",
    "CT6": "Having multiple sexual partners increases the risk of getting STIs",
    # Table 4 – Signs & Symptoms
    "SS1": "STIs can cause unusual discharge from the penis or vagina",
    "SS2": "Pain or burning sensation during urination may indicate an STI",
    "SS3": "Rashes or sores around the genital area can be signs of an STI",
    "SS4": "Fever or body pain may occur with some STIs",
    "SS5": "Not all STIs show visible symptoms immediately after infection",
    "SS6": "Some STIs may remain asymptomatic, especially in women",
    # Table 5 – Prevention & Control
    "PC1": "Proper and consistent condom use can reduce the risk of STIs",
    "PC2": "Abstaining from sexual activity is the most effective way to prevent STIs",
    "PC3": "Having one faithful and uninfected partner lowers the risk of STIs",
    "PC4": "Regular medical check-ups help in early detection of STIs",
    "PC5": "Avoiding the sharing of needles can prevent STI transmission",
    "PC6": "Vaccines can protect against certain STIs such as HPV and Hepatitis B",
    # Table 6 – Treatment & Complications
    "TC1": "Many STIs can be treated effectively with proper medical care",
    "TC2": "Some STIs require long-term management rather than a one-time treatment",
    "TC3": "Ignoring STI symptoms can lead to serious health problems",
    "TC4": "Untreated STIs may cause infertility or reproductive complications",
    "TC5": "HIV/AIDS cannot be cured with antibiotics",
    "TC6": "Early diagnosis and treatment can help prevent the spread of STIs",
    # Table 8 – Personal Factors
    "PF1": "I am interested in learning more about sexual health and STIs",
    "PF2": "I believe STI knowledge is important for my personal health",
    "PF3": "I feel embarrassed talking about sexual health topics",
    "PF4": "I prefer to keep sexual health issues private",
    "PF5": "Learning about STIs helps me make better decisions",
    "PF6": "I feel confident seeking information about STIs when needed",
    # Table 9 – Social Factors
    "SF1": "My peers influence how I view sexual health issues",
    "SF2": "I discuss sexual health topics with my friends or classmates",
    "SF3": "I feel comfortable talking about STIs with people my age",
    "SF4": "Peer opinions affect my awareness of STI prevention",
    "SF5": "I receive information about STIs through social interactions",
    "SF6": "My social environment encourages responsible sexual health behavior",
    # Table 10 – Educational Factors
    "EF1": "I have learned about STIs through community programs or informal learning",
    "EF2": "I receive enough information about STI prevention from non-school sources",
    "EF3": "Health workers or community leaders are approachable when discussing sexual health",
    "EF4": "Community discussions or peer conversations help clarify misconceptions about STIs",
    "EF5": "Seminars, workshops, or outreach programs improve my understanding of STIs",
    "EF6": "Informal education and community-based learning play an important role in my awareness",
    # Table 11 – Media Exposure
    "MF1": "I get information about STIs from social media platforms",
    "MF2": "I have seen STI-related educational content online",
    "MF3": "The media influences my understanding of sexual health",
    "MF4": "Online information increases my awareness of STI prevention",
    "MF5": "I verify STI information obtained from media sources",
    "MF6": "The media plays an important role in spreading STI awareness",
}

def score_legend_html():
    items = [
        ("#2ecc71", "3.25 – 4.00", "Highly Knowledgeable"),
        ("#4A90D9", "2.50 – 3.24", "Knowledgeable"),
        ("#f39c12", "1.75 – 2.49", "Somewhat Knowledgeable"),
        ("#e74c3c", "1.00 – 1.74", "Not Knowledgeable"),
    ]
    rows = "".join(
        f"<div class='legend-row'>"
        f"<div class='legend-dot' style='background:{c}'></div>"
        f"<span style='color:#ccc;font-size:12px'><b style='color:white'>{rng}</b> — {lbl}</span>"
        f"</div>"
        for c, rng, lbl in items
    )
    return f"<div class='legend-box'><p style='color:#aaa;font-size:11px;margin:0 0 6px 0'>📏 Score Legend (Weighted Mean)</p>{rows}</div>"

def interp_color(mean):
    if mean >= 3.25: return "#2ecc71"
    elif mean >= 2.50: return "#4A90D9"
    elif mean >= 1.75: return "#f39c12"
    else: return "#e74c3c"

def interp_label(mean):
    if mean >= 3.25: return "Highly Knowledgeable"
    elif mean >= 2.50: return "Knowledgeable"
    elif mean >= 1.75: return "Somewhat Knowledgeable"
    else: return "Not Knowledgeable"

# ── Load & prepare data ───────────────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file):
    # Try reading the Excel file with the expected sheet name first, then
    # fall back to the first sheet if that fails. This makes the loader
    # more robust to user-provided files with slightly different layouts.
    df = None
    last_exc = None
    try:
        df = pd.read_excel(uploaded_file, sheet_name="50 Respondnets ", header=1, engine='openpyxl')
    except Exception as e:
        last_exc = e
        try:
            # Try the first sheet with a conventional header
            df = pd.read_excel(uploaded_file, sheet_name=0, header=0, engine='openpyxl')
        except Exception as e2:
            last_exc = e2
            st.error(f"Failed to read uploaded Excel file: {last_exc}")
            st.stop()

    # Promote second header row if present and reset index (preserve existing
    # behavior but guard against empty files)
    if df is None or df.empty:
        st.error("Uploaded file is empty or could not be parsed. Please check the file and try again.")
        st.stop()

    if not df.empty:
        # If the first row looks like column names (strings) and there is a
        # duplicated header row, promote it. This mirrors the prior logic but
        # avoids failing when header selection differs.
        try:
            df.columns = df.iloc[0].astype(str).tolist()
            df = df.iloc[1:].reset_index(drop=True)
        except Exception:
            # If promoting fails, continue with the dataframe as read.
            pass

    # Sanitize column names: strip whitespace, collapse inner spaces, and make unique by suffixing duplicates
    new_cols = []
    seen = {}
    for col in df.columns:
        col_str = '' if pd.isna(col) else str(col)
        col_clean = " ".join(col_str.strip().split())
        if col_clean == '':
            col_clean = 'unnamed'
        if col_clean in seen:
            seen[col_clean] += 1
            col_final = f"{col_clean}.{seen[col_clean]}"
        else:
            seen[col_clean] = 0
            col_final = col_clean
        new_cols.append(col_final)
    df.columns = new_cols

    # Normalize Respondents/ID column name (handle 'Respondents ', 'Respondent', etc.)
    id_col = None
    for c in df.columns:
        if c.lower().startswith('respondent'):
            id_col = c
            break
    if id_col:
        df = df.rename(columns={id_col: 'ID'})

    # Drop rows that don't look like respondent rows (require numeric ID if available, else numeric Age)
    if 'ID' in df.columns:
        df = df[pd.to_numeric(df['ID'], errors='coerce').notna()].copy()
    elif 'Age' in df.columns:
        df = df[pd.to_numeric(df['Age'], errors='coerce').notna()].copy()
    else:
        st.warning("Uploaded file missing expected ID/Age columns; data may be malformed.")

    sti_cols = ['CT1','CT2','CT3','CT4','CT5','CT6',
                'SS1','SS2','SS3','SS4','SS5','SS6',
                'PC1','PC2','PC3','PC4','PC5','PC6',
                'TC1','TC2','TC3','TC4','TC5','TC6']
    ant_cols = ['PF1','PF2','PF3','PF4','PF5','PF6',
                'SF1','SF2','SF3','SF4','SF5','SF6',
                'EF1','EF2','EF3','EF4','EF5','EF6',
                'MF1','MF2','MF3','MF4','MF5','MF6']
    num_cols = ['Age','Sex'] + sti_cols + ant_cols

    # Convert known numeric columns to numeric types
    df = df.assign(**{c: pd.to_numeric(df[c], errors='coerce') for c in num_cols if c in df.columns})

    # Normalize gender values: support 1/0, 'M'/'F', or textual 'Male'/'Female'
    if 'Sex' in df.columns:
        gender_series = df['Sex'].map({1: 'Male', 0: 'Female'}).fillna(df['Sex'])
        gender_series = (
            gender_series.astype(str)
            .str.strip()
            .replace({'M': 'Male', 'F': 'Female', 'm': 'Male', 'f': 'Female', 'male': 'Male', 'female': 'Female'})
            .str.title()
        )
        df['Gender'] = gender_series
    else:
        df['Gender'] = np.nan

    df = df.assign(
        CT_avg     = df[['CT1','CT2','CT3','CT4','CT5','CT6']].mean(axis=1),
        SS_avg     = df[['SS1','SS2','SS3','SS4','SS5','SS6']].mean(axis=1),
        PC_avg     = df[['PC1','PC2','PC3','PC4','PC5','PC6']].mean(axis=1),
        TC_avg     = df[['TC1','TC2','TC3','TC4','TC5','TC6']].mean(axis=1),
        PF_avg     = df[['PF1','PF2','PF3','PF4','PF5','PF6']].mean(axis=1) if all(c in df.columns for c in ['PF1','PF6']) else np.nan,
        SF_avg     = df[['SF1','SF2','SF3','SF4','SF5','SF6']].mean(axis=1) if all(c in df.columns for c in ['SF1','SF6']) else np.nan,
        EF_avg     = df[['EF1','EF2','EF3','EF4','EF5','EF6']].mean(axis=1) if all(c in df.columns for c in ['EF1','EF6']) else np.nan,
        MF_avg     = df[['MF1','MF2','MF3','MF4','MF5','MF6']].mean(axis=1) if all(c in df.columns for c in ['MF1','MF6']) else np.nan,
    )
    df = df.assign(
        Overall    = df[['CT_avg','SS_avg','PC_avg','TC_avg']].mean(axis=1),
        Ant_Overall= df[['PF_avg','SF_avg','EF_avg','MF_avg']].mean(axis=1),
    )

    def classify(s):
        if s >= 3.25: return "Highly Knowledgeable"
        elif s >= 2.50: return "Knowledgeable"
        elif s >= 1.75: return "Somewhat Knowledgeable"
        else: return "Not Knowledgeable"

    df = df.assign(
        Knowledge_Level = df['Overall'].apply(classify),
        Age_Group       = pd.cut(df['Age'], bins=[17,20,25], labels=['18–20','21–25'])
    )
    return df

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📂 Data Source")
uploaded = st.sidebar.file_uploader("Upload Excel File", type=["xlsx","xls"])

if uploaded is None:
    st.warning("⬆️ Please upload the Excel data file using the sidebar to begin.")
    st.stop()

df = load_data(uploaded)

st.sidebar.divider()
st.sidebar.markdown("## 🔍 Filters")
sel_gender = st.sidebar.multiselect("Gender", options=['Male','Female'], default=['Male','Female'])
sel_age    = st.sidebar.multiselect("Age Group", options=['18–20','21–25'], default=['18–20','21–25'])
sel_know   = st.sidebar.multiselect(
    "Knowledge Level",
    options=['Highly Knowledgeable','Knowledgeable','Somewhat Knowledgeable','Not Knowledgeable'],
    default=['Highly Knowledgeable','Knowledgeable','Somewhat Knowledgeable','Not Knowledgeable']
)

fdf = df[
    df['Gender'].isin(sel_gender) &
    df['Age_Group'].isin(sel_age) &
    df['Knowledge_Level'].isin(sel_know)
].copy()

st.sidebar.divider()
st.sidebar.markdown(f"**Showing {len(fdf)} / {len(df)} respondents**")
st.sidebar.dataframe(
    fdf[['ID','Age','Gender','Overall']].rename(columns={'Overall':'Score'})
      .assign(Score=lambda x: x['Score'].round(2)).sort_values('ID'),
    height=380, hide_index=True
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center; color:white; margin-bottom:4px'>
    📊 STI Knowledge Research Dashboard
</h1>
<p style='text-align:center; color:#aaa; font-size:14px; margin-top:0'>
    Gender Disparities in Knowledge of Sexually Transmitted Infections (STIs) Among Out-of-School Youth
</p>
""", unsafe_allow_html=True)
st.divider()

if len(fdf) == 0:
    st.warning("⚠️ No respondents match the current filters.")
    st.stop()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("👥 Respondents", len(fdf))
k2.metric("♂ Male",  int((fdf['Gender']=='Male').sum()))
k3.metric("♀ Female", int((fdf['Gender']=='Female').sum()))
k4.metric("📈 Avg Score",  f"{fdf['Overall'].mean():.2f}")
k5.metric("📊 Std Dev",    f"{fdf['Overall'].std():.2f}")
st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Dashboard",
    "📚 STI Knowledge",
    "🔬 Antecedent Factors",
    "⚖️ Gender Comparison (Table 13)",
    "🏷️ Indicator Legend",
    "📋 Raw Data"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("#### 🔵 Age × Sex Distribution (Bubble)")
        age_sex  = fdf.groupby(['Age','Gender']).size().reset_index(name='Count')
        male_b   = age_sex[age_sex['Gender']=='Male']
        female_b = age_sex[age_sex['Gender']=='Female']

        fig_bubble = go.Figure()
        fig_bubble.add_trace(go.Scatter(
            x=male_b['Age'], y=[1.2]*len(male_b), mode='markers+text',
            marker=dict(size=male_b['Count']*18, color=MALE_CLR, opacity=1, line=dict(color='white',width=1)),
            text=male_b['Count'], textposition='middle center',
            textfont=dict(color='white',size=11,family='Arial Black'), name='Male',
            hovertemplate='Age %{x} | Male: %{text}<extra></extra>'
        ))
        fig_bubble.add_trace(go.Scatter(
            x=female_b['Age'], y=[0.8]*len(female_b), mode='markers+text',
            marker=dict(size=female_b['Count']*18, color=FEMALE_CLR, opacity=1, line=dict(color='white',width=1)),
            text=female_b['Count'], textposition='middle center',
            textfont=dict(color='white',size=11,family='Arial Black'), name='Female',
            hovertemplate='Age %{x} | Female: %{text}<extra></extra>'
        ))
        fig_bubble.update_layout(**dark_layout(height=520, margin=dict(l=40, r=20, t=50, b=80)), title='Male (top row) vs Female (bottom row) per Age', title_font_size=12, dragmode='zoom')
        fig_bubble.update_xaxes(title='Age', tickvals=list(range(18,26)))
        fig_bubble.update_yaxes(visible=False, range=[0.2,1.8])
        st.plotly_chart(fig_bubble, width='stretch', config=PLOTLY_CONFIG)

    with col_right:
        st.markdown("#### ⚤ Sex Split")
        gender_cnt = fdf['Gender'].value_counts()
        fig_donut = go.Figure(go.Pie(
            labels=gender_cnt.index, values=gender_cnt.values, hole=0.55,
            marker=dict(colors=[MALE_CLR,FEMALE_CLR], line=dict(color='white',width=2)),
            textinfo='label+percent',
        ))
        fig_donut.update_layout(**dark_layout(height=230, margin=dict(l=10,r=10,t=10,b=10)))
        st.plotly_chart(fig_donut, width='stretch')

        st.markdown("#### 🏅 Knowledge Level")
        kl_order  = ['Highly Knowledgeable','Knowledgeable','Somewhat Knowledgeable','Not Knowledgeable']
        kl_colors = ['#2ecc71','#4A90D9','#f39c12','#e74c3c']
        kl_cnt    = fdf['Knowledge_Level'].value_counts().reindex(kl_order, fill_value=0)
        fig_kl = go.Figure(go.Bar(
            x=kl_cnt.values, y=kl_cnt.index, orientation='h',
            marker_color=kl_colors, text=kl_cnt.values, textposition='outside',
        ))
        fig_kl.update_layout(**dark_layout(height=230, margin=dict(l=10,r=40,t=10,b=30)), xaxis_title='Count')
        st.plotly_chart(fig_kl, width='stretch')

    st.divider()

    # Score legend in dashboard
    st.markdown(score_legend_html(), unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📊 Knowledge Level × Gender")
        ct = pd.crosstab(fdf['Knowledge_Level'], fdf['Gender']).reindex(kl_order, fill_value=0)
        fig_gk = go.Figure()
        for gender, color in [('Male',MALE_CLR),('Female',FEMALE_CLR)]:
            if gender in ct.columns:
                fig_gk.add_trace(go.Bar(
                    x=ct.index, y=ct[gender], name=gender, marker_color=color,
                    text=ct[gender], textposition='outside',
                ))
        fig_gk.update_layout(**dark_layout(height=300, barmode='group'))
        st.plotly_chart(fig_gk, width='stretch')

    with c2:
        st.markdown("#### 📈 Age vs Overall Score")
        fig_sc = px.scatter(fdf, x='Age', y='Overall', color='Gender', symbol='Knowledge_Level',
            color_discrete_map={'Male':MALE_CLR,'Female':FEMALE_CLR},
            hover_data={'Age':True,'Overall':':.2f','Gender':True,'Knowledge_Level':True},
        )
        for gender, color in [('Male',MALE_CLR),('Female',FEMALE_CLR)]:
            gdf = fdf[fdf['Gender']==gender].dropna(subset=['Age','Overall'])
            if len(gdf) > 1:
                z = np.polyfit(gdf['Age'], gdf['Overall'], 1)
                x_range = np.linspace(gdf['Age'].min(), gdf['Age'].max(), 50)
                fig_sc.add_trace(go.Scatter(
                    x=x_range, y=np.polyval(z, x_range), mode='lines',
                    name=f'{gender} trend', line=dict(color=color,width=2,dash='dash'), showlegend=False
                ))
        fig_sc.update_layout(**dark_layout(height=300), dragmode='zoom')
        # ensure the x-axis shows each age from 18 through 25 (add 25 after 24)
        fig_sc.update_xaxes(tickmode='array', tickvals=list(range(18, 26)))
        fig_sc.update_traces(marker=dict(size=10,line=dict(width=1,color='white')), selector=dict(mode='markers'))
        st.plotly_chart(fig_sc, width='stretch', config=PLOTLY_CONFIG)

    st.divider()
    st.markdown("#### 🌡️ Score Heatmap — Age Group × Gender")
    pivot = fdf.pivot_table(values='Overall', index='Age_Group', columns='Gender', aggfunc='mean').round(2)
    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=[str(i) for i in pivot.index.tolist()],
        colorscale='Blues', text=pivot.values, texttemplate='%{text:.2f}',
        hovertemplate='Age %{y} | %{x}: %{z:.2f}<extra></extra>',
        colorbar=dict(tickfont=dict(color='white'), title=dict(text='Score',font=dict(color='white')))
    ))
    fig_heat.update_layout(**dark_layout(height=220))
    st.plotly_chart(fig_heat, width='stretch')


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — STI KNOWLEDGE
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📚 STI Knowledge Indicators")
    st.markdown("Each group has **6 indicators** rated 1–4. Charts show Male vs Female totals per indicator.")
    st.markdown(score_legend_html(), unsafe_allow_html=True)

    sti_tables = {
        "A. Causes & Transmission (Table 3)": {
            "cols": ['CT1','CT2','CT3','CT4','CT5','CT6'], "avg_col": "CT_avg",
            "overall_mean": 2.18,
        },
        "B. Signs & Symptoms (Table 4)": {
            "cols": ['SS1','SS2','SS3','SS4','SS5','SS6'], "avg_col": "SS_avg",
            "overall_mean": 2.04,
        },
        "C. Prevention & Control (Table 5)": {
            "cols": ['PC1','PC2','PC3','PC4','PC5','PC6'], "avg_col": "PC_avg",
            "overall_mean": 2.22,
        },
        "D. Treatment & Complications (Table 6)": {
            "cols": ['TC1','TC2','TC3','TC4','TC5','TC6'], "avg_col": "TC_avg",
            "overall_mean": 2.38,
        },
    }

    for tname, tinfo in sti_tables.items():
        cols   = tinfo["cols"]
        avg_c  = tinfo["avg_col"]
        male_df   = fdf[fdf['Gender']=='Male']
        female_df = fdf[fdf['Gender']=='Female']
        male_means   = [male_df[c].mean() for c in cols]
        female_means = [female_df[c].mean() for c in cols]
        overall_means= [fdf[c].mean() for c in cols]

        with st.expander(f"📌 {tname}", expanded=True):
            ch_col, stat_col = st.columns([3, 1])

            with ch_col:
                # Short label on x-axis, full label in hover
                short_labels = cols
                hover_labels = [INDICATOR_LABELS.get(c, c) for c in cols]
                male_texts   = [f"{v:.2f}" for v in male_means]
                female_texts = [f"{v:.2f}" for v in female_means]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=short_labels, y=male_means, name='Male', marker_color=MALE_CLR,
                    text=male_texts, textposition='outside',
                    customdata=hover_labels,
                    hovertemplate='<b>Male</b><br>%{customdata}<br>Mean: %{y:.2f}<extra></extra>'
                ))
                fig.add_trace(go.Bar(
                    x=short_labels, y=female_means, name='Female', marker_color=FEMALE_CLR,
                    text=female_texts, textposition='outside',
                    customdata=hover_labels,
                    hovertemplate='<b>Female</b><br>%{customdata}<br>Mean: %{y:.2f}<extra></extra>'
                ))
                # Reference lines for scale thresholds
                for threshold, color, label in [
                    (3.25,"#2ecc71","Highly Knowledgeable"),
                    (2.50,"#4A90D9","Knowledgeable"),
                    (1.75,"#f39c12","Somewhat Knowledgeable"),
                ]:
                    fig.add_hline(y=threshold, line_dash="dot", line_color=color,
                                  annotation_text=label, annotation_position="right",
                                  annotation_font_color=color, annotation_font_size=10)

                fig.update_layout(**dark_layout(height=320, barmode='group', yaxis=dict(range=[0,4.8])),
                                  title=f'{tname} — Indicator Means', title_font_size=12)
                st.plotly_chart(fig, width='stretch')

                # Indicator description table
                rows_html = "".join(
                    f"<tr><td style='color:#4A90D9;font-weight:bold;padding:3px 8px'>{c}</td>"
                    f"<td style='color:#ccc;font-size:12px;padding:3px 8px'>{INDICATOR_LABELS.get(c,'')}</td>"
                    f"<td style='color:white;font-size:12px;padding:3px 8px;text-align:center'>{om:.2f}</td>"
                    f"<td style='color:{interp_color(om)};font-size:11px;padding:3px 8px'>{interp_label(om)}</td>"
                    f"</tr>"
                    for c, om in zip(cols, overall_means)
                )
                st.markdown(
                    f"<table style='width:100%;border-collapse:collapse'>"
                    f"<thead><tr>"
                    f"<th style='color:#aaa;font-size:11px;padding:3px 8px;text-align:left'>Code</th>"
                    f"<th style='color:#aaa;font-size:11px;padding:3px 8px;text-align:left'>Indicator Description</th>"
                    f"<th style='color:#aaa;font-size:11px;padding:3px 8px;text-align:center'>Mean</th>"
                    f"<th style='color:#aaa;font-size:11px;padding:3px 8px;text-align:left'>Interpretation</th>"
                    f"</tr></thead><tbody>{rows_html}</tbody></table>",
                    unsafe_allow_html=True
                )

            with stat_col:
                st.markdown(score_legend_html(), unsafe_allow_html=True)
                st.markdown("**Group Averages**")
                male_avg    = male_df[avg_c].mean()
                female_avg  = female_df[avg_c].mean()
                overall_avg = fdf[avg_c].mean()
                st.metric("Male avg",    f"{male_avg:.2f}")
                st.metric("Female avg",  f"{female_avg:.2f}")
                st.metric("Overall avg", f"{overall_avg:.2f}")
                c_oa = interp_color(overall_avg)
                st.markdown(
                    f"<p style='color:{c_oa};font-size:12px;font-weight:bold'>{interp_label(overall_avg)}</p>",
                    unsafe_allow_html=True
                )
                diff = male_avg - female_avg
                direction = "Male higher" if diff > 0 else "Female higher"
                st.markdown(f"<p style='color:#aaa;font-size:11px'>Δ {abs(diff):.2f} — {direction}</p>",
                            unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 📊 STI Knowledge Summary — Overall Means (Table 7)")

    summary_data = {
        "Causes & Transmission": fdf['CT_avg'].mean(),
        "Signs & Symptoms":      fdf['SS_avg'].mean(),
        "Prevention & Control":  fdf['PC_avg'].mean(),
        "Treatment & Complications": fdf['TC_avg'].mean(),
    }
    grand_mean_sti = np.mean(list(summary_data.values()))

    cols_summary = st.columns(4)
    for i, (label, mean) in enumerate(summary_data.items()):
        cols_summary[i].metric(label, f"{mean:.2f}", delta=f"{interp_label(mean)}")

    st.markdown(f"<p style='text-align:center;color:#aaa;margin-top:8px'>Grand Mean: <b style='color:white'>{grand_mean_sti:.2f}</b> — <span style='color:{interp_color(grand_mean_sti)}'>{interp_label(grand_mean_sti)}</span></p>", unsafe_allow_html=True)

    group_names  = list(summary_data.keys())
    male_avgs    = [fdf[fdf['Gender']=='Male'][c].mean()   for c in ['CT_avg','SS_avg','PC_avg','TC_avg']]
    female_avgs  = [fdf[fdf['Gender']=='Female'][c].mean() for c in ['CT_avg','SS_avg','PC_avg','TC_avg']]
    overall_avgs = list(summary_data.values())

    fig_summary = go.Figure()
    fig_summary.add_trace(go.Bar(x=group_names, y=male_avgs, name='Male', marker_color=MALE_CLR,
        text=[f"{v:.2f}" for v in male_avgs], textposition='outside'))
    fig_summary.add_trace(go.Bar(x=group_names, y=female_avgs, name='Female', marker_color=FEMALE_CLR,
        text=[f"{v:.2f}" for v in female_avgs], textposition='outside'))
    for threshold, color in [(3.25,"#2ecc71"),(2.50,"#4A90D9"),(1.75,"#f39c12")]:
        fig_summary.add_hline(y=threshold, line_dash="dot", line_color=color, line_width=1)
    fig_summary.update_layout(**dark_layout(height=380, barmode='group', yaxis=dict(range=[0,4.5])),
        title='Average Score per STI Knowledge Group by Gender')
    st.plotly_chart(fig_summary, width='stretch')


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANTECEDENT FACTORS
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔬 Antecedent Factors Influencing STI Knowledge")
    st.markdown("Personal, Social, Educational, and Media Exposure factors — all rated 1–4.")
    st.markdown(score_legend_html(), unsafe_allow_html=True)

    ant_tables = {
        "A. Personal Factors (Table 8)": {
            "cols": ['PF1','PF2','PF3','PF4','PF5','PF6'], "avg_col": "PF_avg",
        },
        "B. Social Factors (Table 9)": {
            "cols": ['SF1','SF2','SF3','SF4','SF5','SF6'], "avg_col": "SF_avg",
        },
        "C. Educational Factors (Table 10)": {
            "cols": ['EF1','EF2','EF3','EF4','EF5','EF6'], "avg_col": "EF_avg",
        },
        "D. Media Exposure (Table 11)": {
            "cols": ['MF1','MF2','MF3','MF4','MF5','MF6'], "avg_col": "MF_avg",
        },
    }

    for tname, tinfo in ant_tables.items():
        cols  = tinfo["cols"]
        avg_c = tinfo["avg_col"]
        if avg_c not in fdf.columns or fdf[avg_c].isna().all():
            st.warning(f"⚠️ {tname}: data not found in uploaded file.")
            continue

        male_df   = fdf[fdf['Gender']=='Male']
        female_df = fdf[fdf['Gender']=='Female']
        male_means    = [male_df[c].mean() for c in cols if c in male_df.columns]
        female_means  = [female_df[c].mean() for c in cols if c in female_df.columns]
        overall_means = [fdf[c].mean() for c in cols if c in fdf.columns]
        valid_cols    = [c for c in cols if c in fdf.columns]

        with st.expander(f"📌 {tname}", expanded=True):
            ch_col, stat_col = st.columns([3,1])

            with ch_col:
                hover_labels = [INDICATOR_LABELS.get(c, c) for c in valid_cols]
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=valid_cols, y=male_means, name='Male', marker_color=MALE_CLR,
                    text=[f"{v:.2f}" for v in male_means], textposition='outside',
                    customdata=hover_labels,
                    hovertemplate='<b>Male</b><br>%{customdata}<br>Mean: %{y:.2f}<extra></extra>'
                ))
                fig.add_trace(go.Bar(
                    x=valid_cols, y=female_means, name='Female', marker_color=FEMALE_CLR,
                    text=[f"{v:.2f}" for v in female_means], textposition='outside',
                    customdata=hover_labels,
                    hovertemplate='<b>Female</b><br>%{customdata}<br>Mean: %{y:.2f}<extra></extra>'
                ))
                for threshold, color, label in [
                    (3.25,"#2ecc71","Highly Knowledgeable"),
                    (2.50,"#4A90D9","Knowledgeable"),
                    (1.75,"#f39c12","Somewhat Knowledgeable"),
                ]:
                    fig.add_hline(y=threshold, line_dash="dot", line_color=color,
                                  annotation_text=label, annotation_position="right",
                                  annotation_font_color=color, annotation_font_size=10)
                fig.update_layout(**dark_layout(height=320, barmode='group', yaxis=dict(range=[0,4.8])),
                                  title=f'{tname} — Indicator Means', title_font_size=12)
                st.plotly_chart(fig, use_container_width=True)

                rows_html = "".join(
                    f"<tr><td style='color:#E05C8A;font-weight:bold;padding:3px 8px'>{c}</td>"
                    f"<td style='color:#ccc;font-size:12px;padding:3px 8px'>{INDICATOR_LABELS.get(c,'')}</td>"
                    f"<td style='color:white;font-size:12px;padding:3px 8px;text-align:center'>{om:.2f}</td>"
                    f"<td style='color:{interp_color(om)};font-size:11px;padding:3px 8px'>{interp_label(om)}</td>"
                    f"</tr>"
                    for c, om in zip(valid_cols, overall_means)
                )
                st.markdown(
                    f"<table style='width:100%;border-collapse:collapse'>"
                    f"<thead><tr>"
                    f"<th style='color:#aaa;font-size:11px;padding:3px 8px;text-align:left'>Code</th>"
                    f"<th style='color:#aaa;font-size:11px;padding:3px 8px;text-align:left'>Indicator Description</th>"
                    f"<th style='color:#aaa;font-size:11px;padding:3px 8px;text-align:center'>Mean</th>"
                    f"<th style='color:#aaa;font-size:11px;padding:3px 8px;text-align:left'>Interpretation</th>"
                    f"</tr></thead><tbody>{rows_html}</tbody></table>",
                    unsafe_allow_html=True
                )

            with stat_col:
                st.markdown(score_legend_html(), unsafe_allow_html=True)
                st.markdown("**Factor Averages**")
                m = male_df[avg_c].mean()
                f_ = female_df[avg_c].mean()
                o  = fdf[avg_c].mean()
                st.metric("Male avg",    f"{m:.2f}")
                st.metric("Female avg",  f"{f_:.2f}")
                st.metric("Overall avg", f"{o:.2f}")
                st.markdown(f"<p style='color:{interp_color(o)};font-size:12px;font-weight:bold'>{interp_label(o)}</p>",
                            unsafe_allow_html=True)
                diff = m - f_
                direction = "Male higher" if diff > 0 else "Female higher"
                st.markdown(f"<p style='color:#aaa;font-size:11px'>Δ {abs(diff):.2f} — {direction}</p>",
                            unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 📊 Antecedent Factors Summary (Table 12)")

    ant_avg_cols = ['PF_avg','SF_avg','EF_avg','MF_avg']
    ant_labels   = ['Personal Factors','Social Factors','Educational Factors','Media Exposure']
    ant_cols_present = [(c, l) for c, l in zip(ant_avg_cols, ant_labels) if c in fdf.columns and not fdf[c].isna().all()]

    if ant_cols_present:
        cols_sum = st.columns(len(ant_cols_present))
        for i, (c, l) in enumerate(ant_cols_present):
            cols_sum[i].metric(l, f"{fdf[c].mean():.2f}", delta=interp_label(fdf[c].mean()))

        grand_ant = np.mean([fdf[c].mean() for c, _ in ant_cols_present])
        st.markdown(f"<p style='text-align:center;color:#aaa;margin-top:8px'>Grand Mean: <b style='color:white'>{grand_ant:.2f}</b> — <span style='color:{interp_color(grand_ant)}'>{interp_label(grand_ant)}</span></p>", unsafe_allow_html=True)

        fig_ant_sum = go.Figure()
        for gender, color in [('Male',MALE_CLR),('Female',FEMALE_CLR)]:
            gdf  = fdf[fdf['Gender']==gender]
            avgs = [gdf[c].mean() for c, _ in ant_cols_present]
            fig_ant_sum.add_trace(go.Bar(
                x=[l for _, l in ant_cols_present], y=avgs, name=gender, marker_color=color,
                text=[f"{v:.2f}" for v in avgs], textposition='outside',
            ))
        for threshold, color in [(3.25,"#2ecc71"),(2.50,"#4A90D9"),(1.75,"#f39c12")]:
            fig_ant_sum.add_hline(y=threshold, line_dash="dot", line_color=color, line_width=1)
        fig_ant_sum.update_layout(**dark_layout(height=380, barmode='group', yaxis=dict(range=[0,4.5])),
            title='Antecedent Factor Averages by Gender')
        st.plotly_chart(fig_ant_sum, width='stretch')

        # Horizontal grouped bar chart (replacing radar)
        st.markdown("#### 📊 Factor Comparison — Male vs Female (Table 12)")
        factor_labels = [l for _, l in ant_cols_present]
        male_vals   = [fdf[fdf['Gender']=='Male'][c].mean()   for c, _ in ant_cols_present]
        female_vals = [fdf[fdf['Gender']=='Female'][c].mean() for c, _ in ant_cols_present]
        overall_vals= [fdf[c].mean() for c, _ in ant_cols_present]

        fig_hbar = go.Figure()
        fig_hbar.add_trace(go.Bar(
            y=factor_labels, x=female_vals, name='Female',
            orientation='h', marker_color=FEMALE_CLR,
            text=[f"{v:.2f}" for v in female_vals], textposition='outside',
            hovertemplate='<b>Female</b> | %{y}: %{x:.2f}<extra></extra>'
        ))
        fig_hbar.add_trace(go.Bar(
            y=factor_labels, x=male_vals, name='Male',
            orientation='h', marker_color=MALE_CLR,
            text=[f"{v:.2f}" for v in male_vals], textposition='outside',
            hovertemplate='<b>Male</b> | %{y}: %{x:.2f}<extra></extra>'
        ))
        # Threshold lines
        for threshold, color, label in [
            (3.25, "#2ecc71", "Highly Knowledgeable (3.25)"),
            (2.50, "#4A90D9", "Knowledgeable (2.50)"),
            (1.75, "#f39c12", "Somewhat Knowledgeable (1.75)"),
        ]:
            fig_hbar.add_vline(x=threshold, line_dash="dot", line_color=color,
                               annotation_text=label, annotation_position="top",
                               annotation_font_color=color, annotation_font_size=10)
        fig_hbar.update_layout(
            **dark_layout(height=320, barmode='group',
                          xaxis=dict(range=[0, 4.5], gridcolor='rgba(255,255,255,0.1)', color=FONT_CLR),
                          yaxis=dict(gridcolor='rgba(255,255,255,0.1)', color=FONT_CLR)),
            title='Antecedent Factor Means by Gender — Table 12',
            title_font_size=13,
        )
        st.plotly_chart(fig_hbar, width='stretch')


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — TABLE 13 (GENDER COMPARISON / T-TEST)
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### ⚖️ Table 13 — Difference in Knowledge Between Male and Female Respondents")
    st.markdown("Independent samples t-test results comparing gender groups across STI knowledge domains and antecedent factors.")
    st.markdown(score_legend_html(), unsafe_allow_html=True)

    male_df   = fdf[fdf['Gender']=='Male']
    female_df = fdf[fdf['Gender']=='Female']

    # Build t-test table dynamically from data
    test_variables = [
        ("Causes & Transmission", "CT_avg"),
        ("Signs & Symptoms",       "SS_avg"),
        ("Prevention & Control",   "PC_avg"),
        ("Treatment & Complications", "TC_avg"),
        ("Personal Factors",       "PF_avg"),
        ("Social Factors",         "SF_avg"),
        ("Educational Factors",    "EF_avg"),
        ("Media Exposure",         "MF_avg"),
        ("Overall STI Knowledge",  "Overall"),
    ]

    ttest_rows = []
    for label, col in test_variables:
        if col not in fdf.columns or fdf[col].isna().all():
            continue
        m_vals = male_df[col].dropna()
        f_vals = female_df[col].dropna()
        if len(m_vals) < 2 or len(f_vals) < 2:
            continue
        mean_all = fdf[col].mean()
        sd_all   = fdf[col].std()
        t_stat, p_val = stats.ttest_ind(m_vals, f_vals, equal_var=False)
        df_val   = min(len(m_vals), len(f_vals)) - 1
        sig      = p_val < 0.05
        interp   = "❌ Not Accepted (Significant)" if sig else "✅ Accepted (Not Significant)"
        ttest_rows.append({
            "Variable": label,
            "Male Mean": round(m_vals.mean(), 2),
            "Female Mean": round(f_vals.mean(), 2),
            "Overall Mean": round(mean_all, 2),
            "SD": round(sd_all, 2),
            "t": round(t_stat, 3),
            "df": df_val,
            "p": round(p_val, 3),
            "Interpretation": interp,
            "Significant": sig,
        })

    if ttest_rows:
        # Summary table
        ttest_df = pd.DataFrame(ttest_rows)
        st.markdown("#### 📋 T-Test Results Summary")

        # Styled HTML table
        header_cells = "".join(
            f"<th style='color:#aaa;font-size:12px;padding:6px 10px;border-bottom:1px solid rgba(255,255,255,0.15);text-align:{'left' if c=='Variable' else 'center'}'>{c}</th>"
            for c in ["Variable","Male Mean","Female Mean","Overall Mean","SD","t","df","p","Interpretation"]
        )
        body_rows = ""
        for _, row in ttest_df.iterrows():
            bg = "rgba(231,76,60,0.12)" if row['Significant'] else "rgba(46,204,113,0.08)"
            body_rows += (
                f"<tr style='background:{bg}'>"
                f"<td style='color:white;font-size:12px;padding:6px 10px'>{row['Variable']}</td>"
                f"<td style='color:{MALE_CLR};font-size:12px;padding:6px 10px;text-align:center'>{row['Male Mean']:.2f}</td>"
                f"<td style='color:{FEMALE_CLR};font-size:12px;padding:6px 10px;text-align:center'>{row['Female Mean']:.2f}</td>"
                f"<td style='color:white;font-size:12px;padding:6px 10px;text-align:center'>{row['Overall Mean']:.2f}</td>"
                f"<td style='color:#aaa;font-size:12px;padding:6px 10px;text-align:center'>{row['SD']:.2f}</td>"
                f"<td style='color:#f39c12;font-size:12px;padding:6px 10px;text-align:center'>{row['t']:.3f}</td>"
                f"<td style='color:#aaa;font-size:12px;padding:6px 10px;text-align:center'>{row['df']}</td>"
                f"<td style='color:{'#e74c3c' if row['Significant'] else '#2ecc71'};font-size:12px;font-weight:bold;padding:6px 10px;text-align:center'>{row['p']:.3f}</td>"
                f"<td style='color:{'#e74c3c' if row['Significant'] else '#2ecc71'};font-size:11px;padding:6px 10px'>{row['Interpretation']}</td>"
                f"</tr>"
            )
        st.markdown(
            f"<div style='overflow-x:auto'><table style='width:100%;border-collapse:collapse'>"
            f"<thead><tr>{header_cells}</tr></thead><tbody>{body_rows}</tbody></table></div>",
            unsafe_allow_html=True
        )

        st.divider()

        # Visual: Mean comparison bars
        st.markdown("#### 📊 Male vs Female Mean by Domain")
        fig_t = go.Figure()
        fig_t.add_trace(go.Bar(
            x=ttest_df['Variable'], y=ttest_df['Male Mean'], name='Male', marker_color=MALE_CLR,
            text=[f"{v:.2f}" for v in ttest_df['Male Mean']], textposition='outside',
        ))
        fig_t.add_trace(go.Bar(
            x=ttest_df['Variable'], y=ttest_df['Female Mean'], name='Female', marker_color=FEMALE_CLR,
            text=[f"{v:.2f}" for v in ttest_df['Female Mean']], textposition='outside',
        ))
        # Mark significant ones with an annotation
        for _, row in ttest_df[ttest_df['Significant']].iterrows():
            idx = ttest_df[ttest_df['Variable']==row['Variable']].index[0]
            fig_t.add_annotation(
                x=row['Variable'], y=max(row['Male Mean'], row['Female Mean']) + 0.3,
                text="⚠️ p<.05", showarrow=False, font=dict(color='#e74c3c', size=10)
            )
        for threshold, color in [(3.25,"#2ecc71"),(2.50,"#4A90D9"),(1.75,"#f39c12")]:
            fig_t.add_hline(y=threshold, line_dash="dot", line_color=color, line_width=1)
        fig_t.update_layout(**dark_layout(height=420, barmode='group', yaxis=dict(range=[0,4.8])),
            title='Gender Comparison of Means — All Domains')
        st.plotly_chart(fig_t, width='stretch')

        st.divider()

        # P-value visualization
        st.markdown("#### 📉 P-Value Significance Chart")
        p_colors = ['#e74c3c' if row['Significant'] else '#2ecc71' for _, row in ttest_df.iterrows()]
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(
            x=ttest_df['Variable'], y=ttest_df['p'], marker_color=p_colors,
            text=[f"p={v:.3f}" for v in ttest_df['p']], textposition='outside',
            hovertemplate='<b>%{x}</b><br>p = %{y:.3f}<extra></extra>'
        ))
        fig_p.add_hline(y=0.05, line_dash="dash", line_color="#f39c12",
                        annotation_text="α = 0.05 significance threshold",
                        annotation_position="right", annotation_font_color="#f39c12")
        fig_p.update_layout(**dark_layout(height=360, yaxis=dict(range=[0, max(ttest_df['p'])+0.1])),
            title='P-Values by Domain (Red = Significant Difference, Green = No Significant Difference)')
        st.plotly_chart(fig_p, width='stretch')

        st.divider()
        st.markdown("""
#### 📝 Interpretation Notes
- **p < 0.05** → Statistically significant difference between male and female (null hypothesis **rejected**)
- **p ≥ 0.05** → No statistically significant difference (null hypothesis **accepted**)
- Based on Chapter 4 findings: significant difference was found **only in Personal Factors** (p = .012), 
  indicating a *knowledge–action gap* where personal motivation and perceived self-efficacy differ by gender 
  even when factual STI knowledge is comparable.
""")


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — INDICATOR LEGEND
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🏷️ Complete Indicator Legend")
    st.markdown("This reference table shows the full description of every indicator code used across all tables in the dashboard.")
    st.markdown(score_legend_html(), unsafe_allow_html=True)

    sections = [
        ("📌 Table 3 — Causes & Transmission (CT)", ['CT1','CT2','CT3','CT4','CT5','CT6'], "#4A90D9"),
        ("📌 Table 4 — Signs & Symptoms (SS)",      ['SS1','SS2','SS3','SS4','SS5','SS6'], "#9B59B6"),
        ("📌 Table 5 — Prevention & Control (PC)",  ['PC1','PC2','PC3','PC4','PC5','PC6'], "#2ecc71"),
        ("📌 Table 6 — Treatment & Complications (TC)", ['TC1','TC2','TC3','TC4','TC5','TC6'], "#E67E22"),
        ("📌 Table 8 — Personal Factors (PF)",      ['PF1','PF2','PF3','PF4','PF5','PF6'], "#E05C8A"),
        ("📌 Table 9 — Social Factors (SF)",        ['SF1','SF2','SF3','SF4','SF5','SF6'], "#1ABC9C"),
        ("📌 Table 10 — Educational Factors (EF)",  ['EF1','EF2','EF3','EF4','EF5','EF6'], "#F1C40F"),
        ("📌 Table 11 — Media Exposure (MF)",       ['MF1','MF2','MF3','MF4','MF5','MF6'], "#E74C3C"),
    ]

    for section_title, codes, accent in sections:
        with st.expander(section_title, expanded=True):
            # Compute means if data available
            rows_html = ""
            for i, code in enumerate(codes):
                mean_val = fdf[code].mean() if code in fdf.columns else None
                mean_str = f"{mean_val:.2f}" if mean_val is not None else "N/A"
                interp_str = interp_label(mean_val) if mean_val is not None else "—"
                interp_c   = interp_color(mean_val) if mean_val is not None else "#aaa"
                rows_html += (
                    f"<tr>"
                    f"<td style='color:{accent};font-weight:bold;font-size:13px;padding:6px 10px'>{code}</td>"
                    f"<td style='color:#ccc;font-size:13px;padding:6px 10px'>{INDICATOR_LABELS.get(code,'—')}</td>"
                    f"<td style='color:white;font-size:13px;padding:6px 10px;text-align:center'>{mean_str}</td>"
                    f"<td style='color:{interp_c};font-size:12px;padding:6px 10px'>{interp_str}</td>"
                    f"</tr>"
                )
            st.markdown(
                f"<table style='width:100%;border-collapse:collapse'>"
                f"<thead><tr>"
                f"<th style='color:#aaa;font-size:11px;padding:5px 10px;border-bottom:1px solid rgba(255,255,255,0.12);text-align:left'>Code</th>"
                f"<th style='color:#aaa;font-size:11px;padding:5px 10px;border-bottom:1px solid rgba(255,255,255,0.12);text-align:left'>Indicator Statement</th>"
                f"<th style='color:#aaa;font-size:11px;padding:5px 10px;border-bottom:1px solid rgba(255,255,255,0.12);text-align:center'>Mean</th>"
                f"<th style='color:#aaa;font-size:11px;padding:5px 10px;border-bottom:1px solid rgba(255,255,255,0.12);text-align:left'>Interpretation</th>"
                f"</tr></thead><tbody>{rows_html}</tbody></table>",
                unsafe_allow_html=True
            )


# ════════════════════════════════════════════════════════════════════════════
# TAB 6 — RAW DATA
# ════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("### 📋 Raw Respondent Data")

    base_cols = ['ID','Age','Gender','Age_Group','Knowledge_Level',
                 'CT_avg','SS_avg','PC_avg','TC_avg','Overall']
    ant_extra = [c for c in ['PF_avg','SF_avg','EF_avg','MF_avg','Ant_Overall'] if c in fdf.columns and not fdf[c].isna().all()]
    display_cols = base_cols + ant_extra

    display = fdf[display_cols].copy()
    rename_map = {
        'CT_avg':'CT Avg','SS_avg':'SS Avg','PC_avg':'PC Avg','TC_avg':'TC Avg',
        'PF_avg':'PF Avg','SF_avg':'SF Avg','EF_avg':'EF Avg','MF_avg':'MF Avg',
        'Ant_Overall':'Antecedent Overall','Age_Group':'Age Group','Knowledge_Level':'Knowledge Level'
    }
    display = display.rename(columns=rename_map)
    round_cols = [c for c in display.columns if 'Avg' in c or c == 'Overall' or c == 'Antecedent Overall']
    display = display.assign(**{c: display[c].round(2) for c in round_cols if c in display.columns})

    st.dataframe(
        display.sort_values('ID'), width='stretch', height=420,
        column_config={
            'Overall': st.column_config.ProgressColumn('Overall', min_value=1, max_value=4, format='%.2f')
        }
    )

    st.divider()
    st.markdown("#### 📥 Download Filtered Data")
    csv = display.to_csv(index=False)
    st.download_button("⬇️ Download CSV", data=csv, file_name="sti_filtered_data.csv", mime="text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<p style='text-align:center; color:#666; font-size:12px'>
    Gender Disparities in Knowledge of STIs Among Out-of-School Youth &nbsp;|&nbsp;
    Mabini Colleges, Inc. &nbsp;|&nbsp; College of Computer Studies
</p>
""", unsafe_allow_html=True)
