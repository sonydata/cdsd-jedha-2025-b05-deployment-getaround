# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Car Rental Delay Analysis",
    #page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        text-align: center;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .recommendation-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATA LOADING ==========
@st.cache_data(show_spinner=False)
def load_data():
    """Load and preprocess the rental data"""
    possible_paths = [
        "get_around_delay_analysis.xlsx",
        "get_around_delay_analysis.csv", 
        "/mnt/data/get_around_delay_analysis.xlsx",
        "/mnt/data/get_around_delay_analysis.csv"
    ]
    
    df = None
    for path in possible_paths:
        if Path(path).exists():
            try:
                if path.endswith('.xlsx'):
                    df = pd.read_excel(path)
                else:
                    df = pd.read_csv(path)
                break
            except Exception as e:
                continue
    
    if df is None:
        st.error("❌ Data file not found. Please ensure 'get_around_delay_analysis.xlsx' or 'get_around_delay_analysis.csv' is available.")
        st.stop()
    
    # Clean the data
    df = df.drop(columns=[c for c in df.columns if c.lower().startswith("unnamed")], errors="ignore")
    df["has_previous_rental"] = df["time_delta_with_previous_rental_in_minutes"].notnull()
    df["clean_delay"] = df["delay_at_checkout_in_minutes"].clip(-720, 720)
    
    return df

# ========== ANALYSIS FUNCTIONS ==========
def calculate_metrics(df, threshold_minutes, scope="all"):
    """Calculate key metrics for threshold analysis"""
    
    # Filter by scope
    if scope == "connect":
        df_filtered = df[df["checkin_type"].str.lower() == "connect"].copy()
    else:
        df_filtered = df.copy()
    
    df_with_prev = df_filtered[df_filtered["has_previous_rental"]].copy()
    
    if len(df_with_prev) == 0:
        return {
            "total_rentals": len(df_filtered),
            "rentals_with_previous": 0,
            "blocked_rentals": 0,
            "blocked_percentage": 0.0,
            "current_problems": 0,
            "problems_solved": 0,
            "solve_efficiency": 0.0,
            "revenue_impact": 0.0
        }
    
    # Join with previous rental data
    prev_rental_data = df[["rental_id", "delay_at_checkout_in_minutes"]].rename(
        columns={"rental_id": "previous_ended_rental_id", 
                "delay_at_checkout_in_minutes": "previous_delay"}
    )
    
    df_with_prev = df_with_prev.merge(prev_rental_data, on="previous_ended_rental_id", how="left")
    
    # Calculate key metrics
    df_with_prev["would_be_blocked"] = df_with_prev["time_delta_with_previous_rental_in_minutes"] < threshold_minutes
    df_with_prev["previous_delay_clean"] = df_with_prev["previous_delay"].clip(-720, 720)
    df_with_prev["causes_problem"] = (
        df_with_prev["previous_delay"].notnull() & 
        (df_with_prev["previous_delay_clean"] > df_with_prev["time_delta_with_previous_rental_in_minutes"])
    )
    df_with_prev["problem_solved"] = df_with_prev["causes_problem"] & df_with_prev["would_be_blocked"]
    
    # Final calculations
    total_rentals = len(df_filtered)
    rentals_with_previous = len(df_with_prev)
    blocked_rentals = int(df_with_prev["would_be_blocked"].sum())
    blocked_percentage = (blocked_rentals / rentals_with_previous) * 100 if rentals_with_previous > 0 else 0
    current_problems = int(df_with_prev["causes_problem"].sum())
    problems_solved = int(df_with_prev["problem_solved"].sum())
    solve_efficiency = (problems_solved / blocked_rentals * 100) if blocked_rentals > 0 else 0
    revenue_impact = (blocked_rentals / total_rentals) * 100 if total_rentals > 0 else 0
    
    return {
        "total_rentals": total_rentals,
        "rentals_with_previous": rentals_with_previous,
        "blocked_rentals": blocked_rentals,
        "blocked_percentage": blocked_percentage,
        "current_problems": current_problems,
        "problems_solved": problems_solved,
        "solve_efficiency": solve_efficiency,
        "availability_impact": revenue_impact  # More accurate naming
    }

