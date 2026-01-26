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
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .help-icon {
        background-color: #e3f2fd;
        border-radius: 50%;
        padding: 0.2rem 0.5rem;
        font-weight: bold;
        color: #1976d2;
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
        background: linear-gradient(90deg, #1f77b4 0%, #2c3e50 100%);
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
    "technical": 0.1667,
    "operational": 0.1667,
    "scalability": 0.3333,
    "complexity": 0.50
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
    """Calculate risk section score (inverse scoring - lower risk = higher score)"""
    risk_scores = []
    risk_questions = ['q12', 'q13', 'q14', 'q15']
    
    for q in risk_questions:
        if f"{q}_prob" in responses and f"{q}_impact" in responses:
            risk_value = responses[f"{q}_prob"] * responses[f"{q}_impact"]
            # Inverse scoring: max risk (1*1=1) becomes lowest score, min risk (3*3=9) becomes highest
            normalized_score = (9 - risk_value) / 8  # Scale 0-1
            risk_scores.append(normalized_score)
    
    return (sum(risk_scores) / len(risk_scores)) * 100 if risk_scores else 0

def calculate_feasibility_score(responses):
    """Calculate feasibility section score"""
    # Technical Feasibility (Q16-Q19)
    tech_weights = {'q16': 0.30, 'q17': 0.20, 'q18': 0.20, 'q19': 0.30}
    tech_score = sum((responses.get(q, 0) / 3) * w for q, w in tech_weights.items())
    
    # Operational Feasibility (Q20-Q24)
    op_weights = {'q20': 0.20, 'q21': 0.20, 'q22': 0.20, 'q23': 0.20, 'q24': 0.20}
    op_score = sum((responses.get(q, 0) / 3) * w for q, w in op_weights.items())
    
    # Scalability & Sustainability (Q25-Q29)
    scale_weights = {'q25': 0.30, 'q26': 0.20, 'q27': 0.20, 'q28': 0.15, 'q29': 0.15}
    scale_score = sum((responses.get(q, 0) / 3) * w for q, w in scale_weights.items())
    
    # Complexity (Q30-Q34)
    complex_weights = {'q30': 0.20, 'q31': 0.20, 'q32': 0.20, 'q33': 0.20, 'q34': 0.20}
    complex_score = sum((responses.get(q, 0) / 3) * w for q, w in complex_weights.items())
    
    # Weighted average based on subsection weights
    total_score = (
        tech_score * FEASIBILITY_WEIGHTS['technical'] +
        op_score * FEASIBILITY_WEIGHTS['operational'] +
        scale_score * FEASIBILITY_WEIGHTS['scalability'] +
        complex_score * FEASIBILITY_WEIGHTS['complexity']
    )
    
    return total_score * 100

def calculate_stakeholder_score(responses):
    """Calculate stakeholder impact score"""
    if 'q37' in responses:  # Brand reputation is used
        return (responses['q37'] / 3) * 100
    elif 'q35' in responses and 'q36' in responses:  # Customer + Supplier
        return ((responses['q35'] + responses['q36']) / 2 / 3) * 100
    elif 'q35' in responses:  # Customer only
        return (responses['q35'] / 3) * 100
    return 0

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
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        )
    ])
    
    fig_bar.update_layout(
        title="Weighted Score Contribution",
        xaxis_title="Section",
        yaxis_title="Weighted Score",
        yaxis_range=[0, 40]
    )
    
    return fig_radar, fig_bar

