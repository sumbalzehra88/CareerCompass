import streamlit as st

st.set_page_config(page_title="CareerCompass", layout="wide")

# --- CSS styling ---
st.markdown("""
    <style>
    /* Main background (overall app) */
    .stApp {
        background-color: #CDFCFF;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #007D99;
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        color: #B2FAFF;
        font-weight: 600;
        margin: 5px 0;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00D0FF, #007D99);
        color: white;
        border-radius: 8px;
        padding: 6px 16px;
        font-weight: bold;
        margin: 4px 0px;
        width: 100%;
        border: none;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #007D99, #00D0FF);
        color: white;
    }

    /* Cards (frames) */
    .card {
        background-color: #B2FAFF;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
    }

    /* Titles */
    .title-text {
        color: black;
        font-weight: 700;
    }

    /* Footer */
    .footer {
        background-color: #007D99;
        padding: 10px;
        text-align: center;
        color: white;
        font-size: 14px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)


# Sidebar Navigation
with st.sidebar:
    st.markdown("<h2 style='color:white;'>CareerCompass</h2>", unsafe_allow_html=True)
    page = st.radio("", ["Home", "Leaderboard", "Contact us", "About us", "Settings"])

# ------------------ Pages ------------------ #
if page == "Home":
    st.markdown("<h2 class='title-text' style='text-align:center;'>Hackathon Dashboard</h2>", unsafe_allow_html=True)
    
    # Cards row
    cols = st.columns(3)
    with cols[0]:
        st.markdown("<div class='card'><h4>Upcoming Hackathons</h4></div>", unsafe_allow_html=True)
        st.button("Contest 101")
        st.button("Contest 102")
        st.button("Contest 103")
    with cols[1]:
        st.markdown("<div class='card'><h4>Discussions and Q&A</h4></div>", unsafe_allow_html=True)
        st.button("Stacks")
        st.button("Queues")
        st.button("Linked list")
    with cols[2]:
        st.markdown("<div class='card'><h4>Submissions Portal</h4></div>", unsafe_allow_html=True)
        st.button("Enroll Now")
        st.button("Hackathons list")
        st.button("Deadlines")

    # Metrics + Activity row
    row2 = st.columns([2,1])
    with row2[0]:
        st.markdown("<div class='card'><h4>Hackathon Metrics</h4></div>", unsafe_allow_html=True)
        st.bar_chart({"Metrics": [5, 3, 4, 2, 5]})
    with row2[1]:
        st.markdown("<div class='card'><h4>Activity</h4></div>", unsafe_allow_html=True)
        st.write("Progress This Month")
        st.progress(60)
        st.progress(30)

elif page == "Leaderboard":
    st.markdown("<h2 class='title-text'>Leaderboard</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.table({"Name": ["Alice", "Bob", "Charlie"], "Score": [1200, 1100, 1000]})
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Contact us":
    st.markdown("<h2 class='title-text'>Contact Us</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>📧 Email: support@careercompass.com</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>📞 Phone: +92-300-0000000</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>📍 Address: Karachi, Pakistan</div>", unsafe_allow_html=True)

elif page == "About us":
    st.markdown("<h2 class='title-text'>About Us</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class='card'>
        CareerCompass is a platform designed to help students participate in hackathons, 
        enhance their skills and collaborate with peers.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div class='card'>
        🚀 Our mission is to provide students with opportunities to learn, 
        compete and grow in the tech ecosystem.
        </div>
    """, unsafe_allow_html=True)

elif page == "Settings":
    st.markdown("<h2 class='title-text'>Settings</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.checkbox("Dark Mode")
    st.checkbox("Enable Notifications")
    st.checkbox("Auto-Save Progress")
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>© 2025 CareerCompass All rights reserved.</div>", unsafe_allow_html=True)




