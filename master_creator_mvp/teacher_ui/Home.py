"""
Master Creator v3 MVP - Teacher UI Home Page

Landing page with quick actions and system overview.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Master Creator v3 - Teacher Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for teacher-friendly styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .quick-action-card {
        background-color: #F8FAFC;
        border: 2px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .quick-action-card:hover {
        border-color: #3B82F6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<div class="main-header">🎓 Master Creator v3 MVP</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">9-Engine Adaptive Learning System for K-12 Special Education</div>',
    unsafe_allow_html=True,
)

# Welcome message
st.info(
    """
    **Welcome, Teacher!** This pilot system helps you create differentiated lessons
    for your 15 classes with adaptive support for all learners, including students with IEPs.
    """
)

# Quick Actions
st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📝 Generate Lesson")
    st.write("Create a new lesson with differentiated materials")
    if st.button("Start Lesson Generator", type="primary", use_container_width=True):
        st.switch_page("pages/1_Generate_Lesson.py")

with col2:
    st.markdown("### 👥 Student Dashboard")
    st.write("View student progress and mastery data")
    if st.button("Open Dashboard", use_container_width=True):
        st.switch_page("pages/3_Student_Dashboard.py")

with col3:
    st.markdown("### 📋 Manage IEPs")
    st.write("Update student accommodations and modifications")
    if st.button("IEP Manager", use_container_width=True):
        st.switch_page("pages/4_IEP_Manager.py")

st.divider()

# System Overview
st.subheader("📊 System Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Students", "2,250", help="Across all 15 teachers")
with col2:
    st.metric("Students with IEPs", "1,350", delta="60%")
with col3:
    st.metric("Lessons Generated", "127", delta="+12 this week")
with col4:
    st.metric("System Status", "🟢 Online", help="All engines operational")

st.divider()

# Recent Activity
st.subheader("📅 Recent Activity")

activity_data = [
    {"time": "10 mins ago", "action": "Generated lesson: Photosynthesis (Grade 9)"},
    {"time": "1 hour ago", "action": "Updated IEP: Maria Gonzalez"},
    {"time": "2 hours ago", "action": "Exported worksheets: Cell Structure unit"},
    {"time": "Yesterday", "action": "Diagnostic assessment: Period 3 Biology (18 students)"},
]

for activity in activity_data:
    st.text(f"⏰ {activity['time']} - {activity['action']}")

st.divider()

# System Information
with st.expander("ℹ️ System Information & Help"):
    st.markdown(
        """
        ### Master Creator v3 Features

        **9 AI Engines:**
        - **Engine 0**: Unit Plan Designer (multi-lesson coherence)
        - **Engine 1**: Lesson Architect (10-part blueprints)
        - **Engine 2**: Worksheet Designer (3-tier differentiation)
        - **Engine 3**: IEP Modification Specialist (legal compliance)
        - **Engine 4**: Adaptive Personalization (branching logic)
        - **Engine 5**: Diagnostic Engine (Bayesian Knowledge Tracing)
        - **Engine 6**: Feedback Loop (accuracy monitoring)
        - **Student Model**: Central data hub (PostgreSQL + Chroma)
        - **Assessment Grader**: Auto-scoring + rubric-based feedback

        **Compliance:**
        - ✅ FERPA (data privacy)
        - ✅ IDEA (IEP requirements)
        - ✅ Section 504 (accommodations)
        - ✅ UDL (Universal Design for Learning)
        - ✅ Trauma-informed practices

        **Need Help?**
        - See the **Settings** page for system configuration
        - Contact support: [email protected]
        - Documentation: See README.md in project root
        """
    )

# Sidebar
with st.sidebar:
    st.image(
        "https://via.placeholder.com/150x50/1E3A8A/FFFFFF?text=Master+Creator",
        use_container_width=True,
    )

    st.markdown("---")

    st.markdown("### 🧭 Navigation")
    st.page_link("Home.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_Generate_Lesson.py", label="📝 Generate Lesson", icon="📝")
    st.page_link("pages/2_Review_Worksheets.py", label="📄 Review Worksheets", icon="📄")
    st.page_link("pages/3_Student_Dashboard.py", label="👥 Student Dashboard", icon="👥")
    st.page_link("pages/4_IEP_Manager.py", label="📋 IEP Manager", icon="📋")
    st.page_link("pages/5_Settings.py", label="⚙️ Settings", icon="⚙️")

    st.markdown("---")

    st.markdown("### 👤 User Info")
    st.write("**Teacher:** Demo User")
    st.write("**School:** Pilot School #1")
    st.write("**Classes:** 1 active")

    if st.button("🚪 Logout", use_container_width=True):
        st.info("Logout functionality will be added in Phase 2")
