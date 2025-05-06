import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from PIL import Image

st.set_page_config(page_title="NFL Referee Bias Dashboard", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        line-height: 1.6;
        color: #002244;
        background-color: #F9FAFB;
    }

    h1, h2, h3 {
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* Padding for main container */
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Force sidebar arrow (hamburger) to show */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        opacity: 1 !important;
        right: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Load and preprocess data
data = pd.read_csv("nfl_penalties_2024.csv")
data = data.iloc[1:]
data.columns = [
    "Name", "Games", "Total Penalties", "Total Yards", "Total Dismissals", "Total Flags",
    "Home Flags", "Away Flags", "Penalties Per Game", "Yards Per Game", "Dismissals Per Game",
    "Total Flags Per Game", "Home Flags Per Game", "Away Flags Per Game"
]
data["Total Penalties"] = data["Total Penalties"].astype(int)
data["Total Yards"] = data["Total Yards"].astype(int)
data["Bias Difference"] = data["Away Flags Per Game"].astype(float) - data["Home Flags Per Game"].astype(float)
data["Bias Type"] = np.where(data["Bias Difference"] > 0, "Favors Home", "Favors Away")

# Page state
if "active_page" not in st.session_state:
    st.session_state.active_page = "Overview"

# Sidebar Styling
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #F0F2F6;
            padding: 20px;
        }
        .sidebar-title {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #002244;
        }
        .sidebar-sub {
            font-size: 14px;
            color: #444444;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .sidebar-footer {
            font-size: 12px;
            color: #888888;
            margin-top: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    # Optional: Add a logo at the top
    # st.image("logo.png", width=180)

    st.markdown('<div class="sidebar-title">NFL Referee Bias</div>', unsafe_allow_html=True)
    
    if st.button("Overview"):
        st.session_state.active_page = "Overview"
    if st.button("Referee Explorer"):
        st.session_state.active_page = "Referee Explorer"
    if st.button("About Us"):
        st.session_state.active_page = "About Us"
    if st.button("Summary"):
        st.session_state.active_page = "Summary"

    st.markdown("""
        <div class="sidebar-sub">
            This dashboard uses real NFL penalty data to explore referee bias trends.  
            Built with Python, Streamlit, and Plotly.
        </div>
        <div class="sidebar-footer">
            © 2024 Ryan Weiss, Michael Perazzo & Tyler Costin
        </div>
    """, unsafe_allow_html=True)

# ------------------ PAGE 1: OVERVIEW ------------------ #
if st.session_state.active_page == "Overview":
    st.markdown("""
        <div style="background-color:#002244;padding:25px;border-radius:10px;margin-bottom:30px;">
            <h1 style="color:#F0F2F6;text-align:center;font-size:45px;">NFL Referee Bias Dashboard</h1>
            <p style="color:#D6E4F0;text-align:center;font-size:20px;">Analyzing trends in officiating across the 2024 NFL Season</p>
        </div>
    """, unsafe_allow_html=True)

    nfl_image = Image.open("nfl_ref.png")
    st.image(nfl_image, use_container_width=True)

    st.markdown("""
        <h2 style='text-align: center; color: #002244;'>Do NFL Referees Show Bias Towards Home Teams?</h2>
        <p style='text-align: center; font-size: 18px; line-height: 1.6; color: #333333; max-width: 800px; margin: auto;'>
            This dashboard explores potential <strong>home-field bias</strong> among NFL referees during the 2024 season.<br>
            We focus on whether referees favored <strong>home teams</strong> by calling more penalties against away teams.<br>
            All of this data was taken from <a href='https://nflpenalties.com' target='_blank'>nflpenalties.com</a>.
        </p>
    """, unsafe_allow_html=True)

    if st.checkbox("Show Raw Data Table"):
        st.dataframe(data)

    st.subheader("Penalty Bias: Home vs Away")
    scatter_fig = px.scatter(
        data,
        text="Name",
        x="Home Flags Per Game",
        y="Away Flags Per Game",
        color="Bias Type",
        color_discrete_map={"Favors Home": "#D50A0A", "Favors Away": "#013369"},
        title="Referee Penalty Bias: Home vs Away Flags Per Game"
    )
    scatter_fig.add_shape(
        type="line",
        x0=data["Home Flags Per Game"].min(),
        y0=data["Home Flags Per Game"].min(),
        x1=data["Home Flags Per Game"].max(),
        y1=data["Home Flags Per Game"].max(),
        line=dict(color="gray", dash="dash")
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    st.markdown("""
    <p style='font-size:16px;'>
    This scatter plot compares the number of penalties referees called per game on home teams versus away teams.  
    Each dot represents one referee. Red dots indicate referees who called more penalties on away teams (suggesting home-team bias), while blue dots indicate the opposite.  
    <em>Most referees fall slightly above the diagonal line, indicating a subtle trend toward penalizing away teams more often.</em><br><br>
    For example, <strong>Bill Vinovich</strong> stands out as one of the most home-biased referees, consistently calling over 1.5 more penalties per game on away teams than home teams.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### Understanding the Bias Score")
    bias_explainer = pd.DataFrame({
        "Bias Type": ["Favors Away Team", "Balanced", "Favors Home Team"],
        "Bias Score Range": ["< 0", "≈ 0", "> 0"],
        "Meaning": [
            "More calls against home team",
            "Roughly equal calls on both",
            "More calls against away team"
        ]
    })
    st.dataframe(bias_explainer, use_container_width=True, hide_index=True)

    st.markdown("""
    <p style='font-size:15px;'>
    A <strong>Bias Score</strong> is calculated as: Away Penalties per Game − Home Penalties per Game.  
    A positive value means more penalties were called on away teams, suggesting possible home-team bias. A negative score means more penalties were called on home teams.
    </p>
    """, unsafe_allow_html=True)

    st.subheader("Overall Referee Bias (Away vs Home)")
    bias_chart = px.bar(
        data.sort_values("Bias Difference"),
        x="Name",
        y="Bias Difference",
        color_discrete_sequence=["#013369"],
        title="Bias Difference Per Game: Away - Home"
    )
    bias_chart.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(bias_chart, use_container_width=True)

    st.markdown("""
    <p style='font-size:16px;'>
    This bar chart shows the average difference in penalties called per game on away teams versus home teams for each referee.  
    A higher positive value indicates a tendency to favor the home team.  
    <em>Several referees show a noticeable positive bias, while others are more balanced or even favor the away team slightly.</em>
    </p>
    """, unsafe_allow_html=True)

    st.subheader("Referees Showing Home-Team Favoritism")
    home_refs = data[data["Bias Difference"] > 0]
    home_bias_chart = px.bar(
        home_refs,
        x="Name",
        y="Bias Difference",
        color_discrete_sequence=["#D50A0A"],
        title="Home-Biased Referees: More Penalties on Away Teams"
    )
    home_bias_chart.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(home_bias_chart, use_container_width=True)

    st.markdown("""
    <p style='font-size:16px;'>
    This chart focuses only on referees who showed home-team favoritism—those who called more penalties against away teams.  
    <em>These referees may be contributing to a subtle home-field advantage, intentionally or not.</em>  
    This helps highlight which individuals stood out most in terms of consistent bias.
    </p>
    """, unsafe_allow_html=True)

# ------------------ PAGE 2: REFEREE EXPLORER ------------------ #
elif st.session_state.active_page == "Referee Explorer":
    st.subheader("Explore a Specific Referee")
    selected_ref = st.selectbox("Select a Referee", data["Name"])
    ref_stats = data[data["Name"] == selected_ref].squeeze()

    st.markdown(f"### Stats for {selected_ref}")
    stats_df = pd.DataFrame([{
        "Games": ref_stats["Games"],
        "Penalties": ref_stats["Total Penalties"],
        "Yards": ref_stats["Total Yards"],
        "Dismissals": ref_stats["Total Dismissals"],
        "Home Flags/Game": ref_stats["Home Flags Per Game"],
        "Away Flags/Game": ref_stats["Away Flags Per Game"],
        "Bias Score": round(ref_stats["Bias Difference"], 2)
    }])
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

    img_col, vis_col = st.columns([1, 2])

    image_folder = "referee_images"
    image_filename = selected_ref.lower().replace(" ", "") + ".png"
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, image_folder, image_filename)

    with img_col:
        if os.path.exists(image_path):
            st.image(Image.open(image_path), width=300, caption=selected_ref)
        else:
            st.warning("No image found for selected referee.")

    with vis_col:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=float(ref_stats["Bias Difference"]),
            delta={'reference': 0, 'increasing': {'color': "red"}, 'decreasing': {'color': "blue"}},
            gauge={
                'axis': {'range': [-2, 2]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-2, -0.5], 'color': "#013369"},
                    {'range': [-0.5, 0.5], 'color': "#CCCCCC"},
                    {'range': [0.5, 2], 'color': "#D50A0A"},
                ],
            },
            title={'text': "Bias Score (Away - Home)"}
        ))
        st.plotly_chart(fig_gauge, use_container_width=False)

        bar_data = pd.DataFrame({
            "Type": ["Home", "Away"],
            "Flags Per Game": [float(ref_stats["Home Flags Per Game"]), float(ref_stats["Away Flags Per Game"])]
        })
        ref_bar = px.bar(
            bar_data,
            x="Type",
            y="Flags Per Game",
            color="Type",
            color_discrete_map={"Home": "#013369", "Away": "#D50A0A"},
            title="Penalties Per Game"
        )
        st.plotly_chart(ref_bar, use_container_width=False)

# ------------------ PAGE 3: ABOUT US ------------------ #
elif st.session_state.active_page == "About Us":
    st.markdown("## About Us")
    st.markdown("""
    This dashboard was created as part of our class project to explore whether NFL referees show bias when officiating games.  
    Our goal was to analyze real penalty data from the 2024 NFL season and present it in a clear and engaging way.

    **Team Members**  
    - Ryan Weiss  
    - Michael Perazzo  
    - Tyler Costin

    We used Python, Pandas, Plotly, and Streamlit to build this app, and we sourced the penalty data from [nflpenalties.com](https://nflpenalties.com).
    """)

# ------------------ PAGE 4: SUMMARY ------------------ #
elif st.session_state.active_page == "Summary":
    st.markdown("## Summary & Key Takeaways")
    st.markdown("""
    Enter Article Here...
    """)