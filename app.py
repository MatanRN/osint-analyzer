import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium  # Updated import
import json
import os
from PIL import Image
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="OSINT Analyzer",
    page_icon="🔍",
    layout="wide",
)


# Function to load data
@st.cache_data
def load_data():
    with open("data.json", "r") as f:
        data = json.load(f)
    return data


# Load the data
data = load_data()


# Create a DataFrame for the bases
def create_bases_df(data):
    bases = []
    for base_analysis in data:
        base_info = base_analysis.get("base_info", {})
        commander_info = base_analysis.get("Commander", {})

        base = {
            "Country": base_info.get("country", "Unknown"),
            "Latitude": float(base_info.get("latitude", 0)),
            "Longitude": float(base_info.get("longitude", 0)),
            "Confidence Level": commander_info.get("confidence_score", "Unknown"),
            "Overall Assessment": commander_info.get(
                "overall_assessment", "No assessment available"
            ),
        }
        bases.append(base)
    return pd.DataFrame(bases)


# Create sidebar for navigation
st.sidebar.title("OSINT Analyzer")

# Add a home button
if st.sidebar.button("Home"):
    st.session_state.page = "home"
    st.session_state.selected_base = None

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_base" not in st.session_state:
    st.session_state.selected_base = None

# Display the home page
if st.session_state.page == "home":
    st.title("Military Bases OSINT Analysis Dashboard")

    # Create a DataFrame with bases information
    bases_df = create_bases_df(data)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Bases Analyzed", len(data))
    with col2:
        countries = bases_df["Country"].unique()
        st.metric("Countries Covered", len(countries))
    with col3:
        high_threat = len(bases_df[bases_df["Confidence Level"] == "High"])
        st.metric("High Threat Bases", high_threat)

    # Display map with all bases
    st.subheader("Military Bases Map")

    # Create a base map
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Add markers for each base
    for i, base in bases_df.iterrows():
        confidence_colors = {
            "High": "red",
            "Medium": "orange",
            "Low": "green",
            "Unknown": "gray",
        }
        confidence_level = base["Confidence Level"]
        color = confidence_colors.get(confidence_level, "blue")

        popup_html = f"""
        <b>Country:</b> {base['Country']}<br>
        <b>Confidence Level:</b> {confidence_level}<br>
        <b>Coordinates:</b> {base['Latitude']:.5f}, {base['Longitude']:.5f}
        """

        folium.Marker(
            location=[base["Latitude"], base["Longitude"]],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)

    # Display the map
    st_folium(m)  # Updated function call

    # Display a table of bases
    st.subheader("Military Bases List")

    # Display bases in a grid of cards
    cols = st.columns(3)
    for i, base_analysis in enumerate(data):
        base_info = base_analysis.get("base_info", {})
        commander_info = base_analysis.get("Commander", {})

        with cols[i % 3]:
            with st.container():
                st.markdown(
                    f"""
                <div style="padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 15px;">
                    <h3>{base_info.get('country', 'Unknown')} Base</h3>
                    <p><b>Coordinates:</b> {base_info.get('latitude', 'N/A')}, {base_info.get('longitude', 'N/A')}</p>
                    <p><b>Confidence Level:</b> {commander_info.get('confidence_score', 'Unknown')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                if st.button(f"View Details", key=f"base_{i}"):
                    st.session_state.page = "base_details"
                    st.session_state.selected_base = i
                    st.rerun()

# Display base details page
elif st.session_state.page == "base_details":
    base_index = st.session_state.selected_base

    if base_index is not None and base_index < len(data):
        base_analysis = data[base_index]
        base_info = base_analysis.get("base_info", {})
        commander_info = base_analysis.get("Commander", {})

        st.title(f"{base_info.get('country', 'Unknown')} Military Base")
        st.subheader(
            f"Coordinates: {base_info.get('latitude', 'N/A')}, {base_info.get('longitude', 'N/A')}"
        )

        # Create tabs for different sections - removing Commander Analysis tab
        tab1, tab2 = st.tabs(["Overview", "Analysts Reports"])

        with tab1:
            col1, col2 = st.columns([1, 1])

            with col1:
                # Display the map
                st.subheader("Location")
                lat = float(base_info.get("latitude", 0))
                lon = float(base_info.get("longitude", 0))

                base_map = folium.Map(location=[lat, lon], zoom_start=15)
                folium.Marker(
                    location=[lat, lon],
                    popup=f"{base_info.get('country', 'Unknown')} Base",
                    icon=folium.Icon(color="red", icon="info-sign"),
                ).add_to(base_map)

                st_folium(base_map)  # Updated function call

            with col2:
                # Display the first analyst's screenshot
                st.subheader("Initial Satellite Image (Analyst 1)")
                country = base_info.get("country", "Unknown")
                base_id_for_screenshot = f"{lat}_{lon}_{country}"
                first_analyst_screenshot_path = (
                    f"screenshots/{base_id_for_screenshot}/analyst_1.jpeg"
                )

                if os.path.exists(first_analyst_screenshot_path):
                    image = Image.open(first_analyst_screenshot_path)
                    st.image(
                        image,
                        caption="Initial satellite view by Analyst 1",
                        use_container_width=True,
                    )
                else:
                    st.error(
                        f"Screenshot for Analyst 1 not found: {first_analyst_screenshot_path}"
                    )

            # Display base metadata and key findings in a styled box
            st.markdown(
                """
            <style>
            /* Global text styles for better readability */
            .info-box h3, .info-box h4 {{
                margin-top: 0.5rem;
                margin-bottom: 1rem;
                font-weight: 600;
                color: #333;
            }}
            
            .info-box p {{
                font-size: 1rem;
                line-height: 1.5;
                color: #333;
                margin-bottom: 0.8rem;
            }}
            
            /* Container styles with improved readability */
            .info-box {{
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 24px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 24px;
                overflow: auto;
            }}
            
            .section-box {{
                background-color: white;
                border-left: 4px solid #4e8cff;
                border-radius: 6px;
                padding: 18px;
                margin-bottom: 18px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }}
            
            .asset-item, .unresolved-item, .action-item {{
                background-color: #fcfcfc;
                border-radius: 6px;
                padding: 14px;
                margin-bottom: 10px;
                font-size: 1rem;
                line-height: 1.5;
                color: #333;
                word-wrap: break-word;
            }}
            
            .asset-item {{
                background-color: #e8f4f8;
                border-left: 4px solid #4e8cff;
            }}
            
            .unresolved-item {{
                background-color: #fff4e8;
                border-left: 4px solid #ff9d4e;
            }}
            
            .action-item {{
                background-color: #e8f8f0;
                border-left: 4px solid #4eff9d;
            }}
            </style>
            <div class="info-box">
                <h3>Key Information</h3>
                <div class="section-box">
                    <h4>Overall Assessment</h4>
                    <p>{}</p>
                    <h4>Confidence Score</h4>
                    <p><span style="font-weight: bold; font-size: 1.1rem; color: {};">{}</span></p>
                </div>
            </div>
            """.format(
                    commander_info.get("overall_assessment", "No assessment available"),
                    (
                        "red"
                        if commander_info.get("confidence_score") == "High"
                        else (
                            "orange"
                            if commander_info.get("confidence_score") == "Medium"
                            else (
                                "green"
                                if commander_info.get("confidence_score") == "Low"
                                else "gray"
                            )
                        )
                    ),
                    commander_info.get("confidence_score", "Unknown"),
                ),
                unsafe_allow_html=True,
            )

            # Display key confirmed assets
            assets_html = ""
            for asset in commander_info.get("key_confirmed_asset", []):
                assets_html += f'<div class="asset-item">{asset}</div>'

            st.markdown(
                f"""
            <div class="info-box">
                <h3>Key Confirmed Assets</h3>
                {assets_html if assets_html else "<p>No assets confirmed</p>"}
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Display unresolved items
            unresolved_html = ""
            for item in commander_info.get("unresolved_item", []):
                unresolved_html += f'<div class="unresolved-item">{item}</div>'

            st.markdown(
                f"""
            <div class="info-box">
                <h3>Unresolved Items</h3>
                {unresolved_html if unresolved_html else "<p>No unresolved items</p>"}
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Display recommended actions
            actions_html = ""
            for action in commander_info.get("recommended_action", []):
                actions_html += f'<div class="action-item">{action}</div>'

            st.markdown(
                f"""
            <div class="info-box">
                <h3>Recommended Actions</h3>
                {actions_html if actions_html else "<p>No recommended actions</p>"}
            </div>
            """,
                unsafe_allow_html=True,
            )

        with tab2:
            st.subheader("Analysts' Reports")

            # Create a selectbox for choosing an analyst
            analysts = [
                key for key in base_analysis.keys() if key.startswith("Analyst")
            ]
            selected_analyst = st.selectbox("Select Analyst", analysts)

            # Display the selected analyst's report with styled containers
            if selected_analyst:
                analyst_report = base_analysis.get(selected_analyst, {})
                analyst_number_str = selected_analyst.split(" ")[
                    -1
                ]  # e.g., "Analyst 1" -> "1"

                # Construct base_id for screenshot path
                lat = base_info.get("latitude", "N/A")
                lon = base_info.get("longitude", "N/A")
                country = base_info.get("country", "Unknown")
                base_id_for_screenshot = f"{lat}_{lon}_{country}"

                analyst_screenshot_path = f"screenshots/{base_id_for_screenshot}/analyst_{analyst_number_str}.jpeg"

                # Create tabs within the analyst report for better organization
                findings_tab, analysis_tab, continue_tab, action_tab = st.tabs(
                    [
                        "Findings",
                        "Analysis",
                        "To Continue Analyzing",
                        "Recommended Action",
                    ]
                )

                with findings_tab:
                    st.markdown(
                        """
                    <style>
                    .findings-container {{
                        background-color: #f0f8ff;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 15px;
                        border: 1px solid #add8e6;
                        overflow: auto;
                    }}
                    
                    .findings-container h3 {{
                        margin-bottom: 15px;
                        color: #333;
                    }}
                    
                    .findings-container p, .findings-container li {{
                        font-size: 1rem;
                        line-height: 1.6;
                        color: #333;
                        margin-bottom: 8px;
                    }}
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        "<div class='findings-container'>", unsafe_allow_html=True
                    )
                    st.subheader("Key Findings")
                    for finding in analyst_report.get("findings", []):
                        if finding != "none":
                            st.markdown(f"✓ {finding}")
                    st.markdown("</div>", unsafe_allow_html=True)

                with analysis_tab:
                    st.markdown(
                        """
                    <style>
                    .analysis-container {{
                        background-color: #f5f5f5;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 15px;
                        border: 1px solid #e0e0e0;
                        overflow: auto;
                    }}
                    
                    .analysis-container h3 {{
                        margin-bottom: 15px;
                        color: #333;
                    }}
                    
                    .analysis-container p {{
                        font-size: 1rem;
                        line-height: 1.6;
                        color: #333;
                    }}
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        "<div class='analysis-container'>", unsafe_allow_html=True
                    )
                    st.subheader("Analysis Details")

                    # Display analyst's screenshot
                    if os.path.exists(analyst_screenshot_path):
                        analyst_image = Image.open(analyst_screenshot_path)
                        st.image(
                            analyst_image,
                            caption=f"Screenshot by {selected_analyst}",
                            use_container_width=True,
                        )
                    else:
                        st.warning(
                            f"Screenshot for {selected_analyst} not found at {analyst_screenshot_path}"
                        )

                    st.write(analyst_report.get("analysis", "No analysis available"))
                    st.markdown("</div>", unsafe_allow_html=True)

                with continue_tab:
                    st.markdown(
                        """
                    <style>
                    .continue-container {{
                        background-color: #fff8dc;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 15px;
                        border: 1px solid #f5deb3;
                        overflow: auto;
                    }}
                    
                    .continue-container h3 {{
                        margin-bottom: 15px;
                        color: #333;
                    }}
                    
                    .continue-container p {{
                        font-size: 1rem;
                        line-height: 1.6;
                        color: #333;
                    }}
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        "<div class='continue-container'>", unsafe_allow_html=True
                    )
                    st.subheader("Areas Requiring Further Investigation")
                    for item in analyst_report.get("things_to_continue_analyzing", []):
                        if item != "none":
                            st.markdown(f"🔍 {item}")
                    st.markdown("</div>", unsafe_allow_html=True)

                with action_tab:
                    st.markdown(
                        """
                    <style>
                    .action-container {{
                        background-color: #f0fff0;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 15px;
                        border: 1px solid #98fb98;
                        overflow: auto;
                    }}
                    
                    .action-container h3 {{
                        margin-bottom: 15px;
                        color: #333;
                    }}
                    
                    .action-container p {{
                        font-size: 1rem;
                        line-height: 1.6;
                        color: #333;
                    }}
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        "<div class='action-container'>", unsafe_allow_html=True
                    )
                    st.subheader("Recommended Course of Action")
                    st.write(analyst_report.get("action", "No action specified"))
                    st.markdown("</div>", unsafe_allow_html=True)