def generate_pdf_report(project_name, responses, scores):
    """Generate comprehensive PDF report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Value Impact Assessment Report", title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Project Information
    elements.append(Paragraph(f"<b>Project Name:</b> {project_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Assessment Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    classification, rating, emoji = get_project_classification(scores['total'])
    elements.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Score', f"{scores['total']:.2f}%"],
        ['Classification', classification],
        ['Priority Rating', rating],
        ['Feasibility', 'Feasible' if scores['total'] >= 60 else 'Not Feasible']
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(PageBreak())
    
    # Detailed Scores
    elements.append(Paragraph("<b>Detailed Section Scores</b>", styles['Heading2']))
    
    score_data = [
        ['Section', 'Score (%)', 'Weight', 'Weighted Score'],
        ['Strategy Evaluation', f"{scores['strategy']:.2f}", '10%', f"{scores['strategy'] * 0.10:.2f}"],
        ['Financial Evaluation', f"{scores['financial']:.2f}", '30%', f"{scores['financial'] * 0.30:.2f}"],
        ['Risk Evaluation', f"{scores['risk']:.2f}", '25%', f"{scores['risk'] * 0.25:.2f}"],
        ['Project Feasibility', f"{scores['feasibility']:.2f}", '30%', f"{scores['feasibility'] * 0.30:.2f}"],
        ['Stakeholder Impact', f"{scores['stakeholder']:.2f}", '5%', f"{scores['stakeholder'] * 0.05:.2f}"],
        ['', '', 'Total:', f"{scores['total']:.2f}%"]
    ]
    
    score_table = Table(score_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(score_table)
    
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
        st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Your+Logo",
    width=150
)

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
        
        selected = st.radio("Navigation", sections, index=st.session_state.current_section)
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
                "Market Expansion (Non-Trad)",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                key="q5a"
            )
            st.session_state.responses['q5a'] = q5a
        
        with col2:
            q5b = st.selectbox(
                "Revenue Generation (Non-Trad)",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                key="q5b"
            )
            st.session_state.responses['q5b'] = q5b
        
        with col3:
            q5c = st.selectbox(
                "Gross Profit (Non-Trad)",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Not Relevant", "Low (<3%)", "Moderate (3-9%)", "High (≥10%)"][x],
                key="q5c"
            )
            st.session_state.responses['q5c'] = q5c
        
        st.markdown("---")
        
        # Net Zero Carbon
        st.subheader("🌱 Net Zero Carbon Emissions")
        q6 = st.selectbox(
            "Carbon Emissions Impact",
            options=[0, 1, 2, 3],
            format_func=lambda x: ["Not Relevant (<5%)", "Low (5-19%)", "Moderate", "High (≥20%)"][x],
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
        st.info("For each risk, assess both the Probability (likelihood) and Impact (severity if it occurs).")
        
        risks = [
            ("Data Quality Issues", "q12", "Assess the likelihood and potential impact of data quality problems."),
            ("Technological Complexity", "q13", "Evaluate the complexity of technology implementation."),
            ("Timeline Delays", "q14", "Assess the likelihood of project timeline delays."),
            ("Budget Constraints", "q15", "Evaluate the probability of budget overruns.")
        ]
        
        for i, (risk_name, q_id, help_text) in enumerate(risks):
            with st.expander(f"📋 {risk_name}", expanded=True):
                st.caption(help_text)
                col1, col2 = st.columns(2)
                
                with col1:
                    prob = st.selectbox(
                        "Probability",
                        options=[1, 2, 3],
                        format_func=lambda x: ["Very Likely", "Possible", "Not Likely"][x-1],
                        key=f"{q_id}_prob_select"
                    )
                    st.session_state.responses[f'{q_id}_prob'] = prob
                
                with col2:
                    impact = st.selectbox(
                        "Impact",
                        options=[1, 2, 3],
                        format_func=lambda x: ["Very High", "Moderate", "Very Low"][x-1],
                        key=f"{q_id}_impact_select"
                    )
                    st.session_state.responses[f'{q_id}_impact'] = impact
                
                risk_score = prob * impact
                risk_level = "🔴 High Risk" if risk_score <= 3 else "🟡 Medium Risk" if risk_score <= 6 else "🟢 Low Risk"
                st.metric("Risk Score", f"{risk_level} ({risk_score}/9)")
        
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
        
        tabs = st.tabs(["Technical", "Operational", "Scalability", "Complexity"])
        
        # Technical Feasibility
        with tabs[0]:
            st.subheader("⚙️ Technical Feasibility")
            
            q16 = st.selectbox(
                "Technology Availability",
                options=[1, 2, 3],
                format_func=lambda x: ["Very Low", "Moderate", "Very High"][x-1],
                help="Are the required technologies readily available?",
                key="q16"
            )
            st.session_state.responses['q16'] = q16
            
            q17 = st.selectbox(
                "Technical Expertise",
                options=[1, 2, 3],
                format_func=lambda x: ["Very Low", "Moderate", "Very High"][x-1],
                help="Does the team have the required skills and experience?",
                key="q17"
            )
            st.session_state.responses['q17'] = q17
            
            q18 = st.selectbox(
                "Infrastructure Needs",
                options=[1, 2, 3],
                format_func=lambda x: ["Very Low", "Moderate", "Very High"][x-1],
                help="Is the required hardware and software infrastructure available?",
                key="q18"
            )
            st.session_state.responses['q18'] = q18
            
            q19 = st.selectbox(
                "Integration Complexity",
                options=[1, 2, 3],
                format_func=lambda x: ["Very Low", "Moderate", "Very High"][x-1],
                help="How easy is it to integrate with current systems?",
                key="q19"
            )
            st.session_state.responses['q19'] = q19
        
        # Operational Feasibility
        with tabs[1]:
            st.subheader("🏭 Operational Feasibility")
            
            questions = [
                ("Process Compatibility", "q20", "How well does the project align with existing workflows?"),
                ("Resource Availability", "q21", "Are personnel, equipment, and materials available?"),
                ("User Acceptance", "q22", "What is the likelihood of user adoption?"),
                ("Training Requirements", "q23", "What level of training is needed?"),
                ("Supportability", "q24", "How easy is it to maintain and support long-term?")
            ]
            
            for label, q_id, help_text in questions:
                response = st.selectbox(
                    label,
                    options=[1, 2, 3],
                    format_func=lambda x: ["Very Low", "Moderate", "Very High"][x-1],
                    help=help_text,
                    key=q_id
                )
                st.session_state.responses[q_id] = response
        
        # Scalability & Sustainability
        with tabs[2]:
            st.subheader("📊 Scalability & Sustainability")
            
            questions = [
                ("System Performance", "q25", "Can the system handle increased data and user load?"),
                ("Expansion Flexibility", "q26", "How easy is it to add/remove features or users?"),
                ("Resource Efficiency", "q27", "How efficiently does the system use resources?"),
                ("Long-Term Costs", "q28", "What are the anticipated maintenance and operational costs?"),
                ("Environmental Impact", "q29", "What is the environmental sustainability of the project?")
            ]
            
            for label, q_id, help_text in questions:
                response = st.selectbox(
                    label,
                    options=[1, 2, 3],
                    format_func=lambda x: ["Very Low", "Moderate", "Very High"][x-1],
                    help=help_text,
                    key=q_id
                )
                st.session_state.responses[q_id] = response
        
        # Complexity
        with tabs[3]:
            st.subheader("🎯 Complexity Assessment")
            
            questions = [
                ("RACI / Clarity of Roles", "q30", "Are roles and responsibilities clearly defined?"),
                ("Stakeholder Alignment", "q31", "Are stakeholders aligned on project goals?"),
                ("Data Availability", "q32", "Is relevant data available for informed decisions?"),
                ("Approval Process", "q33", "How efficient is the approval process?"),
                ("Adaptability", "q34", "Can the project adapt to changing conditions?")
            ]
            
            for label, q_id, help_text in questions:
                response = st.selectbox(
                    label,
                    options=[1, 2, 3],
                    format_func=lambda x: ["Very Low Clarity", "Moderate Clarity", "Very High Clarity"][x-1],
                    help=help_text,
                    key=q_id
                )
                st.session_state.responses[q_id] = response
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", type="secondary"):
                st.session_state.current_section = 3
                st.rerun()
        with col2:
            if st.button("Next: Stakeholder Impact →", type="primary"):
                st.session_state.current_section = 5
                st.rerun()
    
    # Section 5: Stakeholder Impact
    elif st.session_state.current_section == 5:
        st.markdown('<h2 class="section-header">👥 Impact on External Key Stakeholders</h2>', unsafe_allow_html=True)
        
        st.info("Select the stakeholder impact metrics that apply to your project.")
        
        use_brand = st.checkbox("Evaluate Brand Reputation (replaces Customer + Supplier metrics)")
        
        if use_brand:
            q37 = st.selectbox(
                "Brand Reputation Improvement",
                options=[1, 2, 3],
                format_func=lambda x: ["Low Impact (NPS <40%)", "Moderate Impact (NPS 40-70%)", "High Impact (NPS ≥70%)"][x-1],
                help="Will the project improve brand reputation through public recognition, awards, or positive media coverage?"
            )
            st.session_state.responses['q37'] = q37
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                q35 = st.selectbox(
                    "Customer Satisfaction",
                    options=[1, 2, 3],
                    format_func=lambda x: ["Low Impact (NPS <40%)", "Moderate Impact (NPS 40-70%)", "High Impact (NPS ≥70%)"][x-1],
                    help="Expected impact on customer satisfaction using NPS methodology."
                )
                st.session_state.responses['q35'] = q35
            
            with col2:
                q36 = st.selectbox(
                    "Suppliers/Partners Satisfaction",
                    options=[1, 2, 3],
                    format_func=lambda x: ["Low Impact (NPS <40%)", "Moderate Impact (NPS 40-70%)", "High Impact (NPS ≥70%)"][x-1],
                    help="Expected impact on supplier/partner relationships."
                )
                st.session_state.responses['q36'] = q36
        
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
        st.warning("All 10 documents are mandatory for project approval.")
        
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
                f"{i}. {doc_type}",
                type=['pdf', 'docx', 'xlsx', 'pptx'],
                key=f"doc_{i}"
            )
            
            if file:
                st.session_state.uploaded_files[doc_type] = file
                uploaded_count += 1
        
        st.progress(uploaded_count / len(required_docs))
        st.caption(f"Uploaded: {uploaded_count}/{len(required_docs)} documents")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", type="secondary"):
                st.session_state.current_section = 5
                st.rerun()
        with col2:
            if uploaded_count == len(required_docs):
                if st.button("Calculate Results →", type="primary"):
                    # Upload files to Supabase
                    with st.spinner("Uploading documents..."):
                        for doc_type, file in st.session_state.uploaded_files.items():
                            upload_file_to_storage(st.session_state.project_id, file, doc_type)
                    
                    st.session_state.current_section = 7
                    st.rerun()
            else:
                st.error(f"Please upload all {len(required_docs)} required documents.")
    
    # Section 7: Results & Report
    elif st.session_state.current_section == 7:
        st.markdown('<h2 class="section-header">📊 Assessment Results</h2>', unsafe_allow_html=True)
        
        # Calculate scores
        scores = calculate_total_score(st.session_state.responses)
        classification, rating, emoji = get_project_classification(scores['total'])
        
        # Display main score
        st.markdown(f"""
        <div class="score-box">
            <h1>{emoji} {scores['total']:.2f}%</h1>
            <h2>{classification}</h2>
            <h3>Priority: {rating}</h3>
            <h4>{'✅ FEASIBLE' if scores['total'] >= 60 else '❌ NOT FEASIBLE'}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Section breakdown
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Strategy", f"{scores['strategy']:.1f}%", f"Weight: {SECTION_WEIGHTS['strategy']*100}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Financial", f"{scores['financial']:.1f}%", f"Weight: {SECTION_WEIGHTS['financial']*100}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Risk", f"{scores['risk']:.1f}%", f"Weight: {SECTION_WEIGHTS['risk']*100}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Feasibility", f"{scores['feasibility']:.1f}%", f"Weight: {SECTION_WEIGHTS['feasibility']*100}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Stakeholder", f"{scores['stakeholder']:.1f}%", f"Weight: {SECTION_WEIGHTS['stakeholder']*100}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Visualizations
        st.subheader("📈 Score Visualizations")
        
        fig_radar, fig_bar = create_score_visualization(scores)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_radar, use_container_width=True)
        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        # PDF Download
        st.subheader("📄 Download Report")
        
        pdf_buffer = generate_pdf_report(
            st.session_state.responses.get('project_name', 'Untitled'),
            st.session_state.responses,
            scores
        )
        
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_buffer,
            file_name=f"VIA_Report_{st.session_state.responses.get('project_name', 'Project')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            type="primary"
        )
        
        if st.button("🔄 Start New Assessment"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()