def create_threshold_analysis(df, thresholds, scope="all"):
    """Create threshold analysis data"""
    results = []
    for threshold in thresholds:
        metrics = calculate_metrics(df, threshold, scope)
        results.append({"threshold": threshold, **metrics})
    return pd.DataFrame(results)

# ========== LOAD DATA ==========
df = load_data()

# ========== MAIN DASHBOARD ==========
st.markdown('<h1 class="main-header">Car Rental Delay Analysis</h1>', unsafe_allow_html=True)

# Sidebar with controls
with st.sidebar:
    # Logo placeholder - you can add your logo here
    # st.image("logo.png", width=200)  # Uncomment and add your logo file
    
    st.markdown("## Analysis Controls")
    
    selected = option_menu(
        "Analysis Focus",
        ["Overview & Problems", "Threshold & Scope"],
        icons=["graph-up", "sliders"],  # More professional icons
        menu_icon="house-gear",
        default_index=0,
    )
    
    if selected == "Threshold & Scope":
        st.markdown("### Settings")
        threshold = st.slider("Threshold (minutes)", 0, 300, 90, step=30,
                             help="Minimum delay between consecutive rentals")
        scope = st.selectbox("Implementation Scope", ["all", "connect"],
                            format_func=lambda x: "All Cars" if x == "all" else "Connect Cars Only")
    
    st.markdown("---")
    st.markdown("### Dataset Summary")
    st.info(f"""
    **Total Rentals:** {len(df):,}
    **Connect Rentals:** {len(df[df['checkin_type'].str.lower() == 'connect']):,}
    **Cancelled Rentals:** {len(df[df['state'] == 'canceled']):,}
    **With Previous Rental:** {df['has_previous_rental'].sum():,}
    """)

