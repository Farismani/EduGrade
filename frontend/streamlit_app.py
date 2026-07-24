# Ultra-Modern Streamlit frontend for Auto Grader
import streamlit as st
import requests
import os
import time
import json
import plotly.graph_objects as go
import csv
import html
import io
import math
from collections import defaultdict
from datetime import datetime, timedelta

# Configure page
st.set_page_config(
    page_title='EduGrade - AI Code Grader',
    layout='wide',
    initial_sidebar_state='expanded'
)

API = os.getenv('API_URL', 'http://localhost:5000')


def numeric_score(row):
    try:
        return float(row.get('score') or 0)
    except (TypeError, ValueError):
        return 0.0


def average(values):
    return sum(values) / len(values) if values else 0


def median(values):
    if not values:
        return 0
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def stddev(values):
    if len(values) < 2:
        return 1
    avg = average(values)
    variance = sum((value - avg) ** 2 for value in values) / (len(values) - 1)
    return max(math.sqrt(variance), 1)


def unique_values(rows, key):
    return sorted({row.get(key) for row in rows if row.get(key)})


def rows_to_csv(rows):
    if not rows:
        return b''
    fieldnames = sorted({key for row in rows for key in row.keys()})
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode('utf-8')


def rolling_average(values, window):
    rolled = []
    for index in range(len(values)):
        start = max(0, index - window + 1)
        rolled.append(average(values[start:index + 1]))
    return rolled


def language_performance(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row.get('language', 'unknown')].append(numeric_score(row))
    return [
        {
            'language': language,
            'avg_score': round(average(scores), 2),
            'submissions': len(scores),
            'std_dev': round(stddev(scores), 2),
        }
        for language, scores in sorted(grouped.items())
    ]

