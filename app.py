import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from supabase import create_client, Client
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import base64

# Page configuration
st.set_page_config(
    page_title="Value Impact Assessment System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.85rem !important;
        font-weight: 700 !important;
        color: #1f77b4 !important;
        text-align: center !important;
        line-height: 1.25 !important;
        margin-bottom: 1rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.16);
    }
                      
/* Remove header toolbar background */
header[data-testid="stHeader"] > div {
    background-color: transparent !important;
}   
                        
.main {
    padding-top: 0 !important;
}

/* Make background cover entire viewport */
.stApp {
    background-image: url('https://vfsysrkgiakqfyzgxaof.supabase.co/storage/v1/object/sign/project-documents/gif%20via%20main%206.gif?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8xOGYxMzlhYS0xZTYxLTQzYjItODA0Ni1lYTE5OTgwNGU0MTEiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJwcm9qZWN0LWRvY3VtZW50cy9naWYgdmlhIG1haW4gNi5naWYiLCJpYXQiOjE3NzAwNTIwMDcsImV4cCI6MTgwMTU4ODAwN30.VpVESfoSBqQZydFxbeO0VHtRDT-kQAC0XsAu41nsseg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

/* Main content area - transparent to show background */
.main .block-container {
    background: transparent;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-image: url('https://vfsysrkgiakqfyzgxaof.supabase.co/storage/v1/object/sign/project-documents/gif%20via%20sidebar.gif?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8xOGYxMzlhYS0xZTYxLTQzYjItODA0Ni1lYTE5OTgwNGU0MTEiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJwcm9qZWN0LWRvY3VtZW50cy9naWYgdmlhIHNpZGViYXIuZ2lmIiwiaWF0IjoxNzcwMDQ5NDAyLCJleHAiOjE4MDE1ODU0MDJ9.tg-gIJ68GFnQNq1oYN-fWzZsouqoeHK3f6CmgDo29_Y');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

/* Make deploy button area transparent */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Main Back buttons - dark orange gradient */
.stButton>button[kind="secondary"] {
    background: linear-gradient(90deg, #fea45e 0%, #e56842 100%) !important;
    color: white !important;
}            

header[data-testid="stHeader"] > div:first-child {
    background-color: transparent !important;
}            

    .section-header {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        margin-top: 2.3rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 3px solid #1f77b4 !important;
        padding-bottom: 0.4rem !important;
        line-height: 1.2 !important;
    }
    .help-icon {
        background-color: #e3f2fd;
        border-radius: 50%;
        padding: 0.2rem 0.5rem;
        font-weight: bold;
        color: #1976d2;
    }
    
    /* Increase all paragraph text */
p, .stMarkdown p {
    font-size: 1.05rem !important;
}

/* Increase help text inside expanders */
.stExpander p, .stExpander div {
    font-size: 1rem !important;
}        

    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2791db 0%, #2c3e50 100%);
        color: white;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Next buttons - green text on hover */
    .stButton>button[kind="primary"]:hover {
        color: #00ff00 !important;
    }
    
    /* Back buttons - yellow text on hover */
    .stButton>button[kind="secondary"]:hover {
        color: #f7ff2d !important;
    }
            
    /* Modern score box design */
    .modern-score-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border: 2px solid #1f77b4;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    .modern-score-box h1 {
        font-size:3.4rem;
        font-weight: 700;
        color: #1f77b4;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .modern-score-box h2 {
        font-size: 2.34rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 1rem 0 0.5rem 0;
    }
    
    .modern-score-box h3 {
        font-size: 1.3rem;
        color: #34495e;
        margin: 0.5rem 0;
    }
    
    .modern-score-box h4 {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1rem 0 0 0;
    }
    
    .feasible-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        margin-top: 1rem;
    }
    
    .feasible-yes {
        background-color: #4caf50;
        color: white;
    }
    
    .feasible-no {
        background-color: #f44336;
        color: white;
    }        
</style>
""", unsafe_allow_html=True)

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Scoring configuration
SECTION_WEIGHTS = {
    "strategy": 0.10,
    "financial": 0.30,
    "risk": 0.25,
    "feasibility": 0.30,
    "stakeholder": 0.05
}

FEASIBILITY_WEIGHTS = {
    "technical": 1/6,      # Exactly 16.6666...%
    "operational": 1/6,    # Exactly 16.6666...%
    "scalability": 1/6,    # Exactly 16.6666...%
    "complexity": 0.50     # Exactly 50%
}

# Question text mapping
QUESTION_TEXT = {
    'q3a': 'Cost Savings Impact',
    'q3b': 'Cost Avoidance Impact',
    'q4a': 'Traditional Business - Market Expansion',
    'q4b': 'Traditional Business - Revenue Generation',
    'q4c': 'Traditional Business - Gross Profit Generation',
    'q5a': 'Non-Traditional Business - Market Expansion',
    'q5b': 'Non-Traditional Business - Revenue Generation',
    'q5c': 'Non-Traditional Business - Gross Profit Generation',
    'q6': 'Net Zero Carbon Emissions Impact',
    'q7a': 'Digital Transformation - Efficiencies Improvement',
    'q7b': 'Digital Transformation - Technology Improvement',
    'q8': 'Net Present Value (NPV)',
    'q9': 'Return on Investment (ROI)',
    'q10': 'Payback Period',
    'q11': 'Internal Rate of Return (IRR)',
    'q12_prob': 'Data Quality Issues - Probability',
    'q12_impact': 'Data Quality Issues - Impact',
    'q13_prob': 'Technological Complexity - Probability',
    'q13_impact': 'Technological Complexity - Impact',
    'q14_prob': 'Timeline Delays - Probability',
    'q14_impact': 'Timeline Delays - Impact',
    'q15_prob': 'Budget Constraints - Probability',
    'q15_impact': 'Budget Constraints - Impact',
    'q16': 'Technology Availability',
    'q17': 'Technical Expertise',
    'q18': 'Infrastructure Needs',
    'q19': 'Integration Complexity',
    'q20': 'Process Compatibility',
    'q21': 'Resource Availability',
    'q22': 'User Acceptance',
    'q23': 'Training Requirements',
    'q24': 'Supportability',
    'q25': 'System Performance',
    'q26': 'Expansion Flexibility',
    'q27': 'Resource Efficiency',
    'q28': 'Long-Term Costs',
    'q29': 'Environmental Impact',
    'q30': 'RACI / Clarity of Roles',
    'q31': 'Stakeholder Alignment',
    'q32': 'Data Availability',
    'q33': 'Approval Process',
    'q34': 'Adaptability',
    'q35': 'Customer Satisfaction',
    'q36': 'Suppliers/Partners Satisfaction',
    'q37': 'Brand Reputation Improvement'
}

# Initialize session state
if 'project_id' not in st.session_state:
    st.session_state.project_id = None
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

def save_project_to_db(project_name):
    """Save new project to database"""
    try:
        data = {
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        result = supabase.table("projects").insert(data).execute()
        return result.data[0]['id']
    except Exception as e:
        st.error(f"Error saving project: {str(e)}")
        return None

def save_response_to_db(project_id, question_id, response_value, score):
    """Save individual response to database"""
    try:
        data = {
            "project_id": project_id,
            "question_id": question_id,
            "response_value": response_value,
            "score": score,
            "created_at": datetime.now().isoformat()
        }
        supabase.table("responses").insert(data).execute()
    except Exception as e:
        st.error(f"Error saving response: {str(e)}")

def upload_file_to_storage(project_id, file, doc_type):
    """Upload file to Supabase Storage"""
    try:
        file_path = f"{project_id}/{doc_type}_{file.name}"
        supabase.storage.from_("project-documents").upload(
            file_path,
            file.getvalue(),
            {"content-type": file.type}
        )
        
        # Save file reference in database
        data = {
            "project_id": project_id,
            "document_type": doc_type,
            "file_name": file.name,
            "file_path": file_path,
            "uploaded_at": datetime.now().isoformat()
        }
        supabase.table("documents").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return False

def calculate_strategy_score(responses):
    """Calculate strategy section score"""
    strategy_scores = []
    
    # Cash Flow (Q3A, Q3B)
    if 'q3a' in responses:
        strategy_scores.append(responses['q3a'])
    if 'q3b' in responses:
        strategy_scores.append(responses['q3b'])
    
    # Traditional Business Growth (Q4A, Q4B, Q4C)
    if 'q4a' in responses:
        strategy_scores.append(responses['q4a'])
    if 'q4b' in responses:
        strategy_scores.append(responses['q4b'])
    if 'q4c' in responses:
        strategy_scores.append(responses['q4c'])
    
    # Non-Traditional Business Growth (Q5A, Q5B, Q5C)
    if 'q5a' in responses:
        strategy_scores.append(responses['q5a'])
    if 'q5b' in responses:
        strategy_scores.append(responses['q5b'])
    if 'q5c' in responses:
        strategy_scores.append(responses['q5c'])
    
    # Net Zero (Q6)
    if 'q6' in responses:
        strategy_scores.append(responses['q6'])
    
    # Digital Transformation (Q7A, Q7B)
    if 'q7a' in responses:
        strategy_scores.append(responses['q7a'])
    if 'q7b' in responses:
        strategy_scores.append(responses['q7b'])
    
    return (sum(strategy_scores) / len(strategy_scores) / 3) * 100 if strategy_scores else 0

def calculate_financial_score(responses):
    """Calculate financial section score"""
    weights = {'q8': 0.40, 'q9': 0.30, 'q10': 0.20, 'q11': 0.10}
    score = 0
    for q, w in weights.items():
        if q in responses:
            score += (responses[q] / 3) * w
    return score * 100

def calculate_risk_score(responses):
    """Calculate risk section score using new formula: ((Probability + Impact) / 2) * 0.25"""
    risk_scores = []
    risk_questions = ['q12', 'q13', 'q14', 'q15']
    
    for q in risk_questions:
        if f"{q}_prob" in responses and f"{q}_impact" in responses:
            # New formula: (Probability + Impact) / 2 * 0.25
            individual_risk_score = ((responses[f"{q}_prob"] + responses[f"{q}_impact"]) / 2) * 0.25
            risk_scores.append(individual_risk_score)
    
    # Overall Risk Score = (Sum of all 4 individual risk scores / 3) * 25%
    if risk_scores:
        total_risk = sum(risk_scores) / 3
        return total_risk * 100  # Convert to percentage
    return 0

def calculate_feasibility_score(responses):
    """Calculate feasibility section score - returns contribution out of 30%"""
    # Technical Feasibility (Q16-Q19)
    tech_weights = {'q16': 0.30, 'q17': 0.20, 'q18': 0.20, 'q19': 0.30}
    tech_score = sum((responses.get(q, 0) / 3) * w for q, w in tech_weights.items())
    tech_contribution = tech_score * (1/6) * 30  # 16.67% of 30%
    
    # Operational Feasibility (Q20-Q24)
    op_weights = {'q20': 0.20, 'q21': 0.20, 'q22': 0.20, 'q23': 0.20, 'q24': 0.20}
    op_score = sum((responses.get(q, 0) / 3) * w for q, w in op_weights.items())
    op_contribution = op_score * (1/6) * 30  # 16.67% of 30%
    
    # Scalability & Sustainability (Q25-Q29)
    scale_weights = {'q25': 0.30, 'q26': 0.20, 'q27': 0.20, 'q28': 0.15, 'q29': 0.15}
    scale_score = sum((responses.get(q, 0) / 3) * w for q, w in scale_weights.items())
    scale_contribution = scale_score * (1/6) * 30  # 16.67% of 30%
    
    # Complexity (Q30-Q34)
    complex_weights = {'q30': 0.20, 'q31': 0.20, 'q32': 0.20, 'q33': 0.20, 'q34': 0.20}
    complex_score = sum((responses.get(q, 0) / 3) * w for q, w in complex_weights.items())
    complex_contribution = complex_score * 0.50 * 30  # 50% of 30%
    
    # Total feasibility contribution (already out of 30, not 100)
    total_contribution = tech_contribution + op_contribution + scale_contribution + complex_contribution
    
    # For display purposes, calculate the percentage within feasibility
    feasibility_percentage = (total_contribution / 30) * 100
    
    return feasibility_percentage

def calculate_stakeholder_score(responses):
    """Calculate stakeholder impact score - all 3 questions contribute 33.33% each"""
    stakeholder_scores = []
    
    # Customer Satisfaction (33.33%)
    if 'q35' in responses:
        stakeholder_scores.append((responses['q35'] / 3) * 0.3333)
    
    # Supplier/Partner Satisfaction (33.33%)
    if 'q36' in responses:
        stakeholder_scores.append((responses['q36'] / 3) * 0.3333)
    
    # Brand Reputation (33.33%)
    if 'q37' in responses:
        stakeholder_scores.append((responses['q37'] / 3) * 0.3333)
    
    return sum(stakeholder_scores) * 100 if stakeholder_scores else 0

def calculate_total_score(responses):
    """Calculate total weighted score"""
    strategy = calculate_strategy_score(responses) * SECTION_WEIGHTS['strategy']
    financial = calculate_financial_score(responses) * SECTION_WEIGHTS['financial']
    risk = calculate_risk_score(responses) * SECTION_WEIGHTS['risk']
    feasibility = calculate_feasibility_score(responses) * SECTION_WEIGHTS['feasibility']
    stakeholder = calculate_stakeholder_score(responses) * SECTION_WEIGHTS['stakeholder']
    
    total = strategy + financial + risk + feasibility + stakeholder
    
    return {
        'total': total,
        'strategy': strategy / SECTION_WEIGHTS['strategy'],
        'financial': financial / SECTION_WEIGHTS['financial'],
        'risk': risk / SECTION_WEIGHTS['risk'],
        'feasibility': feasibility / SECTION_WEIGHTS['feasibility'],
        'stakeholder': stakeholder / SECTION_WEIGHTS['stakeholder']
    }

def get_project_classification(score):
    """Determine project classification"""
    if score >= 80:
        return "Crucial", "Very High", "🟢"
    elif score >= 60:
        return "Essential", "High", "🟡"
    elif score >= 40:
        return "Optional", "Low", "🟠"
    else:
        return "Insignificant", "Very Low", "🔴"

def create_score_visualization(scores):
    """Create interactive score visualizations"""
    # Radar chart for section scores
    categories = ['Strategy', 'Financial', 'Risk', 'Feasibility', 'Stakeholder']
    values = [
        scores['strategy'],
        scores['financial'],
        scores['risk'],
        scores['feasibility'],
        scores['stakeholder']
    ]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Project Score',
        line_color='#1f77b4'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=False,
        title="Score Distribution by Section"
    )
    
    # Bar chart for weighted contributions
    weighted_values = [
        scores['strategy'] * SECTION_WEIGHTS['strategy'],
        scores['financial'] * SECTION_WEIGHTS['financial'],
        scores['risk'] * SECTION_WEIGHTS['risk'],
        scores['feasibility'] * SECTION_WEIGHTS['feasibility'],
        scores['stakeholder'] * SECTION_WEIGHTS['stakeholder']
    ]
    
    fig_bar = go.Figure(data=[
        go.Bar(
            x=categories,
            y=weighted_values,
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            text=[f"{v:.1f}" for v in weighted_values],
            textposition='outside'
        )
    ])
    
    fig_bar.update_layout(
        title="Weighted Score Contribution (Out of 100)",
        xaxis_title="Section",
        yaxis_title="Weighted Score",
        yaxis_range=[0, 40],
        showlegend=False
    )
    

    # Waterfall chart showing score breakdown
    fig_waterfall = go.Figure(go.Waterfall(
        name="Score Build-up",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=categories + ["Total"],
        y=weighted_values + [scores['total']],
        text=[f"{v:.1f}" for v in weighted_values] + [f"{scores['total']:.1f}"],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig_waterfall.update_layout(
        title="Score Build-up Analysis",
        showlegend=False,
        yaxis_range=[0, 110]
    )

    
    # Gauge chart for total score
    classification, rating, emoji = get_project_classification(scores['total'])
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=scores['total'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Score", 'font': {'size': 24}},
        delta={'reference': 60, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#ffcccc'},
                {'range': [40, 60], 'color': '#fff4cc'},
                {'range': [60, 80], 'color': '#cce5ff'},
                {'range': [80, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig_radar, fig_bar, fig_waterfall, fig_gauge

def generate_justification(scores):
    """Generate AI-like justification for the project classification"""
    classification, rating, _ = get_project_classification(scores['total'])
    
    # Identify strengths and weaknesses
    section_scores = {
        'Strategy': scores['strategy'],
        'Financial': scores['financial'],
        'Risk': scores['risk'],
        'Feasibility': scores['feasibility'],
        'Stakeholder': scores['stakeholder']
    }
    
    sorted_sections = sorted(section_scores.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_sections[0]
    weakest = sorted_sections[-1]
    
    # Generate justification
    if scores['total'] >= 80:
        justification = f"""
### ✅ Project Classification: {classification} (Priority: {rating})

**Overall Assessment:** This project demonstrates exceptional viability across all evaluation dimensions with an outstanding total score of **{scores['total']:.1f}%**.

**Key Strengths:**
- **{strongest[0]}** is the highest-performing area at {strongest[1]:.1f}%, indicating {
    'strong strategic alignment' if strongest[0] == 'Strategy' else
    'excellent financial returns' if strongest[0] == 'Financial' else
    'well-managed risks' if strongest[0] == 'Risk' else
    'high feasibility and implementation readiness' if strongest[0] == 'Feasibility' else
    'significant stakeholder value'
}.
- All sections scored above 60%, showing balanced excellence across dimensions.
- The project exceeds the feasibility threshold significantly.

**Areas for Attention:**
- While still strong, **{weakest[0]}** at {weakest[1]:.1f}% could benefit from additional focus.

**Recommendation:** **APPROVED** - This is a critical priority project that should be fast-tracked for implementation. The strong scores across all dimensions indicate high probability of success and significant value creation.
        """
    elif scores['total'] >= 60:
        justification = f"""
### ✅ Project Classification: {classification} (Priority: {rating})

**Overall Assessment:** This project demonstrates solid viability with a total score of **{scores['total']:.1f}%**, meeting the feasibility threshold.

**Key Strengths:**
- **{strongest[0]}** is performing well at {strongest[1]:.1f}%, demonstrating {
    'good strategic fit' if strongest[0] == 'Strategy' else
    'positive financial prospects' if strongest[0] == 'Financial' else
    'acceptable risk levels' if strongest[0] == 'Risk' else
    'reasonable implementation feasibility' if strongest[0] == 'Feasibility' else
    'meaningful stakeholder impact'
}.

**Areas for Improvement:**
- **{weakest[0]}** at {weakest[1]:.1f}% requires attention and mitigation strategies.
- {len([s for s in section_scores.values() if s < 70])} section(s) scored below 70%, indicating opportunities for enhancement.

**Recommendation:** **APPROVED with CONDITIONS** - Proceed with implementation while developing specific action plans to address weaker areas, particularly {weakest[0]}. Regular monitoring and progress reviews are recommended.
        """
    elif scores['total'] >= 40:
        justification = f"""
### ⚠️ Project Classification: {classification} (Priority: {rating})

**Overall Assessment:** This project shows potential but falls short of the feasibility threshold with a total score of **{scores['total']:.1f}%**.

**Areas of Concern:**
- **{weakest[0]}** is significantly weak at {weakest[1]:.1f}%, representing a major risk factor.
- Only {len([s for s in section_scores.values() if s >= 60])} section(s) meet the minimum 60% threshold.
- Overall score falls in the "Optional" category, indicating substantial uncertainties.

**Positive Aspects:**
- **{strongest[0]}** shows promise at {strongest[1]:.1f}%.

**Recommendation:** **CONDITIONAL APPROVAL REQUIRED** - This project requires significant improvements before full approval. Recommend:
1. Develop comprehensive mitigation plans for {weakest[0]}
2. Conduct detailed risk assessment and develop contingency plans
3. Re-evaluate after implementing improvements
4. Consider phased or pilot approach to minimize risk
        """
    else:
        justification = f"""
### ❌ Project Classification: {classification} (Priority: {rating})

**Overall Assessment:** This project is currently **NOT FEASIBLE** with a total score of **{scores['total']:.1f}%**, significantly below the required threshold.

**Critical Issues:**
- **{weakest[0]}** is critically low at {weakest[1]:.1f}%, indicating fundamental challenges.
- Only {len([s for s in section_scores.values() if s >= 60])} section(s) meet minimum standards.
- Multiple dimensions show scores below acceptable levels.

**Salvageable Elements:**
- **{strongest[0]}** at {strongest[1]:.1f}% shows some potential.

**Recommendation:** **NOT APPROVED** - This project should not proceed in its current form. Options to consider:
1. **Major Redesign:** Fundamentally restructure the project to address critical weaknesses
2. **Defer:** Postpone until conditions improve and requirements can be better met
3. **Cancel:** If core issues cannot be resolved, consider alternative approaches
4. **Pilot Study:** If there's strategic importance, consider a small-scale pilot to validate assumptions

A comprehensive review and substantial changes are required before reconsideration.
        """
    
    return justification

def generate_pdf_report(project_name, responses, scores):
    """Generate comprehensive PDF report without images - text and tables only"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, 
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#2c3e50'),
        spaceBefore=12,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#34495e'),
        spaceBefore=8,
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )
    
    # Title Page
    elements.append(Paragraph("VALUE IMPACT ASSESSMENT (VIA) REPORT", title_style))
    elements.append(Spacer(1, 0.26*inch))
    
    # Project Information Box
    info_data = [
        ['Project Name:', project_name],
        ['Assessment Date:', datetime.now().strftime('%B %d, %Y at %H:%M')],
        ['Generated By:', 'VIA System v2.0']
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f8ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1f77b4')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Executive Summary
    classification, rating, emoji = get_project_classification(scores['total'])
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    # Determine priority information based on score
    if scores['total'] >= 80:
        priority_label = "MUST HAVE"
        priority_subtitle = "Critical Priority Project"
        priority_desc = "Exceptional value - Fast-track for immediate implementation"
    elif scores['total'] >= 60:
        priority_label = "SHOULD HAVE"
        priority_subtitle = "High Value Project"
        priority_desc = "Strong business case - Proceed with implementation"
    elif scores['total'] >= 40:
        priority_label = "NICE TO HAVE"
        priority_subtitle = "Discretionary Project"
        priority_desc = "Moderate value - Consider when resources available"
    else:
        priority_label = "RECONSIDER"
        priority_subtitle = "Low Priority Project"
        priority_desc = "Limited value - Requires major improvements or deferral"
    
    summary_data = [
        ['Assessment Metric', 'Result'],
        ['Overall Weighted Score', f"{scores['total']:.2f}%"],
        ['Project Classification', classification],
        ['Priority Level', priority_label],
        ['Priority Category', priority_subtitle],
        ['Recommendation Status', priority_desc]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Justification
    justification_text = generate_justification(scores)
    # Extract just the recommendation part without markdown headers
    justification_lines = justification_text.split('\n')
    clean_justification = []
    for line in justification_lines:
        if line.startswith('###') or line.startswith('**Overall Assessment:**'):
            continue
        if line.strip() and not line.startswith('#'):
            clean_line = line.replace('**', '').replace('*', '')
            clean_justification.append(clean_line)
    
    elements.append(Paragraph("<b>Assessment Justification:</b>", subheading_style))
    for line in clean_justification[:15]:  # Limit to key points
        if line.strip():
            stripped_line = line.strip()
            # Check if line already has a prefix (-, digit., or other formatting)
            has_prefix = (
                stripped_line.startswith('-') or 
                (len(stripped_line) > 1 and stripped_line[0].isdigit() and stripped_line[1] in ['.', ' '])
            )
            
            if has_prefix:
                # Don't add bullet - line already has its own formatting
                elements.append(Paragraph(stripped_line, styles['Normal']))
            else:
                # Add bullet for section headers and regular lines
                elements.append(Paragraph(f"• {stripped_line}", styles['Normal']))
    
    elements.append(PageBreak())
    
    # Detailed Section Scores
    elements.append(Paragraph("SECTION PERFORMANCE ANALYSIS", heading_style))
    
    score_data = [
        ['Section', 'Raw Score', 'Weight', 'Contribution', 'Status'],
        ['Strategy Evaluation', f"{scores['strategy']:.2f}%", '10%', f"{scores['strategy'] * 0.10:.2f}", 
         '✓' if scores['strategy'] >= 60 else '✗'],
        ['Financial Evaluation', f"{scores['financial']:.2f}%", '30%', f"{scores['financial'] * 0.30:.2f}",
         '✓' if scores['financial'] >= 60 else '✗'],
        ['Risk Evaluation', f"{scores['risk']:.2f}%", '25%', f"{scores['risk'] * 0.25:.2f}",
         '✓' if scores['risk'] >= 60 else '✗'],
        ['Project Feasibility', f"{scores['feasibility']:.2f}%", '30%', f"{scores['feasibility'] * 0.30:.2f}",
         '✓' if scores['feasibility'] >= 60 else '✗'],
        ['Stakeholder Impact', f"{scores['stakeholder']:.2f}%", '5%', f"{scores['stakeholder'] * 0.05:.2f}",
         '✓' if scores['stakeholder'] >= 60 else '✗'],
        ['', '', 'TOTAL SCORE', f"{scores['total']:.2f}%", '']
    ]
    
    score_table = Table(score_data, colWidths=[2.2*inch, 1.2*inch, 0.9*inch, 1.2*inch, 0.8*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, 5), colors.beige),  # Changed from -2 to 5 to include all data rows
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (3, -1), (3, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.6*inch))
    
    # DETAILED BREAKDOWN SECTION
    elements.append(Paragraph("DETAILED CALCULATION BREAKDOWN", heading_style))
    elements.append(Spacer(1, 0.01*inch))

    # 1. STRATEGY EVALUATION
    elements.append(Paragraph("1. Strategy Evaluation (Weight: 10%)", subheading_style))
    elements.append(Spacer(1, 0.1*inch))
    strategy_questions = ['q3a', 'q3b', 'q4a', 'q4b', 'q4c', 'q5a', 'q5b', 'q5c', 'q6', 'q7a', 'q7b']
    strategy_scores = [responses.get(q, 0) for q in strategy_questions]
    strategy_avg = sum(strategy_scores) / len(strategy_scores) if strategy_scores else 0
    strategy_pct = (strategy_avg / 3) * 100
    
    strategy_data = [
        ['Question Area', 'Score'],
        ['Cash Flow - Cost Savings', f"{responses.get('q3a', 0)}/3"],
        ['Cash Flow - Cost Avoidance', f"{responses.get('q3b', 0)}/3"],
        ['Traditional Business - Market Expansion', f"{responses.get('q4a', 0)}/3"],
        ['Traditional Business - Revenue Generation', f"{responses.get('q4b', 0)}/3"],
        ['Traditional Business - Gross Profit', f"{responses.get('q4c', 0)}/3"],
        ['Non-Traditional Business - Market Expansion', f"{responses.get('q5a', 0)}/3"],
        ['Non-Traditional Business - Revenue', f"{responses.get('q5b', 0)}/3"],
        ['Non-Traditional Business - Gross Profit', f"{responses.get('q5c', 0)}/3"],
        ['Net Zero Carbon Emissions', f"{responses.get('q6', 0)}/3"],
        ['Digital Transformation - Efficiencies', f"{responses.get('q7a', 0)}/3"],
        ['Digital Transformation - Technology', f"{responses.get('q7b', 0)}/3"],
        ['Average Score:', f"{strategy_avg:.2f}/3"],
        ['Section Score:', f"{strategy_pct:.2f}%"],
        ['Weighted Contribution:', f"{strategy_pct * 0.10:.2f}"]
    ]
    
    strategy_table = Table(strategy_data, colWidths=[4.5*inch, 1.5*inch])
    strategy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    elements.append(strategy_table)
    elements.append(PageBreak())
    
    # 2. FINANCIAL EVALUATION
    elements.append(Paragraph("2. Financial Evaluation (Weight: 30%)", subheading_style))
    elements.append(Spacer(1, 0.1*inch))
    fin_weights = {'q8': 0.40, 'q9': 0.30, 'q10': 0.20, 'q11': 0.10}
    fin_score = sum((responses.get(q, 0) / 3) * w for q, w in fin_weights.items())
    fin_pct = fin_score * 100
    
    financial_data = [
        ['Financial Metric', 'Score', 'Weight', 'Contribution'],
        ['Net Present Value (NPV)', f"{responses.get('q8', 0)}/3", '40%', 
         f"{(responses.get('q8', 0)/3)*0.40*100:.2f}%"],
        ['Return on Investment (ROI)', f"{responses.get('q9', 0)}/3", '30%',
         f"{(responses.get('q9', 0)/3)*0.30*100:.2f}%"],
        ['Payback Period', f"{responses.get('q10', 0)}/3", '20%',
         f"{(responses.get('q10', 0)/3)*0.20*100:.2f}%"],
        ['Internal Rate of Return (IRR)', f"{responses.get('q11', 0)}/3", '10%',
         f"{(responses.get('q11', 0)/3)*0.10*100:.2f}%"],
        ['Section Total:', '', '', f"{fin_pct:.2f}%"],
        ['Weighted Contribution:', '', '', f"{fin_pct * 0.30:.2f}"]
    ]
    
    financial_table = Table(financial_data, colWidths=[2.8*inch, 1*inch, 1*inch, 1.2*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(financial_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 3. RISK EVALUATION
    elements.append(Paragraph("3. Risk Evaluation (Weight: 25%)", subheading_style))
    elements.append(Spacer(1, 0.1*inch))
    risk_data = [['Risk Element', 'Prob.', 'Impact', 'Calculation', 'Score']]
    total_risk = 0
    for q in ['q12', 'q13', 'q14', 'q15']:
        prob = responses.get(f'{q}_prob', 1)
        impact = responses.get(f'{q}_impact', 1)
        ind_score = ((prob + impact) / 2) * 0.25
        total_risk += ind_score
        risk_name = {
            'q12': 'Data Quality Issues', 
            'q13': 'Technological Complexity', 
            'q14': 'Timeline Delays', 
            'q15': 'Budget Constraints'
        }[q]
        risk_data.append([risk_name, str(prob), str(impact), f"(({prob}+{impact})/2)×0.25", f"{ind_score:.3f}"])
    
    risk_score_pct = (total_risk / 3) * 100
    risk_data.append(['Total of Individual Risks:', '', '', '', f"{total_risk:.3f}"])
    risk_data.append(['Section Score:', '', '', f"({total_risk:.3f}/3)×100", f"{risk_score_pct:.2f}%"])
    risk_data.append(['Weighted Contribution:', '', '', '', f"{risk_score_pct * 0.25:.2f}"])
    
    risk_table = Table(risk_data, colWidths=[2.2*inch, 0.6*inch, 0.7*inch, 1.5*inch, 1*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -3), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (4, -3), (4, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 4. PROJECT FEASIBILITY
    elements.append(Paragraph("4. Project Feasibility (Weight: 30%)", subheading_style))
    elements.append(Spacer(1, 0.1*inch))
    # Calculate feasibility sub-scores
    tech_weights = {'q16': 0.30, 'q17': 0.20, 'q18': 0.20, 'q19': 0.30}
    tech_score = sum((responses.get(q, 0) / 3) * w for q, w in tech_weights.items()) * 100
    
    op_weights = {'q20': 0.20, 'q21': 0.20, 'q22': 0.20, 'q23': 0.20, 'q24': 0.20}
    op_score = sum((responses.get(q, 0) / 3) * w for q, w in op_weights.items()) * 100
    
    scale_weights = {'q25': 0.30, 'q26': 0.20, 'q27': 0.20, 'q28': 0.15, 'q29': 0.15}
    scale_score = sum((responses.get(q, 0) / 3) * w for q, w in scale_weights.items()) * 100
    
    complex_weights = {'q30': 0.20, 'q31': 0.20, 'q32': 0.20, 'q33': 0.20, 'q34': 0.20}
    complex_score = sum((responses.get(q, 0) / 3) * w for q, w in complex_weights.items()) * 100
    
    feasibility_data = [
        ['Feasibility Dimension', 'Score', 'Sub-Weight', 'Contribution'],
        ['Technical Feasibility', f"{tech_score:.2f}%", '16.67%', f"{tech_score * 0.1667:.2f}%"],
        ['Operational Feasibility', f"{op_score:.2f}%", '16.67%', f"{op_score * 0.1667:.2f}%"],
        ['Scalability & Sustainability', f"{scale_score:.2f}%", '16.67%', f"{scale_score * 0.1667:.2f}%"],
        ['Complexity Management', f"{complex_score:.2f}%", '50.00%', f"{complex_score * 0.50:.2f}%"],
        ['Section Total:', f"{scores['feasibility']:.2f}%", '', ''],
        ['Weighted Contribution:', '', '', f"{scores['feasibility'] * 0.30:.2f}"]
    ]
    
    feasibility_table = Table(feasibility_data, colWidths=[2.5*inch, 1.3*inch, 1.2*inch, 1*inch])
    feasibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(feasibility_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 5. STAKEHOLDER IMPACT
    elements.append(Paragraph("5. Impact on External Stakeholders (Weight: 5%)", subheading_style))
    elements.append(Spacer(1, 0.1*inch))
    stakeholder_data = [
        ['Stakeholder Dimension', 'Score', 'Sub-Weight', 'Contribution'],
        ['Customer Satisfaction', f"{responses.get('q35', 0)}/3", '33.33%', 
         f"{(responses.get('q35', 0)/3)*0.3333*100:.2f}%"],
        ['Supplier/Partner Relations', f"{responses.get('q36', 0)}/3", '33.33%',
         f"{(responses.get('q36', 0)/3)*0.3333*100:.2f}%"],
        ['Brand Reputation', f"{responses.get('q37', 0)}/3", '33.33%',
         f"{(responses.get('q37', 0)/3)*0.3333*100:.2f}%"],
        ['Section Total:', f"{scores['stakeholder']:.2f}%", '', ''],
        ['Weighted Contribution:', '', '', f"{scores['stakeholder'] * 0.05:.2f}"]
    ]
    
    stakeholder_table = Table(stakeholder_data, colWidths=[2.5*inch, 1.3*inch, 1.2*inch, 1*inch])
    stakeholder_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(stakeholder_table)
    
    elements.append(PageBreak())
    
    # FINAL RECOMMENDATION
    elements.append(Paragraph("FINAL RECOMMENDATION", heading_style))
    
    # Determine priority information for final recommendation
    if scores['total'] >= 80:
        priority_label = "MUST HAVE"
        priority_subtitle = "Critical Priority Project"
        priority_desc = "Exceptional value - Fast-track for immediate implementation"
        action_recommendation = "APPROVE IMMEDIATELY - Fast-track for implementation"
    elif scores['total'] >= 60:
        priority_label = "SHOULD HAVE"
        priority_subtitle = "High Value Project"
        priority_desc = "Strong business case - Proceed with implementation"
        action_recommendation = "APPROVE - Proceed with standard implementation timeline"
    elif scores['total'] >= 40:
        priority_label = "NICE TO HAVE"
        priority_subtitle = "Discretionary Project"
        priority_desc = "Moderate value - Consider when resources available"
        action_recommendation = "CONDITIONAL APPROVAL - Implement when resources permit"
    else:
        priority_label = "RECONSIDER"
        priority_subtitle = "Low Priority Project"
        priority_desc = "Limited value - Requires major improvements or deferral"
        action_recommendation = "DEFER/REJECT - Significant improvements needed before approval"
    
    # Determine priority information for final recommendation
    if scores['total'] >= 80:
        priority_label = "MUST HAVE"
        priority_subtitle = "Critical Priority Project"
        priority_desc = "Exceptional value - Fast-track for immediate implementation"
        action_recommendation = "APPROVE IMMEDIATELY - Fast-track for implementation"
    elif scores['total'] >= 60:
        priority_label = "SHOULD HAVE"
        priority_subtitle = "High Value Project"
        priority_desc = "Strong business case - Proceed with implementation"
        action_recommendation = "APPROVE - Proceed with standard implementation timeline"
    elif scores['total'] >= 40:
        priority_label = "NICE TO HAVE"
        priority_subtitle = "Discretionary Project"
        priority_desc = "Moderate value - Consider when resources available"
        action_recommendation = "CONDITIONAL APPROVAL - Implement when resources permit"
    else:
        priority_label = "RECONSIDER"
        priority_subtitle = "Low Priority Project"
        priority_desc = "Limited value - Requires major improvements or deferral"
        action_recommendation = "DEFER/REJECT - Significant improvements needed"
    
    recommendation_data = [
        ['Total Weighted Score:', f"{scores['total']:.2f}%"],
        ['Project Classification:', classification],
        ['Priority Level:', priority_label],
        ['Priority Category:', priority_subtitle],
        ['Assessment Summary:', Paragraph(priority_desc, styles['Normal'])],
        ['Action Recommendation:', Paragraph(action_recommendation, styles['Normal'])]
    ]
    
    recommendation_table = Table(recommendation_data, colWidths=[2.3*inch, 3.7*inch])
    recommendation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f8ff')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1f77b4')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to top for better readability
    ]))
    elements.append(recommendation_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Footer note
    elements.append(Paragraph(
        "<i>This report was generated by the Value Impact Assessment (VIA) System. "
        "For detailed analysis and interactive features, please refer to the web interface.</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
    """Generate comprehensive PDF report with charts and detailed breakdown"""
    import tempfile
    import os
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    # Title Page
    elements.append(Paragraph("Value Impact Assessment (VIA) Report", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Project Information
    info_data = [
        ['Project Name:', project_name],
        ['Assessment Date:', datetime.now().strftime('%Y-%m-%d %H:%M')],
        ['Generated By:', 'VIA System v2.0']
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    classification, rating, emoji = get_project_classification(scores['total'])
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    # Determine priority information based on score
    if scores['total'] >= 80:
        priority_label = "MUST HAVE"
        priority_subtitle = "Critical Priority Project"
        priority_desc = "Exceptional value - Fast-track for immediate implementation"
    elif scores['total'] >= 60:
        priority_label = "SHOULD HAVE"
        priority_subtitle = "High Value Project"
        priority_desc = "Strong business case - Proceed with implementation"
    elif scores['total'] >= 40:
        priority_label = "NICE TO HAVE"
        priority_subtitle = "Discretionary Project"
        priority_desc = "Moderate value - Consider when resources available"
    else:
        priority_label = "RECONSIDER"
        priority_subtitle = "Low Priority Project"
        priority_desc = "Limited value - Requires major improvements or deferral"
    
    summary_data = [
        ['Assessment Metric', 'Result'],
        ['Overall Weighted Score', f"{scores['total']:.2f}%"],
        ['Project Classification', classification],
        ['Priority Level', priority_label],
        ['Priority Category', priority_subtitle],
        ['Recommendation Status', priority_desc]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Detailed Section Scores
    elements.append(Paragraph("Detailed Section Scores", heading_style))
    
    score_data = [
        ['Section', 'Raw Score (%)', 'Weight', 'Weighted Contribution', 'Status'],
        ['Strategy Evaluation', f"{scores['strategy']:.2f}", '10%', f"{scores['strategy'] * 0.10:.2f}", 
         '✓' if scores['strategy'] >= 60 else '✗'],
        ['Financial Evaluation', f"{scores['financial']:.2f}", '30%', f"{scores['financial'] * 0.30:.2f}",
         '✓' if scores['financial'] >= 60 else '✗'],
        ['Risk Evaluation', f"{scores['risk']:.2f}", '25%', f"{scores['risk'] * 0.25:.2f}",
         '✓' if scores['risk'] >= 60 else '✗'],
        ['Project Feasibility', f"{scores['feasibility']:.2f}", '30%', f"{scores['feasibility'] * 0.30:.2f}",
         '✓' if scores['feasibility'] >= 60 else '✗'],
        ['Stakeholder Impact', f"{scores['stakeholder']:.2f}", '5%', f"{scores['stakeholder'] * 0.05:.2f}",
         '✓' if scores['stakeholder'] >= 60 else '✗'],
        ['', '', 'TOTAL:', f"{scores['total']:.2f}%", '']
    ]
    
    score_table = Table(score_data, colWidths=[2*inch, 1.3*inch, 0.8*inch, 1.4*inch, 0.8*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -1), (2, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, -1), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (3, -1), (3, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Try to generate and add charts, but continue if kaleido is not available
    try:
        # Generate and save charts as images
        fig_radar, fig_bar, fig_waterfall, fig_gauge = create_score_visualization(scores)
        
        # Save charts temporarily
        temp_dir = tempfile.gettempdir()
        radar_path = os.path.join(temp_dir, 'radar_chart.png')
        bar_path = os.path.join(temp_dir, 'bar_chart.png')
        waterfall_path = os.path.join(temp_dir, 'waterfall_chart.png')
        gauge_path = os.path.join(temp_dir, 'gauge_chart.png')
        
        fig_radar.write_image(radar_path, width=600, height=500, engine="kaleido")
        fig_bar.write_image(bar_path, width=600, height=500, engine="kaleido")
        fig_waterfall.write_image(waterfall_path, width=600, height=500, engine="kaleido")
        fig_gauge.write_image(gauge_path, width=600, height=400, engine="kaleido")
        
        # Add charts to PDF
        elements.append(Paragraph("Score Visualizations", heading_style))
        
        # Add radar and bar charts side by side
        img_radar = Image(radar_path, width=3*inch, height=2.5*inch)
        img_bar = Image(bar_path, width=3*inch, height=2.5*inch)
        
        chart_table1 = Table([[img_radar, img_bar]], colWidths=[3.2*inch, 3.2*inch])
        elements.append(chart_table1)
        elements.append(Spacer(1, 0.2*inch))
        
        # Add waterfall and gauge charts
        img_waterfall = Image(waterfall_path, width=3*inch, height=2.5*inch)
        img_gauge = Image(gauge_path, width=3*inch, height=2*inch)
        
        chart_table2 = Table([[img_waterfall, img_gauge]], colWidths=[3.2*inch, 3.2*inch])
        elements.append(chart_table2)
        
        # Cleanup temp files
        try:
            os.remove(radar_path)
            os.remove(bar_path)
            os.remove(waterfall_path)
            os.remove(gauge_path)
        except:
            pass
            
    except Exception as e:
        # If chart generation fails, add a note and continue with text-based report
        elements.append(Paragraph("Score Visualizations", heading_style))
        elements.append(Paragraph(
            "<i>Note: Visual charts are available in the web interface. "
            "To include charts in PDF, please install kaleido: pip install kaleido</i>",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        # Add text-based visualization as fallback
        viz_data = [
            ['Section', 'Score', 'Visual'],
            ['Strategy', f"{scores['strategy']:.1f}%", '█' * int(scores['strategy']/10)],
            ['Financial', f"{scores['financial']:.1f}%", '█' * int(scores['financial']/10)],
            ['Risk', f"{scores['risk']:.1f}%", '█' * int(scores['risk']/10)],
            ['Feasibility', f"{scores['feasibility']:.1f}%", '█' * int(scores['feasibility']/10)],
            ['Stakeholder', f"{scores['stakeholder']:.1f}%", '█' * int(scores['stakeholder']/10)],
        ]
        
        viz_table = Table(viz_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        viz_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(viz_table)
    
    elements.append(PageBreak())
    
    # Detailed Calculation Breakdown
    elements.append(Paragraph("Detailed Calculation Breakdown", heading_style))
    
    # Strategy breakdown
    elements.append(Paragraph("<b>1. Strategy Evaluation (10%)</b>", styles['Normal']))
    strategy_questions = ['q3a', 'q3b', 'q4a', 'q4b', 'q4c', 'q5a', 'q5b', 'q5c', 'q6', 'q7a', 'q7b']
    strategy_scores = [responses.get(q, 0) for q in strategy_questions]
    strategy_avg = sum(strategy_scores) / len(strategy_scores) if strategy_scores else 0
    strategy_pct = (strategy_avg / 3) * 100
    
    strategy_data = [
        ['Question', 'Your Answer', 'Score'],
        ['Cash Flow - Cost Savings', str(responses.get('q3a', 'N/A')), f"{responses.get('q3a', 0)}/3"],
        ['Cash Flow - Cost Avoidance', str(responses.get('q3b', 'N/A')), f"{responses.get('q3b', 0)}/3"],
        ['Traditional - Market Expansion', str(responses.get('q4a', 'N/A')), f"{responses.get('q4a', 0)}/3"],
        ['Traditional - Revenue Generation', str(responses.get('q4b', 'N/A')), f"{responses.get('q4b', 0)}/3"],
        ['Traditional - Gross Profit', str(responses.get('q4c', 'N/A')), f"{responses.get('q4c', 0)}/3"],
        ['Non-Traditional - Market Expansion', str(responses.get('q5a', 'N/A')), f"{responses.get('q5a', 0)}/3"],
        ['Non-Traditional - Revenue', str(responses.get('q5b', 'N/A')), f"{responses.get('q5b', 0)}/3"],
        ['Non-Traditional - Gross Profit', str(responses.get('q5c', 'N/A')), f"{responses.get('q5c', 0)}/3"],
        ['Net Zero Carbon Emissions', str(responses.get('q6', 'N/A')), f"{responses.get('q6', 0)}/3"],
        ['Digital - Efficiencies', str(responses.get('q7a', 'N/A')), f"{responses.get('q7a', 0)}/3"],
        ['Digital - Technology', str(responses.get('q7b', 'N/A')), f"{responses.get('q7b', 0)}/3"],
        ['', 'Average Score:', f"{strategy_avg:.2f}/3"],
        ['', 'Section Score:', f"{strategy_pct:.2f}%"],
        ['', 'Weighted (10%):', f"{strategy_pct * 0.10:.2f}"]
    ]
    
    strategy_table = Table(strategy_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
    strategy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (1, -3), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(strategy_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Financial breakdown
    elements.append(Paragraph("<b>2. Financial Evaluation (30%)</b>", styles['Normal']))
    fin_weights = {'q8': 0.40, 'q9': 0.30, 'q10': 0.20, 'q11': 0.10}
    fin_score = sum((responses.get(q, 0) / 3) * w for q, w in fin_weights.items())
    fin_pct = fin_score * 100
    
    financial_data = [
        ['Metric', 'Your Answer', 'Score', 'Weight', 'Contribution'],
        ['Net Present Value (NPV)', str(responses.get('q8', 'N/A')), f"{responses.get('q8', 0)}/3", '40%', 
         f"{(responses.get('q8', 0)/3)*0.40*100:.2f}"],
        ['Return on Investment (ROI)', str(responses.get('q9', 'N/A')), f"{responses.get('q9', 0)}/3", '30%',
         f"{(responses.get('q9', 0)/3)*0.30*100:.2f}"],
        ['Payback Period', str(responses.get('q10', 'N/A')), f"{responses.get('q10', 0)}/3", '20%',
         f"{(responses.get('q10', 0)/3)*0.20*100:.2f}"],
        ['Internal Rate of Return (IRR)', str(responses.get('q11', 'N/A')), f"{responses.get('q11', 0)}/3", '10%',
         f"{(responses.get('q11', 0)/3)*0.10*100:.2f}"],
        ['', '', '', 'Total:', f"{fin_pct:.2f}%"],
        ['', '', '', 'Weighted (30%):', f"{fin_pct * 0.30:.2f}"]
    ]
    
    financial_table = Table(financial_data, colWidths=[2*inch, 1.2*inch, 0.9*inch, 0.9*inch, 1*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (3, -2), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(financial_table)
    
    elements.append(PageBreak())
    
    # Risk breakdown
    elements.append(Paragraph("<b>3. Risk Evaluation (25%)</b>", styles['Normal']))
    elements.append(Paragraph("<i>Formula: Individual Risk = ((Probability + Impact) / 2) × 0.25</i>", styles['Normal']))
    
    risk_data = [['Risk Element', 'Probability', 'Impact', 'Individual Score', 'Formula']]
    total_risk = 0
    for q in ['q12', 'q13', 'q14', 'q15']:
        prob = responses.get(f'{q}_prob', 1)
        impact = responses.get(f'{q}_impact', 1)
        ind_score = ((prob + impact) / 2) * 0.25
        total_risk += ind_score
        risk_name = {'q12': 'Data Quality', 'q13': 'Tech Complexity', 'q14': 'Timeline Delays', 'q15': 'Budget Constraints'}[q]
        risk_data.append([risk_name, str(prob), str(impact), f"{ind_score:.3f}", f"(({prob}+{impact})/2)×0.25"])
    
    risk_score_pct = (total_risk / 3) * 100
    risk_data.append(['', '', 'Total:', f"{total_risk:.3f}", f"Sum of individual scores"])
    risk_data.append(['', '', 'Score (%):', f"{risk_score_pct:.2f}%", f"({total_risk:.3f}/3)×100"])
    risk_data.append(['', '', 'Weighted (25%):', f"{risk_score_pct * 0.25:.2f}", ''])
    
    risk_table = Table(risk_data, colWidths=[1.8*inch, 0.9*inch, 0.9*inch, 1.2*inch, 2.2*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (2, -3), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Note about completeness
    elements.append(Paragraph("<i>Note: Feasibility and Stakeholder sections follow similar detailed breakdowns. Please refer to the system for complete question-by-question analysis.</i>", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Main App UI
def main():
    # Header with logo placeholder
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<h1 class="main-header">📊 Value Impact Assessment (VIA) System</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://vfsysrkgiakqfyzgxaof.supabase.co/storage/v1/object/sign/project-documents/cropped1.1.png?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8xOGYxMzlhYS0xZTYxLTQzYjItODA0Ni1lYTE5OTgwNGU0MTEiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJwcm9qZWN0LWRvY3VtZW50cy9jcm9wcGVkMS4xLnBuZyIsImlhdCI6MTc2OTY2MDE4MCwiZXhwIjoxODAxMTk2MTgwfQ.CBnXlkd6viFy6Wt9W8SKM_i5TVjSUMGr4a4P2ir9owA")
        st.markdown("---")
        
        sections = [
            "🏠 Project Setup",
            "🎯 Strategy Evaluation",
            "💰 Financial Evaluation",
            "⚠️ Risk Evaluation",
            "🔧 Project Feasibility",
            "👥 Stakeholder Impact",
            "📎 Document Upload",
            "📊 Results & Report"
        ]
        
        selected = st.radio("**Navigation** ~", sections, index=st.session_state.current_section)
        st.session_state.current_section = sections.index(selected)
        
        st.markdown("---")
        if st.session_state.project_id:
            st.success(f"✅ Project ID: {st.session_state.project_id}")
        
        # Progress indicator
        progress = (st.session_state.current_section / (len(sections) - 1)) * 100
        st.progress(progress / 100)
        st.caption(f"Progress: {progress:.0f}%")
    
    # Section 0: Project Setup
    if st.session_state.current_section == 0:
        st.markdown('<h2 class="section-header">🏠 Project Setup</h2>', unsafe_allow_html=True)
        
        project_name = st.text_input(
            "Project Name",
            help="Enter the name of your project. This will appear throughout the assessment and in all reports."
        )
        
        if st.button("Start Assessment", type="primary"):
            if project_name:
                project_id = save_project_to_db(project_name)
                if project_id:
                    st.session_state.project_id = project_id
                    st.session_state.responses['project_name'] = project_name
                    st.success(f"✅ Project '{project_name}' created successfully!")
                    st.session_state.current_section = 1
                    st.rerun()
            else:
                st.error("Please enter a project name.")
    
    # Section 1: Strategy Evaluation
    elif st.session_state.current_section == 1:
        st.markdown('<h2 class="section-header">🎯 Strategy Evaluation</h2>', unsafe_allow_html=True)
        
        # Strategic Focus Selection
        st.subheader("Strategic Focus Area")
        focus = st.radio(
            "Select your Strategic Focus Area",
            ["Long Term Goals (3-5+ years)", "Key Priorities (0-2 years)"],
            help="Choose whether your project primarily addresses long-term organizational vision or immediate strategic priorities."
        )
        st.session_state.responses['strategic_focus'] = focus
        
        st.markdown("---")
        
        # Cash Flow
        st.subheader("💵 Improved Cash Flow")
        
        col1, col2 = st.columns(2)
        with col1:
            q3a = st.selectbox(
                "Cost Savings Impact",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low Relevance (<3%)", "Moderate Relevance (3-9%)", "High Relevance (≥10%)"][x],
                help="Evaluate cost reduction through efficiency improvements, elimination of redundancies, or optimization of existing expenses."
            )
            st.session_state.responses['q3a'] = q3a
        
        with col2:
            q3b = st.selectbox(
                "Cost Avoidance Impact",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low Relevance (<3%)", "Moderate Relevance (3-9%)", "High Relevance (≥10%)"][x],
                help="Evaluate prevention of future costs such as maintenance, penalties, contract leakage, or other cost exposure mitigation."
            )
            st.session_state.responses['q3b'] = q3b
        
        st.markdown("---")
        
        # Traditional Business Growth
        st.subheader("📈 Growth in Traditional Business")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            q4a = st.selectbox(
                "Market Expansion",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                help="Evaluate the project's ability to enter new markets, expand market share, or reach new customer segments."
            )
            st.session_state.responses['q4a'] = q4a
        
        with col2:
            q4b = st.selectbox(
                "Revenue Generation",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                help="Evaluate the project's ability to generate new revenue or increase existing revenue streams."
            )
            st.session_state.responses['q4b'] = q4b
        
        with col3:
            q4c = st.selectbox(
                "Gross Profit Generation",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                help="Evaluate the project's ability to improve gross profit margin or increase gross profit contribution."
            )
            st.session_state.responses['q4c'] = q4c
        
        st.markdown("---")
        
        # Non-Traditional Business Growth
        st.subheader("🚀 Growth in Non-Traditional Business")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            q5a = st.selectbox(
                "Market Expansion",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                help="Evaluate the project's ability to enter new non-traditional markets, expand market share in emerging sectors, or reach new customer segments outside core business.",
                key="q5a"
            )
            st.session_state.responses['q5a'] = q5a
        
        with col2:
            q5b = st.selectbox(
                "Revenue Generation",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                help="Evaluate the project's ability to generate new revenue or increase existing revenue streams in non-traditional business areas.",
                key="q5b"
            )
            st.session_state.responses['q5b'] = q5b
        
        with col3:
            q5c = st.selectbox(
                "Gross Profit Generation",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                help="Evaluate the project's ability to improve gross profit margin or increase gross profit contribution in non-traditional business ventures.",
                key="q5c"
            )
            st.session_state.responses['q5c'] = q5c
        
        st.markdown("---")
        
        # Net Zero Carbon
        st.subheader("🌱 Net Zero Carbon Emissions")
        q6 = st.selectbox(
            "Carbon Emissions Impact",
            options=[0, 1, 2, 3],
            format_func=lambda x: ["Not Relevant ", "Low (<5%)", "Moderate (5-19%)", "High (≥20%)"][x],
            help="Evaluate the project's impact on reducing carbon emissions through process changes, technology adoption, or verified decarbonization programs."
        )
        st.session_state.responses['q6'] = q6
        
        st.markdown("---")
        
        # Digital Transformation
        st.subheader("💻 Digital Transformation")
        
        col1, col2 = st.columns(2)
        with col1:
            q7a = st.selectbox(
                "Efficiencies Improvement",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<5%)", "Moderate (5-14%)", "High (≥15%)"][x],
                help="Assess improvements in process efficiency, resource utilization, and cycle time reduction."
            )
            st.session_state.responses['q7a'] = q7a
        
        with col2:
            q7b = st.selectbox(
                "Technology Improvement",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (Minor)", "Moderate (5-19%)", "High (≥20%)"][x],
                help="Evaluate the technological advancement and digital transformation impact of the project."
            )
            st.session_state.responses['q7b'] = q7b

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Next: Financial Evaluation →", type="primary"):
            st.session_state.current_section = 2
            st.rerun()
    
    # Section 2: Financial Evaluation
    elif st.session_state.current_section == 2:
        st.markdown('<h2 class="section-header">💰 Financial Evaluation</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            q8 = st.selectbox(
                "Net Present Value (NPV)",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Applicable/Negative (≤0)", "Low (0-39%)", "Moderate (40-99%)", "High (≥100%)"][x],
                help="NPV represents the difference between the present value of cash inflows and outflows over the project's lifetime."
            )
            st.session_state.responses['q8'] = q8
            
            q10 = st.selectbox(
                "Payback Period",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Applicable (>10 years)", "Low (5-10 years)", "Moderate (2-5 years)", "High (≤1 year)"][x],
                help="Time required to recover the initial investment from the project's cash flows."
            )
            st.session_state.responses['q10'] = q10
        
        with col2:
            q9 = st.selectbox(
                "Return on Investment (ROI)",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Negative (<10%)", "Low (10-39%)", "Moderate (40-99%)", "High (≥100%)"][x],
                help="ROI measures the efficiency of the investment by comparing the gain from the investment to its cost."
            )
            st.session_state.responses['q9'] = q9
            
            q11 = st.selectbox(
                "Internal Rate of Return (IRR)",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Below Hurdle (<10%)", "Low (10-39%)", "Moderate (40-99%)", "High (≥100%)"][x],
                help="IRR is the discount rate that makes the NPV of all cash flows equal to zero."
            )
            st.session_state.responses['q11'] = q11

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", type="secondary"):
                st.session_state.current_section = 1
                st.rerun()
        with col2:
            if st.button("Next: Risk Evaluation →", type="primary"):
                st.session_state.current_section = 3
                st.rerun()
    
    # Section 3: Risk Evaluation
    elif st.session_state.current_section == 3:
        st.markdown('<h2 class="section-header">⚠️ Risk Evaluation</h2>', unsafe_allow_html=True)
        st.info("💡 For each risk element, assess both **Probability** (how likely it is to occur) and **Impact** (severity if it occurs). **Lower scores indicate Higher risk**.")
        
        # Risk 1: Data Quality Issues
        with st.expander("📋 Risk 1: Data Quality Issues", expanded=True):
            st.markdown("**Evaluate data accuracy, completeness, and consistency risks**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Probability (Likelihood)**")
                q12_prob = st.radio(
                    "How likely are data quality issues?",
                    options=[1, 2, 3],
                    format_func=lambda x: {
                        1: "1 - Very Likely (>20% data issues)",
                        2: "2 - Possible (5-20% data issues)", 
                        3: "3 - Not Likely (<5% data issues)"
                    }[x],
                    key="q12_prob_select",
                    help="Frequent issues (>20% missing/inaccurate) = Very Likely | Occasional issues (5-20%) = Possible | Minimal issues (<5%) = Not Likely"
                )
                st.session_state.responses['q12_prob'] = q12_prob
            
            with col2:
                st.markdown("**Impact (Severity)**")
                q12_impact = st.radio(
                    "If data issues occur, what's the impact?",
                    options=[1, 2, 3],
                    format_func=lambda x: {
                        1: "1 - Very High (Invalid analytics/results)",
                        2: "2 - Moderate (Some rework needed)",
                        3: "3 - Very Low (Minor, easily corrected)"
                    }[x],
                    key="q12_impact_select",
                    help="Severe business impact (invalid results) = Very High | Limited effect (some rework) = Moderate | Minor errors (no major impact) = Very Low"
                )
                st.session_state.responses['q12_impact'] = q12_impact
        
        # Risk 2: Technological Complexity
        with st.expander("📋 Risk 2: Technological Complexity", expanded=True):
            st.markdown("**Evaluate technology implementation and integration risks**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Probability (Likelihood)**")
                q13_prob = st.radio(
                    "How likely is technology failure/complexity?",
                    options=[1, 2, 3],
                    format_func=lambda x: {
                        1: "1 - Very Likely (New/untested tech)",
                        2: "2 - Possible (Minor customization needed)",
                        3: "3 - Not Likely (Proven, stable tech)"
                    }[x],
                    key="q13_prob_select",
                    help="New/untested technology = Very Likely | Moderate risk (partial integration) = Possible | Proven technology = Not Likely"
                )
                st.session_state.responses['q13_prob'] = q13_prob
            
            with col2:
                st.markdown("**Impact (Severity)**")
                q13_impact = st.radio(
                    "If tech issues occur, what's the impact?",
                    options=[1, 2, 3],
                    format_func=lambda x: {
                        1: "1 - Very High (Could cause project failure)",
                        2: "2 - Moderate (Localized, recoverable)",
                        3: "3 - Very Low (Minimal, manageable)"
                    }[x],
                    key="q13_impact_select",
                    help="Critical system impact (project failure) = Very High | Localized disruptions = Moderate | Minimal impact = Very Low"
                )
                st.session_state.responses['q13_impact'] = q13_impact
        
        # Risk 3: Timeline Delays
        with st.expander("📋 Risk 3: Timeline Delays", expanded=True):
            st.markdown("**Evaluate schedule and milestone achievement risks**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Probability (Likelihood)**")
                q14_prob = st.radio(
                    "How likely are timeline delays?",
                    options=[1, 2, 3],
                    format_func=lambda x: {
                        1: "1 - Very Likely (>30% delay chance)",
                        2: "2 - Possible (10-30% delay chance)",
                        3: "3 - Not Likely (<10% delay chance)"
                    }[x],
                    key="q14_prob_select",
                    help="Unclear milestones/resources (>30% chance) = Very Likely | Some dependencies (10-30%) = Possible | Well-defined timeline (<10%) = Not Likely"
                )
                st.session_state.responses['q14_prob'] = q14_prob
            
            with col2:
                st.markdown("**Impact (Severity)**")
                q14_impact = st.radio(
                    "If delays occur, what's the impact?",
                    options=[1, 2, 3],
                    format_func=lambda x: {
                        1: "1 - Very High (Critical to success)",
                        2: "2 - Moderate (Manageable slippage)",
                        3: "3 - Very Low (Negligible effect)"
                    }[x],
                    key="q14_impact_select",
                    help="Critically affects project success = Very High | Partial milestone slippage = Moderate | Minimal delay impact = Very Low"
                )
                st.session_state.responses['q14_impact'] = q14_impact
        
        # Risk 4: Budget Constraints
        with st.expander("📋 Risk 4: Budget Constraints", expanded=True):
            st.markdown("**Evaluate financial and cost overrun risks**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Probability (Likelihood)**")
                q15_prob = st.radio(
                    "How likely are budget overruns?",
                    options=[1, 2, 3],
                    format_func=lambda x: {
                        1: "1 - Very Likely (>10% overrun chance)",
                        2: "2 - Possible (5-10% overrun chance)",
                        3: "3 - Not Likely (<5% overrun chance)"
                    }[x],
                    key="q15_prob_select",
                    help="Funding not secured (>10% chance) = Very Likely | Moderate uncertainty (5-10%) = Possible | Budget approved (<5%) = Not Likely"
                )
                st.session_state.responses['q15_prob'] = q15_prob
            
            with col2:
                st.markdown("**Impact (Severity)**")
                q15_impact = st.radio(
                    "If budget issues occur, what's the impact?",
                    options=[1, 2, 3],
                    format_func=lambda x: {
                        1: "1 - Very High (>10% overrun, project halt)",
                        2: "2 - Moderate (Manageable via reallocation)",
                        3: "3 - Very Low (Full funding secured)"
                    }[x],
                    key="q15_impact_select",
                    help="Funding gap leads to halt = Very High | Minor overspend (manageable) = Moderate | Full funding in place = Very Low"
                )
                st.session_state.responses['q15_impact'] = q15_impact
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", type="secondary"):
                st.session_state.current_section = 2
                st.rerun()
        with col2:
            if st.button("Next: Project Feasibility →", type="primary"):
                st.session_state.current_section = 4
                st.rerun()
    
    # Section 4: Project Feasibility
    elif st.session_state.current_section == 4:
        st.markdown('<h2 class="section-header">🔧 Project Feasibility</h2>', unsafe_allow_html=True)
        
        # Track completion status
        if 'feasibility_tab' not in st.session_state:
            st.session_state.feasibility_tab = 0
        
        # Create navigation hints
        tabs_completed = {
            'technical': all(f'q{i}' in st.session_state.responses for i in range(16, 20)),
            'operational': all(f'q{i}' in st.session_state.responses for i in range(20, 25)),
            'scalability': all(f'q{i}' in st.session_state.responses for i in range(25, 30)),
            'complexity': all(f'q{i}' in st.session_state.responses for i in range(30, 35))
        }
        
        completion_status = f"✅ Technical | ✅ Operational | ✅ Scalability | ✅ Complexity" if all(tabs_completed.values()) else \
            f"{'✅' if tabs_completed['technical'] else '⬜'} Technical | " \
            f"{'✅' if tabs_completed['operational'] else '⬜'} Operational | " \
            f"{'✅' if tabs_completed['scalability'] else '⬜'} Scalability | " \
            f"{'✅' if tabs_completed['complexity'] else '⬜'} Complexity"
        
        st.info(f"📋 **Complete all 4 sub-sections:**")
        
        # Progress indicator
        st.markdown("""
        <style>
        .progress-bar-container {
            display: flex;
            gap: 5px;
            margin: 15px 0 20px 0;
        }
        .progress-segment {
            flex: 1;
            height: 8.5px;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .progress-incomplete {
            background: #e0e0e0;
        }
        .progress-active {
            background: linear-gradient(90deg, #a1fb17 0%, #26e215 100%);
            box-shadow: 0 2px 6px rgba(60, 221, 160, 0.4);
        }
        .progress-completed {
            background: linear-gradient(90deg, #05e1ce 0%, #00b8aa 100%);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Visual progress bar
        progress_html = '<div class="progress-bar-container">'
        for key in ['technical', 'operational', 'scalability', 'complexity']:
            idx = ['technical', 'operational', 'scalability', 'complexity'].index(key)
            is_completed = tabs_completed[key]
            is_active = st.session_state.feasibility_tab == idx
            
            if is_active:
                progress_html += '<div class="progress-segment progress-active" title="Current section"></div>'
            elif is_completed:
                progress_html += '<div class="progress-segment progress-completed" title="Completed"></div>'
            else:
                progress_html += '<div class="progress-segment progress-incomplete" title="Pending"></div>'
        
        progress_html += '</div>'
        st.markdown(progress_html, unsafe_allow_html=True)
        
        # Tab selection buttons with primary type (mint green)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button(f"{'✅' if tabs_completed['technical'] else '1.'} Technical", use_container_width=True, type="primary"):
                st.session_state.feasibility_tab = 0
        with col2:
            if st.button(f"{'✅' if tabs_completed['operational'] else '2.'} Operational", use_container_width=True, type="primary"):
                st.session_state.feasibility_tab = 1
        with col3:
            if st.button(f"{'✅' if tabs_completed['scalability'] else '3.'} Scalability", use_container_width=True, type="primary"):
                st.session_state.feasibility_tab = 2
        with col4:
            if st.button(f"{'✅' if tabs_completed['complexity'] else '4.'} Complexity", use_container_width=True, type="primary"):
                st.session_state.feasibility_tab = 3
        
        st.markdown("---")

        # Technical Feasibility
        if st.session_state.feasibility_tab == 0:
            st.subheader("⚙️ Technical Feasibility (4 Questions)")
            
            q16 = st.selectbox(
                "1. Technology Availability",
                options=[None, 1, 2, 3],
                format_func=lambda x: "Select an option" if x is None else ["Very Low", "Moderate", "Very High"][x-1],
                help="Are the required technologies readily available?",
                key="q16"
            )
            if q16 is not None:
                st.session_state.responses['q16'] = q16
            
            q17 = st.selectbox(
                "2. Technical Expertise",
                options=[None, 1, 2, 3],
                format_func=lambda x: "Select an option" if x is None else ["Very Low", "Moderate", "Very High"][x-1],
                help="Does the team have the required skills and experience?",
                key="q17"
            )
            if q17 is not None:
                st.session_state.responses['q17'] = q17
            
            q18 = st.selectbox(
                "3. Infrastructure Needs",
                options=[None, 1, 2, 3],
                format_func=lambda x: "Select an option" if x is None else ["Very Low", "Moderate", "Very High"][x-1],
                help="Is the required hardware and software infrastructure available?",
                key="q18"
            )
            if q18 is not None:
                st.session_state.responses['q18'] = q18
            
            q19 = st.selectbox(
                "4. Integration Complexity",
                options=[None, 1, 2, 3],
                format_func=lambda x: "Select an option" if x is None else ["Very Low", "Moderate", "Very High"][x-1],
                help="How easy is it to integrate with current systems?",
                key="q19"
            )
            if q19 is not None:
                st.session_state.responses['q19'] = q19
            
            if st.button("Next: Operational Feasibility →", type="primary"):
                st.session_state.feasibility_tab = 1
                st.rerun()
        
        # Operational Feasibility
        elif st.session_state.feasibility_tab == 1:
            st.subheader("🏭 Operational Feasibility (5 Questions)")
            
            questions = [
                ("1. Process Compatibility", "q20", "How well does the project align with existing workflows?"),
                ("2. Resource Availability", "q21", "Are personnel, equipment, and materials available?"),
                ("3. User Acceptance", "q22", "What is the likelihood of user adoption?"),
                ("4. Training Requirements", "q23", "What level of training is needed?"),
                ("5. Supportability", "q24", "How easy is it to maintain and support long-term?")
            ]
            
            for label, q_id, help_text in questions:
                response = st.selectbox(
                    label,
                    options=[None, 1, 2, 3],
                    format_func=lambda x: "Select an option" if x is None else ["Very Low", "Moderate", "Very High"][x-1],
                    help=help_text,
                    key=q_id
                )
                if response is not None:
                    st.session_state.responses[q_id] = response
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back: Technical", type="secondary"):
                    st.session_state.feasibility_tab = 0
                    st.rerun()
            with col2:
                if st.button("Next: Scalability →", type="primary"):
                    st.session_state.feasibility_tab = 2
                    st.rerun()
        
        # Scalability & Sustainability
        elif st.session_state.feasibility_tab == 2:
            st.subheader("📊 Scalability & Sustainability (5 Questions)")
            
            questions = [
                ("1. System Performance", "q25", "Can the system handle increased data and user load?"),
                ("2. Expansion Flexibility", "q26", "How easy is it to add/remove features or users?"),
                ("3. Resource Efficiency", "q27", "How efficiently does the system use resources?"),
                ("4. Long-Term Costs", "q28", "What are the anticipated maintenance and operational costs?"),
                ("5. Environmental Impact", "q29", "What is the environmental sustainability of the project?")
            ]
            
            for label, q_id, help_text in questions:
                response = st.selectbox(
                    label,
                    options=[None, 1, 2, 3],
                    format_func=lambda x: "Select an option" if x is None else ["Very Low", "Moderate", "Very High"][x-1],
                    help=help_text,
                    key=q_id
                )
                if response is not None:
                    st.session_state.responses[q_id] = response
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back: Operational", type="secondary"):
                    st.session_state.feasibility_tab = 1
                    st.rerun()
            with col2:
                if st.button("Next: Complexity →", type="primary"):
                    st.session_state.feasibility_tab = 3
                    st.rerun()
        
        # Complexity
        elif st.session_state.feasibility_tab == 3:
            st.subheader("🎯 Complexity Assessment (5 Questions)")
            
            questions = [
                ("1. RACI / Clarity of Roles", "q30", "Are roles and responsibilities clearly defined?"),
                ("2. Stakeholder Alignment", "q31", "Are stakeholders aligned on project goals?"),
                ("3. Data Availability", "q32", "Is relevant data available for informed decisions?"),
                ("4. Approval Process", "q33", "How efficient is the approval process?"),
                ("5. Adaptability", "q34", "Can the project adapt to changing conditions?")
            ]
            
            for label, q_id, help_text in questions:
                response = st.selectbox(
                    label,
                    options=[None, 1, 2, 3],
                    format_func=lambda x: "Select an option" if x is None else ["Very Low Clarity", "Moderate Clarity", "Very High Clarity"][x-1],
                    help=help_text,
                    key=q_id
                )
                if response is not None:
                    st.session_state.responses[q_id] = response
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back: Scalability", type="secondary"):
                    st.session_state.feasibility_tab = 2
                    st.rerun()
            with col2:
                if st.button("Next: Stakeholder Impact →", type="primary"):
                    st.session_state.current_section = 5
                    st.rerun()
        
        # Main navigation buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Risk Evaluation", type="secondary"):
                st.session_state.current_section = 3
                st.rerun()
        with col2:
            if st.button("Skip to Stakeholder Impact →", type="primary"):
                st.session_state.current_section = 5
                st.rerun()
    
    # Section 5: Stakeholder Impact
    elif st.session_state.current_section == 5:
        st.markdown('<h2 class="section-header">👥 Impact on External Key Stakeholders</h2>', unsafe_allow_html=True)
        
        st.info("All three stakeholder metrics contribute equally (33.33% each) to the total Stakeholder Impact score.")
        
        st.subheader("😇 Customer Satisfaction")
        q35 = st.selectbox(
            "Expected impact on customer satisfaction",
            options=[None, 1, 2, 3],
            format_func=lambda x: "Select an option" if x is None else ["Low Impact (NPS <40%)", "Moderate Impact (NPS 40-70%)", "High Impact (NPS ≥70%)"][x-1],
            help="Assess the project's expected impact on customer satisfaction using NPS methodology.",
            key="q35"
        )
        if q35 is not None:
            st.session_state.responses['q35'] = q35
        
        st.markdown("---")
        
        st.subheader("🤝 Suppliers or Partners Satisfaction")
        q36 = st.selectbox(
            "Expected impact on supplier/partner relationships",
            options=[None, 1, 2, 3],
            format_func=lambda x: "Select an option" if x is None else ["Low Impact (NPS <40%)", "Moderate Impact (NPS 40-70%)", "High Impact (NPS ≥70%)"][x-1],
            help="Evaluate how the project will impact relationships with suppliers and partners.",
            key="q36"
        )
        if q36 is not None:
            st.session_state.responses['q36'] = q36
        
        st.markdown("---")
        
        st.subheader("🌟 Brand Reputation Improvement")
        q37 = st.selectbox(
            "Expected impact on brand reputation",
            options=[None, 1, 2, 3],
            format_func=lambda x: "Select an option" if x is None else ["Low Impact (NPS <40%)", "Moderate Impact (NPS 40-70%)", "High Impact (NPS ≥70%)"][x-1],
            help="Assess whether the project will enhance the organization's brand reputation through recognition or positive media coverage.",
            key="q37"
        )
        if q37 is not None:
            st.session_state.responses['q37'] = q37

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", type="secondary"):
                st.session_state.current_section = 4
                st.rerun()
        with col2:
            if st.button("Next: Document Upload →", type="primary"):
                st.session_state.current_section = 6
                st.rerun()
    
    # Section 6: Document Upload
    elif st.session_state.current_section == 6:
        st.markdown('<h2 class="section-header">📎 Document Upload</h2>', unsafe_allow_html=True)
        
        # Ask user about project status first
        if 'project_status' not in st.session_state:
            st.session_state.project_status = None
        
        st.subheader("📋 Project Assessment Type")
        project_status = st.radio(
            "Is this assessment for:",
            options=["forecast", "completed"],
            format_func=lambda x: {
                "forecast": "🔮 Project Forecasting (Pre-Implementation)",
                "completed": "✅ Completed Project (Post-Implementation)"
            }[x],
            help="Select whether you're assessing a project before implementation (forecasting) or after completion (scoring actual results).",
            key="project_status_radio"
        )
        st.session_state.project_status = project_status
        
        st.markdown("---")
        
        # Conditional messaging based on project status
        if project_status == "completed":
            st.warning("⚠️ **MANDATORY - DOCUMENT UPLOAD REQUIRED**")
            st.info("""
            📌 Since this is a **completed project assessment**, document upload is **MANDATORY** as proof of project completion and results.
            
            **Required documents serve as evidence for:**
            - ✓ Strategic alignment and actual outcomes
            - ✓ Financial results (actual NPV, ROI, costs incurred)
            - ✓ Risk mitigation measures implemented
            - ✓ Feasibility validation and lessons learned
            - ✓ Stakeholder feedback and satisfaction metrics
            
            **You must upload at least 5 documents to proceed to results.**
            """)
            minimum_docs = 5
        else:
            st.success("📌 **OPTIONAL - SUPPORTING DOCUMENTS**")
            st.info("""
            Since this is a **project forecasting assessment**, document upload is **OPTIONAL** but recommended.
            
            **Uploading supporting documents helps validate:**
            - ✓ Projected financial estimates and assumptions
            - ✓ Strategic rationale and business case
            - ✓ Risk assessment methodology
            - ✓ Feasibility studies and technical specifications
            
            **You can skip this section or upload documents for comprehensive record-keeping.**
            """)
            minimum_docs = 0
        
        st.markdown("---")
        
        required_docs = [
            "Project Brief",
            "Strategic Rationale",
            "Financial Assessment",
            "Risk Assessment",
            "Valuation Model",
            "Model Custody",
            "Depository",
            "Value Tracking",
            "Budget Allocation",
            "Fund Availability"
        ]
        
        uploaded_count = 0
        
        for i, doc_type in enumerate(required_docs, 1):
            file = st.file_uploader(
                f"{i}. {doc_type}" + (" *" if project_status == "completed" and i <= minimum_docs else ""),
                type=['pdf', 'docx', 'xlsx', 'pptx'],
                key=f"doc_{i}",
                help=f"{'Required for completed projects' if project_status == 'completed' and i <= minimum_docs else 'Optional'}"
            )
            
            if file:
                st.session_state.uploaded_files[doc_type] = file
                uploaded_count += 1
        
        # Progress indicator
        if project_status == "completed":
            st.progress(min(uploaded_count / minimum_docs, 1.0))
            st.caption(f"Uploaded: {uploaded_count}/{minimum_docs} mandatory documents (Total: {uploaded_count}/{len(required_docs)})")
        else:
            st.progress(uploaded_count / len(required_docs))
            st.caption(f"Uploaded: {uploaded_count}/{len(required_docs)} documents (Optional)")
        
        st.markdown("---")
        
        # Validation for completed projects
        can_proceed = True
        if project_status == "completed" and uploaded_count < minimum_docs:
            can_proceed = False
            st.error(f"❌ You must upload at least {minimum_docs} documents for a completed project assessment. Currently uploaded: {uploaded_count}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", type="secondary", use_container_width=True):
                st.session_state.current_section = 5
                st.rerun()
        
        with col2:
            if uploaded_count > 0:
                if st.button("💾 Upload Documents", type="secondary", use_container_width=True):
                    with st.spinner("Uploading documents..."):
                        for doc_type, file in st.session_state.uploaded_files.items():
                            upload_file_to_storage(st.session_state.project_id, file, doc_type)
                    st.success(f"✅ {uploaded_count} document(s) uploaded successfully!")
        
        with col3:
            if can_proceed:
                if st.button("Next: View Results →", type="primary", use_container_width=True):
                    # Upload any files if they exist
                    if uploaded_count > 0 and st.session_state.project_id:
                        with st.spinner("Uploading documents..."):
                            for doc_type, file in st.session_state.uploaded_files.items():
                                upload_file_to_storage(st.session_state.project_id, file, doc_type)
                    
                    st.session_state.current_section = 7
                    st.rerun()
            else:
                st.button("Next: View Results →", type="primary", use_container_width=True, disabled=True)
                st.caption("⚠️ Upload required documents to proceed")
    
    # Section 7: Results & Report
    elif st.session_state.current_section == 7:
        st.markdown('<h2 class="section-header">📊 Assessment Results</h2>', unsafe_allow_html=True)
        
        # Calculate scores
        scores = calculate_total_score(st.session_state.responses)
        classification, rating, emoji = get_project_classification(scores['total'])
        
        # Display main score with modern design
        if scores['total'] >= 80:
            priority_label = "🎯 MUST HAVE"
            priority_subtitle = "Critical Priority Project"
            priority_color = "#4caf50"
            priority_desc = "Exceptional value - Fast-track for immediate implementation"
        elif scores['total'] >= 60:
            priority_label = "✅ SHOULD HAVE"
            priority_subtitle = "High Value Project"
            priority_color = "#2196f3"
            priority_desc = "Strong business case - Proceed with implementation"
        elif scores['total'] >= 40:
            priority_label = "💡 NICE TO HAVE"
            priority_subtitle = "Discretionary Project"
            priority_color = "#ff9800"
            priority_desc = "Moderate value - Consider when resources available"
        else:
            priority_label = "⚠️ RECONSIDER"
            priority_subtitle = "Low Priority Project"
            priority_color = "#f44336"
            priority_desc = "Limited value - Requires major improvements or deferral"
        
        # Full width score box
        st.markdown(f"""
        <div class="modern-score-box">
            <h1>{emoji} {scores['total']:.2f}%</h1>
            <h2>{classification}</h2>
            <div class="feasible-badge" style="background-color: {priority_color}; color: white; font-size: 1.65rem; margin-top: 1.5rem;">
                {priority_label}
            </div>
            <h3 style="margin-top: 0.5rem; color: #2c3e50;">{priority_subtitle}</h3>
            <p style="font-size: 1rem; color: #34495e; margin-top: 0.5rem; font-style: italic;">{priority_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Collapsible Score Classification Guide
        with st.expander("ℹ️ **Understanding Your Score - Classification Guide**", expanded=False):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f7f5fa 0%, #cdc3e2 100%); 
                        border: 2px solid #8933a6; 
                        padding: 1.5rem; 
                        border-radius: 15px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #7c3387; margin-bottom: 1rem; text-align: center;">📊 Score Classification Range</h3>
                <div style="font-size: 1rem; line-height: 2;">
                    <div style="background: #4caf50; color: white; padding: 12px; margin: 8px 0; border-radius: 8px; font-weight: 600;">
                        🎯 ≥80% - Crucial (MUST HAVE) - Critical priority for immediate implementation
                    </div>
                    <div style="background: #2196f3; color: white; padding: 12px; margin: 8px 0; border-radius: 8px; font-weight: 600;">
                        ✅ ≥60% - Essential (SHOULD HAVE) - High value, proceed with implementation
                    </div>
                    <div style="background: #ff9800; color: white; padding: 12px; margin: 8px 0; border-radius: 8px; font-weight: 600;">
                        💡 ≥40% - Optional (NICE TO HAVE) - Consider when resources available
                    </div>
                    <div style="background: #f44336; color: white; padding: 12px; margin: 8px 0; border-radius: 8px; font-weight: 600;">
                        ⚠️ &lt;40% - Insignificant (RECONSIDER) - Requires major improvements
                    </div>
                </div>
                <hr style="margin: 1.5rem 0; border: 1px solid #7c3387;">
                <h4 style="color: #7c3387; margin-bottom: 0.8rem;">📈 What Contributes to Your Score:</h4>
                <ul style="color: #34495e; font-size: 0.95rem; line-height: 1.8;">
                    <li><strong>Strategy Evaluation (10%):</strong> Alignment with organizational goals and strategic priorities</li>
                    <li><strong>Financial Evaluation (30%):</strong> NPV, ROI, Payback Period, and IRR metrics</li>
                    <li><strong>Risk Evaluation (25%):</strong> Data quality, technical complexity, timeline, and budget risks</li>
                    <li><strong>Project Feasibility (30%):</strong> Technical, operational, scalability, and complexity factors</li>
                    <li><strong>Stakeholder Impact (5%):</strong> Customer, supplier/partner, and brand reputation effects</li>
                </ul>
                <p style="font-size: 0.85rem; color: #666; margin-top: 1rem; text-align: center; font-style: italic; border-top: 1px solid #ddd; padding-top: 1rem;">
                    💡 Tip: Projects scoring ≥60% are considered feasible and recommended for approval
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Section breakdown with progress bars instead of metric cards
        st.subheader("📈 Section Performance Breakdown")
        st.markdown("<br>", unsafe_allow_html=True)
        
        sections_data = [
            ("Strategy Evaluation", scores['strategy'], SECTION_WEIGHTS['strategy'], "#1f77b4"),
            ("Financial Evaluation", scores['financial'], SECTION_WEIGHTS['financial'], "#ff7f0e"),
            ("Risk Evaluation", scores['risk'], SECTION_WEIGHTS['risk'], "#2ca02c"),
            ("Project Feasibility", scores['feasibility'], SECTION_WEIGHTS['feasibility'], "#d62728"),
            ("Stakeholder Impact", scores['stakeholder'], SECTION_WEIGHTS['stakeholder'], "#9467bd")
        ]
        
        for section_name, section_score, weight, color in sections_data:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Determine status emoji
                if section_score >= 80:
                    status = "🟢 Excellent"
                elif section_score >= 60:
                    status = "🟡 Good"
                elif section_score >= 40:
                    status = "🟠 Fair"
                else:
                    status = "🔴 Poor"
                
                st.markdown(f"**{section_name}** {status}")
                st.progress(section_score / 100)
            
            with col2:
                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: bold; color: {color};'>{section_score:.1f}%</div>", unsafe_allow_html=True)
                st.caption("Raw Score")
            
            with col3:
                weighted_score = section_score * weight
                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: bold; color: {color};'>{weighted_score:.2f}</div>", unsafe_allow_html=True)
                st.caption(f"Weight: {weight*100:.0f}%")
        
        st.markdown("---")
        
        # Visualizations
        st.subheader("📊 Score Visualizations")
        
        fig_radar, fig_bar, fig_waterfall, fig_gauge = create_score_visualization(scores)
        
        # First row: Radar and Bar
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_radar, width="stretch")
        with col2:
            st.plotly_chart(fig_bar, width="stretch")
        
        # Second row: Waterfall and Gauge
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_waterfall, width="stretch")
        with col2:
            st.plotly_chart(fig_gauge, width="stretch")
        
        st.markdown("---")
        
        # Justification Section
        st.subheader("📋 Assessment Justification")
        justification_text = generate_justification(scores)
        st.markdown(justification_text)
        
        st.markdown("---")
        
        # PDF Download
        st.subheader("📄 Download Comprehensive Report")
        st.info("💡 The PDF report includes all detailed calculation breakdowns, justification and recommendations.")
        
        if st.button("🔄 Generate PDF Report", type="primary"):
            with st.spinner("Generating comprehensive PDF report with charts..."):
                pdf_buffer = generate_pdf_report(
                    st.session_state.responses.get('project_name', 'Untitled'),
                    st.session_state.responses,
                    scores
                )
                
                # Store PDF in session state
                st.session_state.pdf_buffer = pdf_buffer
                st.session_state.pdf_generated = True
                
                st.success("✅ Report generated successfully!")
                
        # Show download button if PDF is generated
        if st.session_state.get('pdf_generated', False):
            st.download_button(
                label="⬇️ Download PDF Report",
                data=st.session_state.pdf_buffer,
                file_name=f"VIA_Report_{st.session_state.responses.get('project_name', 'Project')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                type="primary",
                on_click=lambda: st.session_state.update({'pdf_downloaded': True})
            )
            
            # Purple success message after download
            if st.session_state.get('pdf_downloaded', False):
                st.markdown("""
                <div style="
                    background-color: #f8e6fc;
                    border-left: 5px solid #ab5eb8;
                    padding: 12px 16px;
                    border-radius: 5px;
                    margin-top: 10px;
                ">
                    <p style="color: #6a3d8a; font-weight: 500; margin: 0;">✅ Successfully Downloaded!</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("← Back to Documents", type="secondary", width="stretch"):
                st.session_state.current_section = 6
                st.rerun()
        
        with col2:
            if st.button("📊 View Response Data", type="primary", width="stretch"):
                st.subheader("📋 Assessment Responses")
                
                # Create a formatted DataFrame with question text
                response_data = []
                for key, value in st.session_state.responses.items():
                    if key != 'project_name' and key != 'strategic_focus':
                        response_data.append({
                            'Question ID': key.upper(),
                            'Subject': QUESTION_TEXT.get(key, 'Unknown Question'),
                            'Response Value': str(value)
                        })
                
                if response_data:
                    df = pd.DataFrame(response_data)
                    st.dataframe(df, width="stretch", hide_index=True)
                else:
                    st.info("No response data available yet")
        
        with col3:
            if st.button("🔄 Start New Assessment", type="secondary", width="stretch"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()             

if __name__ == "__main__":
    main()