# ========== PAGE 1: OVERVIEW & PROBLEMS ==========
if selected == "Overview & Problems":
    st.title("Understanding the Delay Problem")
    
    # Dataset Overview
    st.markdown('<div class="section-header">Dataset Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rentals", f"{len(df):,}",
                 help="Complete dataset of all rental transactions")
    with col2:
        st.metric("Connect Rentals", f"{len(df[df['checkin_type'].str.lower() == 'connect']):,}",
                 help="Rentals using Connect technology (keyless entry via smartphone)")
    with col3:
        st.metric("Mobile Rentals", f"{len(df[df['checkin_type'].str.lower() == 'mobile']):,}",
                 help="Traditional rentals using mobile app (owner hands over keys)")
    with col4:
        st.metric("With Previous Rental", f"{df['has_previous_rental'].sum():,}",
                 help="Rentals where the same car had another rental within 12 hours before - these can be analyzed for delay impact")
    
    # Rental type distribution
    col1, col2 = st.columns(2)
    
    with col1:
        checkin_counts = df["checkin_type"].value_counts()
        fig_checkin = px.pie(
            values=checkin_counts.values, 
            names=checkin_counts.index,
            title="Distribution by Checkin Type",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_checkin, use_container_width=True)
    
    with col2:
        state_counts = df["state"].value_counts()
        fig_state = px.pie(
            values=state_counts.values, 
            names=state_counts.index,
            title="Distribution by Rental State",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_state, use_container_width=True)
    
    # Key Problem Analysis
    st.markdown('<div class="section-header">Current Problem Scope</div>', unsafe_allow_html=True)
    
    # Calculate current problems
    df_problems = df[df["has_previous_rental"]].copy()
    prev_rental_data = df[["rental_id", "delay_at_checkout_in_minutes"]].rename(
        columns={"rental_id": "previous_ended_rental_id", 
                "delay_at_checkout_in_minutes": "previous_delay"}
    )
    df_problems = df_problems.merge(prev_rental_data, on="previous_ended_rental_id", how="left")
    df_problems["previous_delay_clean"] = df_problems["previous_delay"].clip(-720, 720)
    df_problems["causes_problem"] = (
        df_problems["previous_delay"].notnull() & 
        (df_problems["previous_delay_clean"] > df_problems["time_delta_with_previous_rental_in_minutes"])
    )
    df_problems["wait_time"] = np.maximum(
        0, 
        df_problems["previous_delay_clean"] - df_problems["time_delta_with_previous_rental_in_minutes"]
    ).fillna(0)
    
    problem_cases = df_problems[df_problems["causes_problem"]]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Problem Cases", f"{len(problem_cases):,}",
                 help="Formula: previous_rental_delay > gap_to_current_rental AND previous_rental_delay > 0. Uses previous_ended_rental_id to link actual delay data.")
    with col2:
        problem_rate = (len(problem_cases) / len(df_problems)) * 100 if len(df_problems) > 0 else 0
        st.metric("Problem Rate", f"{problem_rate:.1f}%",
                 help="Calculation: problem_cases / rentals_with_previous_rental * 100")
    with col3:
        avg_wait = problem_cases["wait_time"].mean() if len(problem_cases) > 0 else 0
        st.metric("Avg Wait Time", f"{avg_wait:.1f} min",
                 help="Formula: max(0, previous_rental_delay - gap_to_current_rental). Average wait time when problems occur.")
    with col4:
        delay_cancels = problem_cases[problem_cases["state"] == "canceled"]
        st.metric("Resulting Cancellations", f"{len(delay_cancels):,}",
                 help="Cancelled rentals that were also problem cases (delay caused customer to cancel)")
    
    st.markdown("""
    <div class="insight-box">
    <strong>The Problem:</strong> Late returns create customer wait times and cancellations.
    </div>
    """, unsafe_allow_html=True)
    
    # Direct answer to PM's questions
    st.markdown('<div class="section-header">How Often Are Drivers Late & Impact on Next Driver</div>', unsafe_allow_html=True)
    
    # Calculate late return frequency and impact
    df_late_analysis = df[df["has_previous_rental"]].copy()
    
    # Join with previous rental delay data
    prev_rental_data = df[["rental_id", "delay_at_checkout_in_minutes"]].rename(
        columns={"rental_id": "previous_ended_rental_id", 
                "delay_at_checkout_in_minutes": "previous_delay"}
    )
    df_late_analysis = df_late_analysis.merge(prev_rental_data, on="previous_ended_rental_id", how="left")
    
    # Calculate late return frequency
    df_late_analysis["previous_delay_clean"] = df_late_analysis["previous_delay"].clip(-720, 720)
    df_late_analysis["previous_was_late"] = (
        df_late_analysis["previous_delay"].notnull() & 
        (df_late_analysis["previous_delay_clean"] > 0)
    )
    
    # Calculate impact on next driver
    df_late_analysis["causes_problem"] = (
        df_late_analysis["previous_delay"].notnull() & 
        (df_late_analysis["previous_delay_clean"] > df_late_analysis["time_delta_with_previous_rental_in_minutes"])
    )
    df_late_analysis["wait_time"] = np.maximum(
        0, 
        df_late_analysis["previous_delay_clean"] - df_late_analysis["time_delta_with_previous_rental_in_minutes"]
    ).fillna(0)
    
    late_returns = df_late_analysis[df_late_analysis["previous_was_late"]]
    impacted_next_drivers = df_late_analysis[df_late_analysis["causes_problem"]]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Late Return Frequency")
        total_with_delay_data = df_late_analysis[df_late_analysis["previous_delay"].notnull()]
        late_frequency = (len(late_returns) / len(total_with_delay_data)) * 100 if len(total_with_delay_data) > 0 else 0
        
        st.metric("Late Returns", f"{len(late_returns):,}")
        st.metric("Late Return Rate", f"{late_frequency:.1f}%",
                 help="Percentage of returns that are late (delay > 0 minutes)")
        
        # Late return severity
        if len(late_returns) > 0:
            avg_late_delay = late_returns["previous_delay_clean"].mean()
            st.metric("Average Late Delay", f"{avg_late_delay:.1f} min")
    
    with col2:
        st.markdown("#### Impact on Next Driver")
        impact_rate = (len(impacted_next_drivers) / len(df_late_analysis)) * 100 if len(df_late_analysis) > 0 else 0
        
        st.metric("Next Drivers Impacted", f"{len(impacted_next_drivers):,}")
        st.metric("Impact Rate", f"{impact_rate:.1f}%",
                 help="Percentage of consecutive rentals where late return causes waiting")
        
        if len(impacted_next_drivers) > 0:
            avg_wait = impacted_next_drivers["wait_time"].mean()
            st.metric("Average Wait Time", f"{avg_wait:.1f} min",
                     help="Average additional wait time when impacted")
    
    # Visual analysis of the relationship
    col1, col2 = st.columns(2)
    
    with col1:
        # Late return distribution
        if len(late_returns) > 0:
            late_delays = late_returns["previous_delay_clean"]
            late_filtered = late_delays[late_delays <= 300]  # Cap at 5 hours for visualization
            
            fig_late = px.histogram(
                late_filtered, 
                nbins=20,
                title="Distribution of Late Return Delays",
                labels={"value": "Delay (minutes)", "count": "Number of Late Returns"}
            )
            st.plotly_chart(fig_late, use_container_width=True)
    
    with col2:
        # Wait time impact distribution
        if len(impacted_next_drivers) > 0:
            wait_times = impacted_next_drivers[impacted_next_drivers["wait_time"] > 0]["wait_time"]
            
            fig_wait = px.histogram(
                wait_times, 
                nbins=20,
                title="Wait Time Distribution for Impacted Next Drivers",
                labels={"value": "Wait Time (minutes)", "count": "Number of Impacted Drivers"}
            )
            st.plotly_chart(fig_wait, use_container_width=True)
    
    # Key insight summary
    late_to_impact_ratio = (len(impacted_next_drivers) / len(late_returns)) * 100 if len(late_returns) > 0 else 0
    
    st.markdown(f"""
    <div class="insight-box">
    <strong>Key Insights:</strong>
    • {late_frequency:.1f}% of returns are late
    • {impact_rate:.1f}% of consecutive rentals are impacted
    • Average wait time: {avg_wait:.1f} minutes when problems occur
    </div>
    """, unsafe_allow_html=True)
    
    # Visual analysis
    st.markdown('<div class="section-header">Delay Patterns</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Return status distribution
        df_with_delay_data = df[df["delay_at_checkout_in_minutes"].notnull()].copy()
        df_with_delay_data["delay_status"] = df_with_delay_data["delay_at_checkout_in_minutes"].apply(
            lambda x: "Early Return" if x < 0 else "On Time" if x == 0 else "Late Return"
        )
        
        delay_counts = df_with_delay_data["delay_status"].value_counts()
        fig_status = px.pie(
            values=delay_counts.values, 
            names=delay_counts.index,
            title="Return Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Delay distribution
        delay_filtered = df_with_delay_data[df_with_delay_data["delay_at_checkout_in_minutes"].between(-60, 240)]
        fig_hist = px.histogram(
            delay_filtered, 
            x="delay_at_checkout_in_minutes",
            nbins=30,
            title="Delay Distribution",
            labels={"delay_at_checkout_in_minutes": "Delay (minutes)", "count": "Rentals"}
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="On Time")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Gap analysis
    st.markdown('<div class="section-header">Time Gaps Between Rentals</div>', unsafe_allow_html=True)
    
    gap_data = df[df["has_previous_rental"]]
    gap_filtered = gap_data[gap_data["time_delta_with_previous_rental_in_minutes"].between(0, 480)]
    
    fig_gap = px.histogram(
        gap_filtered, 
        x="time_delta_with_previous_rental_in_minutes",
        nbins=20,
        title="Gap Distribution Between Consecutive Rentals",
        labels={"time_delta_with_previous_rental_in_minutes": "Gap (minutes)", "count": "Rentals"}
    )
    st.plotly_chart(fig_gap, use_container_width=True)
    
    # Cancellation analysis
    st.markdown('<div class="section-header">Cancellation Impact</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        total_cancels_all = (df["state"] == "canceled").sum()
        delay_related_cancels = (df_problems["state"] == "canceled") & df_problems["causes_problem"]
        delay_cancel_count = delay_related_cancels.sum()
        
        st.metric("Total Cancellations", f"{total_cancels_all:,}",
                 help="All cancelled rentals in the dataset (state = 'canceled')")
        st.metric("Due to Previous Delays", f"{delay_cancel_count:,}",
                 help="Cancelled rentals that were also problem cases (previous rental caused delay)")
        if total_cancels_all > 0:
            delay_cancel_rate = (delay_cancel_count / total_cancels_all * 100)
            st.metric("% Due to Delays", f"{delay_cancel_rate:.1f}%",
                     help="Calculation: delay_related_cancellations / total_cancellations * 100")
    
    with col2:
        # Cancellation by checkin type
        cancellation_by_type = df.groupby(['checkin_type', 'state']).size().unstack(fill_value=0)
        if 'canceled' in cancellation_by_type.columns:
            cancel_rates = (cancellation_by_type['canceled'] / cancellation_by_type.sum(axis=1) * 100).round(1)
            fig_cancel = px.bar(
                x=cancel_rates.index, 
                y=cancel_rates.values,
                title="Cancellation Rate by Type",
                labels={"x": "Checkin Type", "y": "Cancellation Rate (%)"}
            )
            st.plotly_chart(fig_cancel, use_container_width=True)

# ========== PAGE 2: THRESHOLD & SCOPE ANALYSIS ==========
elif selected == "Threshold & Scope":
    st.title("Threshold & Scope Decision")
    
    st.markdown("""
    <div class="insight-box">
    <strong>Availability Impact:</strong> Percentage of rental slots blocked due to insufficient gap between rentals.
    </div>
    """, unsafe_allow_html=True)
    
    # Current impact
    current_metrics = calculate_metrics(df, threshold, scope)
    
    st.markdown('<div class="section-header">Impact at Current Settings</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: #e74c3c;">{current_metrics['blocked_rentals']:,}</h3>
        <p>Blocked Rentals</p>
        <small>Gap < {threshold} min</small>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Formula: time_delta_with_previous_rental < threshold")
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: #f39c12;">{current_metrics['blocked_percentage']:.1f}%</h3>
        <p>Blocked Rate</p>
        <small>Of consecutive rentals</small>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Calculation: blocked_rentals / rentals_with_previous * 100")
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: #27ae60;">{current_metrics['problems_solved']:,}</h3>
        <p>Problems Solved</p>
        <small>Waiting eliminated</small>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Logic: current_problems AND would_be_blocked")
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: #9b59b6;">{current_metrics['availability_impact']:.1f}%</h3>
        <p>Availability Impact</p>
        <small>% of rental slots blocked</small>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Formula: blocked_rentals / total_rentals * 100")
    
    # Threshold analysis
    st.markdown('<div class="section-header">Threshold Analysis</div>', unsafe_allow_html=True)
    
    thresholds = list(range(0, 301, 30))
    threshold_data = create_threshold_analysis(df, thresholds, scope)
    
    # Create dual-axis chart
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Problems Solved vs Blocked Rentals", "Efficiency vs Availability Impact"),
        specs=[[{"secondary_y": True}, {"secondary_y": True}]]
    )
    
    # Left chart: Problems vs Blocked
    fig.add_trace(
        go.Scatter(x=threshold_data["threshold"], y=threshold_data["problems_solved"],
                  mode="lines+markers", name="Problems Solved", line=dict(color="green")),
        row=1, col=1, secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=threshold_data["threshold"], y=threshold_data["blocked_rentals"],
                  mode="lines+markers", name="Blocked Rentals", line=dict(color="red")),
        row=1, col=1, secondary_y=True
    )
    
    # Right chart: Efficiency vs Availability Impact
    fig.add_trace(
        go.Scatter(x=threshold_data["threshold"], y=threshold_data["solve_efficiency"],
                  mode="lines+markers", name="Efficiency (%)", line=dict(color="blue")),
        row=1, col=2, secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=threshold_data["threshold"], y=threshold_data["availability_impact"],
                  mode="lines+markers", name="Availability Impact (%)", line=dict(color="orange")),
        row=1, col=2, secondary_y=True
    )
    
    # Add current threshold line
    fig.add_vline(x=threshold, line_dash="dash", line_color="red", 
                 annotation_text=f"Current: {threshold}min", row=1, col=1)
    fig.add_vline(x=threshold, line_dash="dash", line_color="red", 
                 annotation_text=f"Current: {threshold}min", row=1, col=2)
    
    fig.update_layout(height=400, showlegend=True)
    fig.update_xaxes(title_text="Threshold (minutes)")
    fig.update_yaxes(title_text="Count", secondary_y=False, row=1, col=1)
    fig.update_yaxes(title_text="Count", secondary_y=True, row=1, col=1)
    fig.update_yaxes(title_text="Percentage (%)", secondary_y=False, row=1, col=2)
    fig.update_yaxes(title_text="Percentage (%)", secondary_y=True, row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Scope comparison
    st.markdown('<div class="section-header">Scope Comparison: All Cars vs Connect Only</div>', unsafe_allow_html=True)
    
    all_metrics = calculate_metrics(df, threshold, "all")
    connect_metrics = calculate_metrics(df, threshold, "connect")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### All Cars")
        st.markdown(f"""
        **Problems Solved:** {all_metrics['problems_solved']:,}  
        **Blocked Rentals:** {all_metrics['blocked_rentals']:,} ({all_metrics['blocked_percentage']:.1f}%)  
        **Efficiency:** {all_metrics['solve_efficiency']:.1f}%  
        **Availability Impact:** {all_metrics['availability_impact']:.1f}%
        """)
    
    with col2:
        st.markdown("### Connect Cars Only")
        st.markdown(f"""
        **Problems Solved:** {connect_metrics['problems_solved']:,}  
        **Blocked Rentals:** {connect_metrics['blocked_rentals']:,} ({connect_metrics['blocked_percentage']:.1f}%)  
        **Efficiency:** {connect_metrics['solve_efficiency']:.1f}%  
        **Availability Impact:** {connect_metrics['availability_impact']:.1f}%
        """)
    
    # Scope comparison chart
    all_data = create_threshold_analysis(df, thresholds, "all")
    connect_data = create_threshold_analysis(df, thresholds, "connect")
    
    fig_scope = go.Figure()
    
    # Calculate percentage of problems solved for fair comparison
    all_data["problems_solved_percent"] = (all_data["problems_solved"] / all_data["current_problems"].iloc[0] * 100).fillna(0)
    connect_data["problems_solved_percent"] = (connect_data["problems_solved"] / connect_data["current_problems"].iloc[0] * 100).fillna(0)
    
    fig_scope.add_trace(go.Scatter(x=all_data["threshold"], y=all_data["problems_solved_percent"],
                                  mode="lines+markers", name="All Cars - % Problems Solved"))
    fig_scope.add_trace(go.Scatter(x=connect_data["threshold"], y=connect_data["problems_solved_percent"],
                                  mode="lines+markers", name="Connect Only - % Problems Solved"))
    fig_scope.add_vline(x=threshold, line_dash="dash", line_color="red", 
                       annotation_text=f"Current: {threshold}min")
    fig_scope.update_layout(title="Percentage of Problems Solved by Scope", 
                           xaxis_title="Threshold (minutes)", 
                           yaxis_title="% of Problems Solved")
    st.plotly_chart(fig_scope, use_container_width=True)
    
    # Recommendations
    st.markdown('<div class="section-header">Business Decision Framework</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-box">
    <strong>Key Trade-off:</strong> Customer experience improvements vs. availability reduction
    </div>
    """, unsafe_allow_html=True)
    
    # Show current trade-offs
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Benefits**")
        st.write(f"• Eliminates {current_metrics['problems_solved']:,} wait situations")
        st.write(f"• {current_metrics['solve_efficiency']:.1f}% efficiency rate")
        st.write(f"• Reduces customer complaints")
    
    with col2:
        st.markdown("**Costs**")
        st.write(f"• Blocks {current_metrics['blocked_rentals']:,} booking opportunities")
        st.write(f"• {current_metrics['availability_impact']:.1f}% availability reduction")
        st.write(f"• Operational implementation required")
    
    # Strategic recommendations with 120min suggestion
    st.markdown("### Recommended Strategy")
    
    # Get 120min metrics for recommendation
    metrics_120 = calculate_metrics(df, 120, scope)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="recommendation-box">
        <h3>Threshold: 120 minutes</h3>
        <p>Balanced approach for customer experience</p>
        <small>Solves {metrics_120['problems_solved']:,} problems, blocks {metrics_120['availability_impact']:.1f}% availability</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Scope recommendation logic
        all_120 = calculate_metrics(df, 120, "all")
        connect_120 = calculate_metrics(df, 120, "connect")
        
        if connect_120['solve_efficiency'] > all_120['solve_efficiency'] and connect_120['problems_solved'] >= all_120['problems_solved'] * 0.7:
            recommended_scope = "Connect Only"
        else:
            recommended_scope = "All Cars"
        
        st.markdown(f"""
        <div class="recommendation-box">
        <h3>Scope: {recommended_scope}</h3>
        <p>Optimal efficiency and coverage</p>
        <small>Based on efficiency and problem-solving balance</small>
        </div>
        """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
<p><strong>Car Rental Delay Analysis</strong> - Supporting threshold and scope decisions</p>
</div>
""", unsafe_allow_html=True)