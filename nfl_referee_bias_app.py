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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        font-size: 13.5px;
        line-height: 1.6;
        color: #002244;
        background-color: #F9FAFB;
    }

    h1 {
        font-size: 32px;
        font-weight: 600;
    }

    h2 {
        font-size: 24px;
        font-weight: 600;
    }

    h3 {
        font-size: 18px;
        font-weight: 600;
    }

    /* Sidebar hamburger always visible */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        opacity: 1 !important;
        right: 1rem;
        top: 1rem;
        z-index: 1000;
    }

    /* Sidebar style */
    [data-testid="stSidebar"] {
        background-color: #f4f6f9;
        padding: 20px;
        border-right: 1px solid #ddd;
    }

    /* Main content spacing */
    .main .block-container {
        padding-left: 3rem;
        padding-right: 2rem;
        padding-top: 2rem;
        padding-bottom: 2rem;
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
data["Bias Difference"] = pd.to_numeric(data["Away Flags Per Game"], errors="coerce") - pd.to_numeric(data["Home Flags Per Game"], errors="coerce")
data["Bias Type"] = np.where(data["Bias Difference"] > 0, "Favors Home", "Favors Away")

# Navigation state
if "active_page" not in st.session_state:
    st.session_state.active_page = "Overview"

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    if st.button("Overview"):
        st.session_state.active_page = "Overview"
    if st.button("Referee Explorer"):
        st.session_state.active_page = "Referee Explorer"
    if st.button("About Us"):
        st.session_state.active_page = "About Us"
    if st.button("Summary"):
        st.session_state.active_page = "Summary"

# ------------------ PAGE 1: OVERVIEW ------------------ #
if st.session_state.active_page == "Overview":
    st.markdown("""
        <div style="background-color:#002244;padding:25px;border-radius:10px;margin-bottom:30px;">
            <h1 style="color:#F0F2F6;text-align:center;">NFL Referee Bias Dashboard</h1>
            <p style="color:#D6E4F0;text-align:center;font-size:18px;">Analyzing trends in officiating across the 2024 NFL Season</p>
        </div>
    """, unsafe_allow_html=True)

    st.image("nfl_ref.png", use_container_width=True)

    st.markdown("""
        <h2 style='text-align: center; color: #002244;'>Do NFL Referees Show Bias Towards Home Teams?</h2>
        <p style='text-align: center; font-size: 15px; line-height: 1.5; color: #333333; max-width: 800px; margin: auto;'>
            This dashboard explores potential <strong>home-field bias</strong> among NFL referees during the 2024 season.<br>
            Data source: <a href='https://nflpenalties.com' target='_blank'>nflpenalties.com</a>.
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
    <p>
    This scatter plot compares how many penalties referees called on home vs. away teams.  
    Red dots = more calls on away teams (suggesting home bias).  
    <strong>Bill Vinovich</strong> shows one of the strongest home biases.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### Understanding the Bias Score")
    bias_explainer = pd.DataFrame({
        "Bias Type": ["Favors Away Team", "Balanced", "Favors Home Team"],
        "Bias Score Range": ["< 0", "≈ 0", "> 0"],
        "Meaning": [
            "More calls against home team",
            "Roughly equal",
            "More calls against away team"
        ]
    })
    st.dataframe(bias_explainer, use_container_width=True, hide_index=True)

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

    st.subheader("Referees Showing Home-Team Favoritism")
    home_refs = data[data["Bias Difference"] > 0]
    home_bias_chart = px.bar(
        home_refs,
        x="Name",
        y="Bias Difference",
        color_discrete_sequence=["#D50A0A"],
        title="Home-Biased Referees"
    )
    home_bias_chart.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(home_bias_chart, use_container_width=True)

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
            "Flags Per Game": [ref_stats["Home Flags Per Game"], ref_stats["Away Flags Per Game"]]
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
    **Team Members**  
    - Ryan Weiss  
    - Michael Perazzo  
    - Tyler Costin  
    Tools: Python, Streamlit, Pandas, Plotly  
    Source: [nflpenalties.com](https://nflpenalties.com)
    """)

# ------------------ PAGE 4: SUMMARY ------------------ #
elif st.session_state.active_page == "Summary":
    st.markdown("## Summary & Key Takeaways")
    st.markdown("""
    Final summary article coming soon.
    """)