import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000/api"

st.set_page_config(page_title="Plan Deeper", page_icon="✈️", layout="wide")

# Theme styling to make it look premium
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .stButton>button {
        background-color: #2e519c;
        color: white;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1a3266;
        border-color: #1a3266;
    }
    h1, h2, h3 {
        color: #1a3266;
    }
    .premium-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "current_group" not in st.session_state:
    st.session_state.current_group = None

def get_users():
    try:
        r = requests.get(f"{API_URL}/users")
        if r.status_code == 200:
            return r.json()
    except:
        return []
    return []

def demo_switcher():
    st.sidebar.title("👥 Demo Controller")
    st.sidebar.write("Switch users to simulate a group.")
    
    users = get_users()
    if users:
        user_names = [u['username'] for u in users]
        current_idx = 0
        if st.session_state.user:
            current_idx = user_names.index(st.session_state.user['username']) if st.session_state.user['username'] in user_names else 0
            
        selected = st.sidebar.selectbox("Current User:", user_names, index=current_idx)
        st.session_state.user = next(u for u in users if u['username'] == selected)
        st.sidebar.success(f"Logged in as {st.session_state.user['username']}")
    else:
        st.sidebar.error("Backend not reachable or no users found. Please start FastAPI.")

def landing_page():
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>✈️ Plan Deeper</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Intelligent Group Travel Planning</h3>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=2074&auto=format&fit=crop", use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='premium-card'><h4>📊 Pool Budgets</h4><p>Combine individual budgets to find the best group options.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='premium-card'><h4>🤖 AI Recommendations</h4><p>Machine Learning algorithms rank the best destinations.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='premium-card'><h4>🗳️ Democratic Voting</h4><p>Vote seamlessly with your group to decide the final spot.</p></div>", unsafe_allow_html=True)
    
    if not st.session_state.user:
        st.warning("Please select a user from the Demo Controller on the left to start planning.")

def dashboard():
    st.title(f"👋 Welcome, {st.session_state.user['username']}")
    
    # Create Group
    with st.expander("➕ Create a New Group", expanded=False):
        g_name = st.text_input("Group Name")
        if st.button("Create Group"):
            r = requests.post(f"{API_URL}/groups?user_id={st.session_state.user['id']}", json={"group_name": g_name})
            if r.status_code == 200:
                st.success("Group created!")
                st.rerun()
    
    # List Groups
    st.subheader("Your Groups")
    r = requests.get(f"{API_URL}/groups?user_id={st.session_state.user['id']}")
    if r.status_code == 200:
        groups = r.json()
        if not groups:
            st.info("You haven't joined any groups yet.")
        for g in groups:
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{g['group_name']}** (ID: {g['id']})")
            if col2.button("Open", key=f"open_{g['id']}"):
                st.session_state.current_group = g
                st.rerun()

def group_view():
    group = st.session_state.current_group
    st.title(f"🏖️ {group['group_name']}")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_group = None
        st.rerun()
        
    tab1, tab2, tab3 = st.tabs(["📝 Preferences", "✨ Recommendations", "🗳️ Voting"])
    
    with tab1:
        st.subheader("Enter Your Preferences")
        dest_type = st.selectbox("Preferred Type", ["Beach", "City", "Hill", "Historical", "Adventure", "Religious", "Nature"])
        activities = st.multiselect("Activities", ["Trekking", "Sightseeing", "Beach Volley", "Surfing", "Museum", "Shopping", "Food Tour", "Skiing"])
        budget = st.number_input("Your Budget ($)", min_value=100, value=1000)
        duration = st.slider("Duration (Days)", 1, 14, 5)
        
        if st.button("Submit Preferences"):
            payload = {
                "destination_type": dest_type,
                "activities": ",".join(activities),
                "budget": budget,
                "duration": duration
            }
            r = requests.post(f"{API_URL}/groups/{group['id']}/preferences?user_id={st.session_state.user['id']}", json=payload)
            if r.status_code == 200:
                st.success("Preferences saved!")
                
    with tab2:
        st.subheader("AI Recommendations")
        if st.button("Generate Recommendations"):
            with st.spinner("Analyzing group preferences and pooling budget..."):
                r = requests.get(f"{API_URL}/groups/{group['id']}/recommendations")
                if r.status_code == 200:
                    data = r.json()
                    st.info(f"💰 **Total Pooled Budget**: ${data['pooled_budget']}")
                    st.success(f"🤖 **Google ADK Insights**: {data.get('adk_insights', '')}")
                    
                    recs = data.get('recommendations', [])
                    if not recs:
                        st.warning("No destinations matched or no preferences set yet.")
                    else:
                        for idx, rec in enumerate(recs):
                            st.markdown(f"""
                            <div class='premium-card'>
                                <h3>#{idx+1} {rec['destination']}</h3>
                                <p><b>Type:</b> {rec['type']} | <b>Rating:</b> ⭐ {rec['rating']} | <b>Cost:</b> ${rec['cost']}</p>
                                <p><b>Match Score:</b> {rec['score']}%</p>
                                <p><i>{rec['explanation']}</i></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
    with tab3:
        st.subheader("Cast Your Vote")
        r = requests.get(f"{API_URL}/groups/{group['id']}/recommendations")
        options = []
        if r.status_code == 200:
            recs = r.json().get('recommendations', [])
            options = [r['destination'] for r in recs]
            
        if options:
            vote = st.selectbox("Select your favorite destination", options)
            if st.button("Submit Vote"):
                requests.post(f"{API_URL}/groups/{group['id']}/vote?user_id={st.session_state.user['id']}", json={"destination_name": vote})
                st.success("Vote recorded!")
                
        st.markdown("---")
        st.subheader("Live Results")
        if st.button("Refresh Votes"):
            r = requests.get(f"{API_URL}/groups/{group['id']}/votes")
            if r.status_code == 200:
                votes = r.json().get('votes', {})
                if votes:
                    df = pd.DataFrame(list(votes.items()), columns=['Destination', 'Votes'])
                    st.bar_chart(df.set_index('Destination'))
                else:
                    st.info("No votes yet.")

# Main Layout Routing
demo_switcher()

if st.session_state.user is None:
    landing_page()
elif st.session_state.current_group is None:
    dashboard()
else:
    group_view()