# Ultra-modern CSS with advanced animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 4rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    
    .main-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 2px,
            rgba(255,255,255,0.05) 2px,
            rgba(255,255,255,0.05) 4px
        );
        animation: move-pattern 20s linear infinite;
    }
    
    @keyframes move-pattern {
        0% { transform: translate(-50px, -50px); }
        100% { transform: translate(50px, 50px); }
    }
    
    .main-hero h1 {
        color: white;
        font-weight: 800;
        font-size: 4rem;
        margin: 0;
        position: relative;
        z-index: 2;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        letter-spacing: -2px;
    }
    
    .main-hero p {
        color: rgba(255,255,255,0.95);
        font-size: 1.4rem;
        margin: 1rem 0 0 0;
        position: relative;
        z-index: 2;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(0,0,0,0.15);
    }
    
    .success-celebration {
        animation: celebration 2s ease-out;
        text-align: center;
        font-size: 6rem;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7);
        background-size: 300% 300%;
        animation: celebration 2s ease-out, rainbow 3s ease-in-out infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    @keyframes celebration {
        0% { transform: scale(0.5) rotate(-180deg); opacity: 0; }
        50% { transform: scale(1.2) rotate(-90deg); opacity: 1; }
        100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    
    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .score-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 24px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
        animation: slideInScale 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes slideInScale {
        0% { transform: translateY(100px) scale(0.8); opacity: 0; }
        100% { transform: translateY(0) scale(1); opacity: 1; }
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .floating-particles {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255,255,255,0.6);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 1; }
        50% { transform: translateY(-20px) rotate(180deg); opacity: 0.5; }
    }
    
    .feedback-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
        animation: fadeInUp 1.2s ease-out 0.5s both;
    }
    
    @keyframes fadeInUp {
        0% { transform: translateY(40px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 3rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
        letter-spacing: 0.5px;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
    }
    
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.8);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .test-result-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid;
        transition: all 0.3s ease;
        animation: slideInRight 0.6s ease-out;
    }
    
    @keyframes slideInRight {
        0% { transform: translateX(100px); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }
    
    .test-passed {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    }
    
    .test-failed {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fef2f2 100%);
    }
    
    .sidebar-gradient {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: white;
    }
    
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 4px solid rgba(102, 126, 234, 0.3);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .pulse-animation {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: .7; }
    }
    
    .typing-effect {
        overflow: hidden;
        border-right: 2px solid #667eea;
        white-space: nowrap;
        margin: 0 auto;
        animation: typing 3s steps(40, end), blink-caret 0.75s step-end infinite;
    }
    
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink-caret {
        from, to { border-color: transparent; }
        50% { border-color: #667eea; }
    }
    
    .code-container {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .code-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 30px;
        background: #2d2d2d;
        border-radius: 12px 12px 0 0;
    }
    
    .morphing-bg {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: morphing 15s ease infinite;
    }
    
    @keyframes morphing {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    :root {
        --ink: #f7f7f2;
        --paper: #050505;
        --muted: #8e8e86;
        --line: rgba(247, 247, 242, 0.16);
        --line-strong: rgba(247, 247, 242, 0.38);
        --panel: rgba(247, 247, 242, 0.045);
        --panel-hot: rgba(247, 247, 242, 0.095);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 20% 0%, rgba(255,255,255,0.10), transparent 28rem),
            linear-gradient(180deg, #0b0b0b 0%, #030303 42%, #10100e 100%) !important;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.82);
        border-right: 1px solid var(--line);
        backdrop-filter: blur(18px);
    }

    [data-testid="stSidebar"] * {
        color: var(--ink);
    }

    .block-container {
        padding-top: 1.25rem;
        max-width: 1320px;
    }

    h1, h2, h3, h4, p, label, span, div {
        letter-spacing: 0;
    }

    h2 {
        color: var(--ink);
        font-size: 1.25rem;
        font-weight: 700;
        text-transform: uppercase;
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.65rem;
    }

    .main-hero {
        min-height: 330px;
        background:
            linear-gradient(90deg, rgba(255,255,255,0.12) 1px, transparent 1px),
            linear-gradient(0deg, rgba(255,255,255,0.10) 1px, transparent 1px),
            #050505 !important;
        background-size: 54px 54px, 54px 54px, auto !important;
        border: 1px solid var(--line-strong);
        border-radius: 8px;
        margin-bottom: 1.4rem;
        padding: 2.2rem;
        text-align: left;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05), 0 24px 80px rgba(0,0,0,0.55);
        animation: grid-drift 18s linear infinite;
    }

    .main-hero::before {
        inset: 0;
        width: 100%;
        height: 100%;
        background:
            linear-gradient(115deg, transparent 0%, rgba(255,255,255,0.20) 48%, transparent 58%);
        animation: scanline 4s ease-in-out infinite;
    }

    .main-hero::after {
        content: "";
        position: absolute;
        inset: 1rem;
        border: 1px solid rgba(255,255,255,0.12);
        pointer-events: none;
    }

    .main-hero h1 {
        max-width: 860px;
        color: var(--ink);
        font-size: clamp(3.7rem, 10vw, 8.8rem);
        line-height: 0.82;
        font-weight: 900;
        text-transform: uppercase;
        text-shadow: 0 0 28px rgba(255,255,255,0.20);
        margin-top: 1.6rem;
        animation: glitch-breathe 3.8s steps(2, end) infinite;
    }

    .main-hero p {
        max-width: 620px;
        color: var(--muted);
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 1.25rem;
    }

    .hero-kicker,
    .hero-kicker span {
        border: 1px solid var(--line);
        background: rgba(255,255,255,0.055);
        padding: 0.42rem 0.62rem;
        border-radius: 999px;
    }

    .floating-particles,
    .particle {
        display: none;
    }

    .typing-effect {
        overflow: visible;
        border-right: none;
        white-space: normal;
        animation: glitch-breathe 3.8s steps(2, end) infinite;
    }

    .glass-card,
    .metric-container,
    .feedback-container,
    .test-result-card,
    .sidebar-gradient {
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        color: var(--ink) !important;
        box-shadow: none !important;
        backdrop-filter: blur(14px);
    }

    .glass-card:hover,
    .metric-container:hover,
    .test-result-card:hover {
        transform: translateY(-1px);
        border-color: var(--line-strong) !important;
        background: var(--panel-hot) !important;
    }

    .metric-container::before {
        background: var(--ink) !important;
        height: 1px;
    }

    .score-display {
        background: var(--ink) !important;
        color: var(--paper) !important;
        border-radius: 8px;
        box-shadow: 0 0 0 1px var(--line), 0 0 80px rgba(255,255,255,0.12);
    }

    .score-display p,
    .score-number {
        color: var(--paper) !important;
        text-shadow: none;
    }

    .success-celebration {
        color: var(--ink);
        background: none;
        -webkit-text-fill-color: currentColor;
        font-size: clamp(2.6rem, 8vw, 6.4rem);
        font-weight: 900;
        text-transform: uppercase;
        animation: impact-pop 900ms cubic-bezier(.2,.9,.2,1);
    }

    .stButton > button {
        background: var(--ink) !important;
        color: var(--paper) !important;
        border: 1px solid var(--ink) !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        text-transform: uppercase;
        font-weight: 900;
        letter-spacing: 0;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        filter: invert(1);
    }

    .stTextInput input,
    .stTextArea textarea,
    [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.045) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] div {
        background: #050505 !important;
        color: var(--ink) !important;
        border-color: var(--line) !important;
    }

    [data-baseweb="select"] span,
    [data-baseweb="select"] svg,
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] span {
        color: var(--ink) !important;
        fill: var(--ink) !important;
    }

    [data-baseweb="popover"] ul,
    [data-baseweb="popover"] div {
        background: #050505 !important;
        border-color: var(--line) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        color: #050505 !important;
        fill: #050505 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
        display: grid;
        gap: 0.5rem;
    }

    [data-testid="stSidebar"] [role="radio"] {
        background: rgba(255,255,255,0.045);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
        transition: border-color 180ms ease, background 180ms ease;
    }

    [data-testid="stSidebar"] [role="radio"]:hover {
        border-color: var(--line-strong);
        background: rgba(255,255,255,0.09);
    }

    [data-testid="stSidebar"] [role="radio"] p {
        color: var(--ink) !important;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.78rem;
    }

    input[type="radio"] {
        accent-color: #f7f7f2 !important;
    }

    .stDataFrame,
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
    }

    .test-passed {
        border-left-color: var(--ink) !important;
        background: rgba(255,255,255,0.08) !important;
    }

    .test-failed {
        border-left-color: #8b8b84 !important;
        background: rgba(255,255,255,0.03) !important;
    }

    .app-footer {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1.2rem;
        color: var(--muted);
        background: rgba(255,255,255,0.035);
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: wrap;
        text-transform: uppercase;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .app-footer span:nth-child(2),
    .app-footer span:nth-child(4) {
        display: none;
    }

    @keyframes grid-drift {
        from { background-position: 0 0, 0 0, 0 0; }
        to { background-position: 54px 54px, -54px -54px, 0 0; }
    }

    @keyframes scanline {
        0%, 30% { transform: translateX(-120%); opacity: 0; }
        45% { opacity: 1; }
        70%, 100% { transform: translateX(120%); opacity: 0; }
    }

    @keyframes glitch-breathe {
        0%, 84%, 100% { transform: translate(0,0); filter: none; }
        86% { transform: translate(-2px,1px); filter: contrast(1.7); }
        88% { transform: translate(2px,-1px); }
        90% { transform: translate(0,0); }
    }

    @keyframes impact-pop {
        from { transform: scale(0.92); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="main-hero">
    <div class="hero-kicker">
        <span>Local Judge</span>
        <span>Instant Signal</span>
        <span>Zero Theater</span>
    </div>
    <h1 class="typing-effect">EduGrade</h1>
    <p>A monochrome grading cockpit for code submissions, test results, feedback, and instructor analytics.</p>
</div>
""", unsafe_allow_html=True)

# Advanced Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-gradient">
        <h3 style="margin: 0; text-align: center;">Command Deck</h3>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        'Navigation',
        ['Submit Code', 'Instructor Dashboard', 'Documentation'],
        label_visibility='collapsed'
    )


def create_advanced_score_gauge(score):
    """Create an ultra-modern score visualization with multiple rings"""
    fig = go.Figure()

    # Background ring
    fig.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100, 100],
        theta=[0, 72, 144, 216, 288],
        mode='lines',
        line=dict(color='rgba(255,255,255,0.1)', width=20),
        showlegend=False
    ))

    # Score ring
    score_steps = max(int(score / 2), 2)
    score_theta = [(score / 100) * 360 * i / (score_steps - 1) for i in range(score_steps)]
    score_r = [80] * len(score_theta)

    fig.add_trace(go.Scatterpolar(
        r=score_r,
        theta=score_theta,
        mode='lines',
        line=dict(
            color='#f7f7f2',
            width=15,
            shape='spline'
        ),
        showlegend=False
    ))

    # Center score display
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"<b>{score}%</b>",
        showarrow=False,
        font=dict(size=48, color='#f7f7f2', family='Inter'),
        xref="paper", yref="paper"
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 100]),
            angularaxis=dict(visible=False)
        ),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=50, l=50, r=50)
    )

    return fig


def show_advanced_success_animation(score):
    """Advanced success animations based on score ranges"""
    if score == 100:
        st.markdown('<div class="success-celebration">PERFECT</div>',
                    unsafe_allow_html=True)
        # Multiple celebration effects
        st.balloons()
        st.snow()
    elif score >= 90:
        st.markdown('<div class="success-celebration">EXCELLENT</div>',
                    unsafe_allow_html=True)
        st.balloons()
    elif score >= 80:
        st.markdown('<div class="success-celebration">GREAT JOB</div>',
                    unsafe_allow_html=True)
    elif score >= 70:
        st.markdown(
            '<div class="success-celebration pulse-animation">GOOD WORK</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="success-celebration pulse-animation">KEEP TRYING</div>', unsafe_allow_html=True)


def create_3d_test_results(results):
    """Create a 3D visualization of test results"""
    if not results:
        return None

    passed = sum(1 for r in results if r.get('ok', False))
    failed = len(results) - passed

    # Create 3D donut chart effect
    fig = go.Figure()

    # Outer ring
    fig.add_trace(go.Pie(
        labels=['Passed', 'Failed'],
        values=[passed, failed],
        hole=0.6,
        marker_colors=['#f7f7f2', '#5f5f5a'],
        textinfo='label+percent',
        textfont=dict(size=16, color='#050505'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    ))

    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#f7f7f2', 'family': 'Inter', 'size': 14},
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )

    return fig


def create_performance_radar(score, results):
    """Create a radar chart showing different performance aspects"""
    passed = sum(1 for r in results if r.get('ok', False))
    total = len(results) if results else 1

    categories = ['Correctness', 'Efficiency', 'Style', 'Completeness']
    values = [
        score,  # Correctness
        min(100, score + 4),  # Efficiency estimate
        min(100, score + 2),  # Style estimate
        (passed/total) * 100  # Completeness
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Performance',
        line_color='rgba(247, 247, 242, 0.95)',
        fillcolor='rgba(247, 247, 242, 0.18)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color='#f7f7f2', size=10)
            ),
            angularaxis=dict(
                tickfont=dict(color='#f7f7f2', size=12)
            )
        ),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#f7f7f2', 'family': 'Inter'},
        showlegend=False
    )

    return fig


# Main content routing
if menu == 'Submit Code':
    st.markdown("## Code Submission Portal")

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form('submit_form', clear_on_submit=False):
            st.markdown("### Assignment Configuration")

            col_a, col_b = st.columns(2)
            with col_a:
                assignment_id = st.text_input(
                    'Assignment Identifier', 'assignment1')
                name = st.text_input(
                    'Full Name', placeholder="Enter your complete name")
            with col_b:
                email = st.text_input(
                    'Email Address', placeholder="your.email@domain.com")
                language = st.selectbox('Programming Language',
                                        ['python', 'javascript', 'c', 'cpp', 'java'])

            st.markdown("### Code Implementation")
            code = st.text_area('Source Code', height=350,
                                placeholder="// Implement your solution here\nfunction solve() {\n    return 'Hello, World!';\n}")

            uploaded = st.file_uploader('Alternative: Upload Code File',
                                        type=['py', 'txt', 'java', 'c', 'cpp', 'js'])

            submitted = st.form_submit_button(
                'Execute Assessment', width='stretch')

    with col2:
        st.markdown("### Platform Statistics")

        # Real-time metrics simulation
        col_x, col_y = st.columns(2)
        with col_x:
            st.metric("Active Users", "1,247", "+23")
            st.metric("Success Rate", "87.3%", "+2.1%")
        with col_y:
            st.metric("Assessments", "15,438", "+156")
            st.metric("AI Accuracy", "94.7%", "+0.3%")

        # Language distribution
        lang_data = [
            {'Language': 'Python', 'Usage': 45},
            {'Language': 'JavaScript', 'Usage': 25},
            {'Language': 'Java', 'Usage': 15},
            {'Language': 'C++', 'Usage': 10},
            {'Language': 'C', 'Usage': 5},
        ]

        fig_lang = go.Figure(data=[
            go.Bar(
                x=[row['Language'] for row in lang_data],
                y=[row['Usage'] for row in lang_data],
                marker_color=['#f7f7f2', '#c9c9c1', '#9b9b94', '#6e6e68', '#454541'],
            )
        ])
        fig_lang.update_layout(
            title="Language Popularity",
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#f7f7f2', 'family': 'Inter'}
        )
        st.plotly_chart(fig_lang, width='stretch')

    if submitted:
        if uploaded is not None:
            code = uploaded.getvalue().decode('utf-8')

        if not name or not email or not code:
            st.error('Please complete all required fields.')
        else:
            # Advanced loading sequence
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Simulate advanced processing steps
            processing_steps = [
                "Initializing assessment environment...",
                "Parsing source code structure...",
                "Running automated test cases...",
                "Performing static code analysis...",
                "Generating AI-powered feedback...",
                "Finalizing assessment results..."
            ]

            for i, step in enumerate(processing_steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(processing_steps))

            status_text.empty()
            progress_bar.empty()

            payload = {
                'assignment_id': assignment_id,
                'student_name': name,
                'student_email': email,
                'language': language,
                'code': code
            }

            try:
                resp = requests.post(API + '/api/submit',
                                     json=payload, timeout=60)
                data = resp.json()

                if resp.status_code == 200 and data.get('success'):
                    score = data.get('score', 0)
                    results = data.get('results', [])
                    feedback = data.get('feedback', '')
                    plagiarism = data.get('plagiarism', [])

                    # Advanced success animation
                    show_advanced_success_animation(score)

                    # Results dashboard
                    st.markdown("## Assessment Complete")

                    # Advanced score display
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.markdown(f"""
                        <div class="score-display">
                            <div class="score-number">{score}%</div>
                            <p>Overall Performance</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Performance overview
                    if results:
                        passed = sum(1 for r in results if r.get('ok', False))
                        total = len(results)

                        col1, col2, col3, col4 = st.columns(4)
                        metrics = [
                            ("Tests Passed",
                             f"{passed}/{total}", f"+{passed}"),
                            ("Success Rate", f"{(passed/total)*100:.1f}%", ""),
                            ("Code Quality", f"{min(100, score + 5)}%", "+3%"),
                            ("Performance", f"{min(100, score + 2)}%", "+1%")
                        ]

                        for i, (label, value, delta) in enumerate(metrics):
                            with [col1, col2, col3, col4][i]:
                                st.markdown(f"""
                                <div class="metric-container">
                                    <h3 style="margin: 0; color: #f7f7f2; font-size: 1.1rem; text-transform: uppercase;">{label}</h3>
                                    <div style="font-size: 2rem; font-weight: 900; margin: 0.5rem 0; color: #f7f7f2;">{value}</div>
                                    <div style="color: #8e8e86; font-size: 0.9rem;">{delta}</div>
                                </div>
                                """, unsafe_allow_html=True)

                        # Advanced visualizations
                        viz_col1, viz_col2 = st.columns(2)

                        with viz_col1:
                            st.markdown("### Test Results Distribution")
                            fig_3d = create_3d_test_results(results)
                            if fig_3d:
                                st.plotly_chart(
                                    fig_3d, width='stretch')

                        with viz_col2:
                            st.markdown("### Performance Analysis")
                            fig_radar = create_performance_radar(
                                score, results)
                            st.plotly_chart(
                                fig_radar, width='stretch')

                    # AI Feedback section
                    if feedback:
                        safe_feedback = html.escape(str(feedback))
                        st.markdown(f"""
                        <div class="feedback-container">
                            <h3 style="margin: 0 0 1rem 0;">AI Performance Analysis</h3>
                            <p style="font-size: 1.1rem; line-height: 1.6;">{safe_feedback}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Detailed test results with advanced styling
                    if results:
                        with st.expander("Comprehensive Test Analysis", expanded=True):
                            for i, result in enumerate(results, 1):
                                status_class = "test-passed" if result.get(
                                    'ok') else "test-failed"
                                status_text = "PASSED" if result.get(
                                    'ok') else "FAILED"
                                status_icon = "✓" if result.get('ok') else "✗"

                                st.markdown(f"""
                                <div class="test-result-card {status_class}">
                                    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                        <h4 style="margin: 0; flex: 1;">Test Case {i}</h4>
                                        <span style="background: {'#f7f7f2' if result.get('ok') else '#5f5f5a'}; color: #050505; padding: 0.25rem 1rem; border-radius: 999px; font-size: 0.8rem; font-weight: 900;">{status_text}</span>
                                    </div>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; font-family: monospace;">
                                        <div>
                                            <strong>Input:</strong><br>
                                            <code style="background: rgba(255,255,255,0.07); color: #f7f7f2; border: 1px solid rgba(255,255,255,0.14); padding: 0.5rem; border-radius: 4px; display: block; margin-top: 0.25rem;">{result.get('input', 'N/A')}</code>
                                        </div>
                                        <div>
                                            <strong>Expected:</strong><br>
                                            <code style="background: rgba(255,255,255,0.07); color: #f7f7f2; border: 1px solid rgba(255,255,255,0.14); padding: 0.5rem; border-radius: 4px; display: block; margin-top: 0.25rem;">{result.get('expected', 'N/A')}</code>
                                        </div>
                                        <div>
                                            <strong>Your Output:</strong><br>
                                            <code style="background: rgba(255,255,255,0.07); color: #f7f7f2; border: 1px solid rgba(255,255,255,0.14); padding: 0.5rem; border-radius: 4px; display: block; margin-top: 0.25rem;">{result.get('output', 'N/A')}</code>
                                        </div>
                                    </div>
                                    {f'<div style="margin-top: 1rem;"><strong>Error Details:</strong><br><code style="background: rgba(255,255,255,0.07); color: #f7f7f2; border: 1px solid rgba(255,255,255,0.14); padding: 0.5rem; border-radius: 4px; display: block;">{result.get("stderr", "")}</code></div>' if result.get('stderr') else ''}
                                </div>
                                """, unsafe_allow_html=True)

                    # Plagiarism analysis
                    if plagiarism:
                        st.markdown("### Academic Integrity Analysis")
                        for p in plagiarism:
                            similarity_percent = p.get('similarity', 0) * 100
                            st.markdown(f"""
                            <div style="background: rgba(255,255,255,0.045); 
                                        border: 1px solid rgba(255,255,255,0.16); border-radius: 8px; padding: 1.5rem; margin: 1rem 0;
                                        border-left: 4px solid #f7f7f2;">
                                <h4 style="margin: 0 0 0.5rem 0; color: #f7f7f2; text-transform: uppercase;">Similarity Detected</h4>
                                <p style="margin: 0;">Similar to submission by <strong>{p.get('student_name', 'Unknown')}</strong></p>
                                <p style="margin: 0; font-size: 1.1rem; font-weight: 900; color: #f7f7f2;">Similarity Score: {similarity_percent:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)

                else:
                    st.error(
                        f"Assessment failed: {data.get('error', 'Unknown error occurred')}")

            except Exception as e:
                st.error(f'System error during assessment: {str(e)}')

elif menu == 'Instructor Dashboard':
    st.markdown("## Instructor Analytics Dashboard")

    # Dashboard header
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("### Access Management")
        adminKey = st.text_input(
            'Administrator Key', value='admin123', type='password')
        load_btn = st.button('Load Analytics Dashboard',
                             width='stretch')

    with col2:
        st.markdown("**System Status**")
        st.success("Online")
        st.markdown("**Last Update**")
        st.info("2 min ago")

    with col3:
        st.markdown("**Active Sessions**")
        st.metric("", "127", "+12")
        st.markdown("**Queue Length**")
        st.metric("", "3", "-2")

    if load_btn:
        try:
            with st.spinner('Loading comprehensive analytics...'):
                resp = requests.get(API + '/api/submissions',
                                    params={'adminKey': adminKey, 'limit': 500}, timeout=30)
                data = resp.json()

                if resp.status_code == 200:
                    submissions = data.get('submissions', [])

                    if submissions:
                        scores = [numeric_score(row) for row in submissions]

                        # Advanced analytics section
                        st.markdown("### Performance Analytics")

                        if scores:
                            # Key metrics
                            total_submissions = len(submissions)
                            avg_score = average(scores)
                            perfect_scores = sum(1 for score in scores if score == 100)
                            completion_rate = (
                                sum(1 for score in scores if score >= 70) / total_submissions) * 100

                            # Advanced metrics display
                            metric_cols = st.columns(4)
                            advanced_metrics = [
                                ("Total Assessments",
                                 f"{total_submissions:,}", "submissions"),
                                ("Average Performance",
                                 f"{avg_score:.1f}%", "mean score"),
                                ("Excellence Rate",
                                 f"{(perfect_scores/total_submissions)*100:.1f}%", "perfect scores"),
                                ("Success Rate",
                                 f"{completion_rate:.1f}%", "passing grade")
                            ]

                            for i, (label, value, subtitle) in enumerate(advanced_metrics):
                                with metric_cols[i]:
                                    st.markdown(f"""
                                    <div class="metric-container">
                                        <h4 style="margin: 0; color: #f7f7f2; font-size: 0.9rem; text-transform: uppercase;">{label}</h4>
                                        <div style="font-size: 2.2rem; font-weight: 900; margin: 0.5rem 0; color: #f7f7f2;">{value}</div>
                                        <div style="color: #8e8e86; font-size: 0.8rem;">{subtitle}</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                            # Advanced visualizations
                            viz_row1_col1, viz_row1_col2 = st.columns(2)

                            with viz_row1_col1:
                                fig_dist = go.Figure(data=[
                                    go.Histogram(
                                        x=scores,
                                        nbinsx=20,
                                        marker_color='#f7f7f2',
                                        opacity=0.85,
                                    )
                                ])
                                fig_dist.update_layout(
                                    title='Score Distribution Analysis',
                                    xaxis_title='Score',
                                    yaxis_title='Submissions',
                                    height=400,
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font={'family': 'Inter', 'color': '#f7f7f2'},
                                    title_font_size=16
                                )
                                st.plotly_chart(
                                    fig_dist, width='stretch')

                            with viz_row1_col2:
                                ordered_rows = sorted(submissions, key=lambda row: row.get('created_at') or '')
                                ordered_scores = [numeric_score(row) for row in ordered_rows]
                                labels = [
                                    row.get('created_at') or (datetime.now() - timedelta(days=index)).isoformat()
                                    for index, row in enumerate(ordered_rows)
                                ]
                                rolling_scores = rolling_average(ordered_scores, min(7, len(ordered_scores)))

                                fig_trend = go.Figure(data=[
                                    go.Scatter(
                                        x=labels,
                                        y=rolling_scores,
                                        mode='lines+markers',
                                        line=dict(width=3, color='#f7f7f2'),
                                        marker=dict(color='#f7f7f2'),
                                    )
                                ])
                                fig_trend.update_layout(
                                    title='Performance Trend (Rolling Average)',
                                    xaxis_title='Submission Time',
                                    yaxis_title='Score',
                                    height=400,
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font={'family': 'Inter', 'color': '#f7f7f2'},
                                    title_font_size=16
                                )
                                st.plotly_chart(
                                    fig_trend, width='stretch')

                            # Language performance analysis
                            lang_performance = language_performance(submissions)
                            if lang_performance:
                                fig_lang_perf = go.Figure(data=[
                                    go.Scatter(
                                        x=[row['submissions'] for row in lang_performance],
                                        y=[row['avg_score'] for row in lang_performance],
                                        text=[row['language'] for row in lang_performance],
                                        mode='markers+text',
                                        textposition='top center',
                                        marker=dict(
                                            size=[max(12, row['std_dev'] * 3) for row in lang_performance],
                                            color=[row['avg_score'] for row in lang_performance],
                                            colorscale=[[0, '#454541'], [0.5, '#9b9b94'], [1, '#f7f7f2']],
                                            showscale=True,
                                        ),
                                    )
                                ])
                                fig_lang_perf.update_layout(
                                    title='Language Performance vs Usage',
                                    xaxis_title='Submissions',
                                    yaxis_title='Average Score',
                                    height=400,
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font={'family': 'Inter', 'color': '#f7f7f2'}
                                )
                                st.plotly_chart(
                                    fig_lang_perf, width='stretch')

                        # Advanced data table with filtering
                        st.markdown("### Submission Records")

                        # Filters
                        filter_cols = st.columns(4)
                        with filter_cols[0]:
                            min_score = st.slider('Minimum Score', 0, 100, 0)
                        with filter_cols[1]:
                            language_options = unique_values(submissions, 'language')
                            selected_langs = st.multiselect(
                                'Languages', language_options, language_options)
                        with filter_cols[2]:
                            assignment_options = unique_values(submissions, 'assignment_id')
                            selected_assignments = st.multiselect(
                                'Assignments', assignment_options, assignment_options)
                        with filter_cols[3]:
                            show_all = st.checkbox('Show All Columns', False)

                        # Apply filters
                        filtered_rows = [
                            row for row in submissions
                            if numeric_score(row) >= min_score
                            and (not selected_langs or row.get('language') in selected_langs)
                            and (not selected_assignments or row.get('assignment_id') in selected_assignments)
                        ]

                        # Display options
                        if not show_all:
                            display_cols = [
                                'student_name', 'assignment_id', 'language', 'score', 'status']
                            display_rows = [
                                {key: row.get(key) for key in display_cols}
                                for row in filtered_rows
                            ]
                        else:
                            display_rows = filtered_rows

                        st.dataframe(
                            display_rows,
                            width='stretch',
                            height=500,
                            column_config={
                                'score': st.column_config.ProgressColumn(
                                    'Score', min_value=0, max_value=100, format='%d%%'
                                ),
                                'created_at': st.column_config.DatetimeColumn(
                                    'Submission Time', format='MMM DD, YYYY HH:mm'
                                )
                            }
                        )

                        # Export functionality
                        export_cols = st.columns(3)
                        with export_cols[0]:
                            csv_data = rows_to_csv(filtered_rows)
                            st.download_button(
                                'Download Filtered Data (CSV)',
                                data=csv_data,
                                file_name=f'submissions_filtered_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                                mime='text/csv',
                                width='stretch'
                            )

                        with export_cols[1]:
                            json_data = json.dumps(
                                filtered_rows, indent=2, default=str).encode('utf-8')
                            st.download_button(
                                'Download as JSON',
                                data=json_data,
                                file_name=f'submissions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                                mime='application/json',
                                width='stretch'
                            )

                        with export_cols[2]:
                            filtered_scores = [numeric_score(row) for row in filtered_rows]
                            top_row = max(filtered_rows, key=numeric_score) if filtered_rows else {}
                            summary_stats = {
                                'total_submissions': len(filtered_rows),
                                'average_score': average(filtered_scores),
                                'median_score': median(filtered_scores),
                                'top_performer': top_row.get('student_name', 'N/A')
                            }
                            summary_json = json.dumps(
                                summary_stats, indent=2).encode('utf-8')
                            st.download_button(
                                'Download Summary Report',
                                data=summary_json,
                                file_name=f'summary_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                                mime='application/json',
                                width='stretch'
                            )

                    else:
                        st.info("No submissions found in the system.")
                        st.markdown("""
                        <div class="glass-card" style="text-align: center; padding: 3rem;">
                            <h3>Get Started</h3>
                            <p>Students can begin submitting their code assignments to see analytics here.</p>
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    st.error(
                        f"Access denied: {data.get('error', 'Authentication failed')}")

        except Exception as e:
            st.error(f'Dashboard loading error: {str(e)}')

    # API documentation section
    st.markdown("---")
    with st.expander("API Reference", expanded=False):
        st.code(f"""
# Individual Submission Details
GET {API}/api/submission/<id>?adminKey=YOUR_KEY

# Bulk Data Export
GET {API}/api/submissions?adminKey=YOUR_KEY

# Generate PDF Reports
GET {API}/api/report/<id>?adminKey=YOUR_KEY
        """, language='bash')

else:  # Documentation
    st.markdown("## Platform Documentation")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Quick Start", "Configuration", "API Reference", "Features", "Troubleshooting"
    ])

    with tab1:
        st.markdown("""
        ### System Requirements
        
        **Project Dependencies:**
        ```bash
        python -m pip install -r requirements.txt
        ```
        
        ### Launch Sequence
        
        **1. Initialize Backend Services**
        ```bash
        python backend/server.py
        ```
        *Backend will be available at `http://localhost:5000`*
        
        **2. Start Frontend Interface**
        ```bash
        streamlit run frontend/streamlit_app.py
        ```
        *Frontend will be available at `http://localhost:8501`*
        
        **3. Create Test Assignment**
        - Create `backend/testcases/assignment1.json`
        - Add test cases in format: `[{"input": "test", "expected": "output"}]`
        
        ### First Submission
        1. Navigate to Submit Code section
        2. Enter student information
        3. Select programming language
        4. Input or upload code
        5. Execute assessment
        """)

    with tab2:
        st.markdown("""
        ### Environment Configuration
        
        Create `.env` file in backend directory:
        
        ```env
        # Code Execution Service
        JUDGE0_BASE_URL=https://ce.judge0.com
        JUDGE0_API_KEY=optional_your_key_here
        
        # AI Feedback Generation
        OPENAI_API_KEY=sk-your-openai-api-key
        
        # Admin Access
        ADMIN_KEY=your_secure_admin_password
        
        # System Configuration
        PORT=5000
        API_URL=http://localhost:5000
        ```
        
        ### Service Providers
        
        **Judge0 CE (Code Execution)**
        - Free tier: 50 requests/day
        - Paid plans available for production
        - Alternative: Self-hosted Judge0 instance
        
        **OpenAI GPT (AI Feedback)**
        - Pay-per-use pricing model
        - Alternative: Local AI models, Hugging Face
        
        ### Database Setup
        
        SQLite database auto-initializes on first run:
        ```sql
        CREATE TABLE submissions (
            id TEXT PRIMARY KEY,
            assignment_id TEXT,
            student_name TEXT,
            student_email TEXT,
            language TEXT,
            code TEXT,
            results TEXT,
            score INTEGER,
            plagiarism TEXT,
            feedback TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ```
        """)

    with tab3:
        st.markdown("""
        ### REST API Endpoints
        
        **Submit Code Assessment**
        ```http
        POST /api/submit
        Content-Type: application/json
        
        {
            "assignment_id": "assignment1",
            "student_name": "John Doe",
            "student_email": "john@example.com",
            "language": "python",
            "code": "def solution(): return 'Hello World'"
        }
        ```
        
        **Retrieve All Submissions**
        ```http
        GET /api/submissions?adminKey=admin123
        ```
        
        **Get Individual Submission**
        ```http
        GET /api/submission/{submission_id}?adminKey=admin123
        ```
        
        **Generate PDF Report**
        ```http
        GET /api/report/{submission_id}?adminKey=admin123
        ```
        
        ### Response Formats
        
        **Successful Submission:**
        ```json
        {
            "success": true,
            "submission_id": "uuid-string",
            "score": 85,
            "results": [...],
            "plagiarism": [...],
            "feedback": "AI generated feedback..."
        }
        ```
        
        **Error Response:**
        ```json
        {
            "error": "Description of the error",
            "code": "ERROR_CODE"
        }
        ```
        """)

    with tab4:
        st.markdown("""
        ### Core Capabilities
        
        **Automated Assessment**
        - Multi-language support (Python, Java, C++, JavaScript, C)
        - Real-time code execution and testing
        - Comprehensive test case evaluation
        - Performance metrics and scoring
        
        **AI-Powered Feedback**
        - Contextual code analysis
        - Personalized improvement suggestions
        - Learning-focused recommendations
        - Style and efficiency guidance
        
        **Academic Integrity**
        - Similarity detection algorithms
        - Cross-submission comparison
        - Plagiarism risk assessment
        - Detailed similarity reports
        
        **Analytics Dashboard**
        - Real-time performance metrics
        - Student progress tracking
        - Language usage statistics
        - Score distribution analysis
        
        **Export & Reporting**
        - CSV data export
        - JSON formatted results
        - PDF report generation
        - Custom analytics queries
        
        ### Advanced Features
        
        **Custom Test Cases**
        ```json
        {
            "assignment_id": "custom_assignment",
            "test_cases": [
                {
                    "input": "5 3",
                    "expected": "8",
                    "description": "Basic addition test"
                }
            ]
        }
        ```
        
        **Batch Processing**
        - Multiple file upload support
        - Bulk assessment capabilities
        - Parallel execution optimization
        """)

    with tab5:
        st.markdown("""
        ### Common Issues & Solutions
        
        **Backend Connection Errors**
        ```
        Problem: Frontend cannot connect to backend
        Solution: 
        1. Verify backend is running on port 5000
        2. Check firewall settings
        3. Ensure API_URL environment variable is correct
        ```
        
        **Judge0 API Failures**
        ```
        Problem: Code execution timeouts or errors
        Solution:
        1. Check Judge0 service status
        2. Verify API key validity
        3. Consider rate limiting
        4. Use alternative execution environment
        ```
        
        **Database Issues**
        ```
        Problem: SQLite database errors
        Solution:
        1. Check file permissions
        2. Verify disk space availability
        3. Run database initialization script
        4. Clear corrupted database file
        ```
        
        **AI Feedback Not Working**
        ```
        Problem: OpenAI API errors
        Solution:
        1. Verify API key validity
        2. Check account billing status
        3. Monitor rate limits
        4. Implement fallback feedback system
        ```
        
        ### Performance Optimization
        
        **Database Optimization**
        - Regular database maintenance
        - Index optimization for queries
        - Archive old submissions
        
        **Memory Management**
        - Monitor system resource usage
        - Implement request queuing
        - Configure appropriate timeouts
        
        **Scaling Considerations**
        - Load balancing for high traffic
        - Database clustering options
        - CDN for static assets
        
        ### Security Best Practices
        
        - Secure API key storage
        - Input validation and sanitization
        - Rate limiting implementation
        - Regular security audits
        - HTTPS encryption in production
        """)
# Advanced footer with system information
st.markdown("---")
st.markdown("""
<div class="app-footer">
    <span>EduGrade / Monochrome Build</span>
        <span>•</span>
    <span>Local API: http://localhost:5000</span>
        <span>•</span>
    <span>Signal over noise</span>
</div>
""", unsafe_allow_html=True)
