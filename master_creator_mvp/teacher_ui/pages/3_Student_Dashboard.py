"""
Master Creator v3 MVP - Page 3: Student Dashboard

Displays student progress and mastery data:
- Class overview with mastery distribution
- Individual student profiles
- Recent assessments
- Adaptive recommendations

Queries Student Model API for real-time data.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Student Dashboard - Master Creator v3",
    page_icon="👥",
    layout="wide",
)

# Initialize session state
if "selected_student_id" not in st.session_state:
    st.session_state.selected_student_id = None

# Header
st.title("👥 Student Dashboard")
st.markdown("Monitor progress, mastery, and identify students needing support.")

st.divider()

# ═══════════════════════════════════════════════════════════
# SECTION 1: CLASS SELECTOR
# ═══════════════════════════════════════════════════════════

col1, col2 = st.columns([3, 1])
with col1:
    selected_class = st.selectbox(
        "Select Class:",
        options=[
            "Period 3 Biology (18 students)",
            "Period 5 Chemistry (22 students)",
            "Period 7 Physics (15 students)",
        ],
        help="Choose which class to view",
    )
with col2:
    st.metric("Total Students", "18", help="Active students in this class")

# Parse class info (mock)
class_id = "class_period_3_bio"
class_name = "Period 3 Biology"
total_students = 18
students_with_ieps = 12

# Mock mastery data (in production, from Student Model API)
class_mastery_data = {
    "concepts": [
        {
            "concept_name": "Photosynthesis",
            "mean_mastery": 0.72,
            "students_below_50": 3,
            "students_50_to_75": 9,
            "students_above_75": 6,
        },
        {
            "concept_name": "Cell Structure",
            "mean_mastery": 0.61,
            "students_below_50": 6,
            "students_50_to_75": 8,
            "students_above_75": 4,
        },
        {
            "concept_name": "Genetics",
            "mean_mastery": 0.38,
            "students_below_50": 11,
            "students_50_to_75": 5,
            "students_above_75": 2,
        },
        {
            "concept_name": "Evolution",
            "mean_mastery": 0.55,
            "students_below_50": 7,
            "students_50_to_75": 7,
            "students_above_75": 4,
        },
    ]
}

# Mock student roster
student_roster = [
    {
        "student_id": "s1",
        "name": "Alex Chen",
        "has_iep": False,
        "reading_level": "Proficient",
        "overall_mastery": 0.85,
        "needs_attention": False,
    },
    {
        "student_id": "s2",
        "name": "Maria Gonzalez",
        "has_iep": True,
        "reading_level": "Basic",
        "overall_mastery": 0.55,
        "needs_attention": False,
    },
    {
        "student_id": "s3",
        "name": "David Kim",
        "has_iep": True,
        "reading_level": "Below Basic",
        "overall_mastery": 0.32,
        "needs_attention": True,
    },
    {
        "student_id": "s4",
        "name": "Jordan Rivera",
        "has_iep": False,
        "reading_level": "Advanced",
        "overall_mastery": 0.78,
        "needs_attention": False,
    },
    {
        "student_id": "s5",
        "name": "Emma Wilson",
        "has_iep": True,
        "reading_level": "Below Basic",
        "overall_mastery": 0.28,
        "needs_attention": True,
    },
    {
        "student_id": "s6",
        "name": "Carlos Martinez",
        "has_iep": True,
        "reading_level": "Basic",
        "overall_mastery": 0.48,
        "needs_attention": True,
    },
    {
        "student_id": "s7",
        "name": "Sam Parker",
        "has_iep": False,
        "reading_level": "Proficient",
        "overall_mastery": 0.82,
        "needs_attention": False,
    },
    {
        "student_id": "s8",
        "name": "Aisha Patel",
        "has_iep": False,
        "reading_level": "Proficient",
        "overall_mastery": 0.62,
        "needs_attention": False,
    },
]

st.divider()

# ═══════════════════════════════════════════════════════════
# SECTION 2: CLASS OVERVIEW - MASTERY DISTRIBUTION
# ═══════════════════════════════════════════════════════════

st.markdown("## 📊 Class Mastery Overview")

# Create bar chart with Plotly
fig = go.Figure()

concepts = [c["concept_name"] for c in class_mastery_data["concepts"]]
mean_mastery = [c["mean_mastery"] * 100 for c in class_mastery_data["concepts"]]

fig.add_trace(
    go.Bar(
        x=concepts,
        y=mean_mastery,
        text=[f"{m:.0f}%" for m in mean_mastery],
        textposition="outside",
        marker=dict(
            color=mean_mastery,
            colorscale="RdYlGn",
            cmin=0,
            cmax=100,
            showscale=False,
        ),
    )
)

fig.update_layout(
    title="Average Mastery by Concept",
    xaxis_title="Concept",
    yaxis_title="Average Mastery (%)",
    yaxis=dict(range=[0, 100]),
    height=400,
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True)

# Distribution table
st.markdown("### 📈 Detailed Distribution")

df_distribution = pd.DataFrame(
    [
        {
            "Concept": c["concept_name"],
            "Avg Mastery": f"{c['mean_mastery']*100:.0f}%",
            "Below 50%": c["students_below_50"],
            "50-75%": c["students_50_to_75"],
            "Above 75%": c["students_above_75"],
        }
        for c in class_mastery_data["concepts"]
    ]
)

st.dataframe(df_distribution, use_container_width=True, hide_index=True)

st.divider()

# ═══════════════════════════════════════════════════════════
# SECTION 3: STUDENTS NEEDING ATTENTION
# ═══════════════════════════════════════════════════════════

st.markdown("## ⚠️ Students Needing Attention")
st.info(
    "Students with <50% mastery or significant struggles on recent assessments (identified by Engine 5 + Engine 6)"
)

attention_students = [s for s in student_roster if s["needs_attention"]]

if attention_students:
    cols = st.columns(3)
    for idx, student in enumerate(attention_students):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### 🔴 {student['name']}")
                st.write(f"**Overall Mastery:** {student['overall_mastery']*100:.0f}%")
                st.write(f"**IEP Status:** {'Yes 📋' if student['has_iep'] else 'No'}")
                st.write(f"**Reading Level:** {student['reading_level']}")

                if st.button(f"View Profile", key=f"view_{student['student_id']}"):
                    st.session_state.selected_student_id = student["student_id"]
                    st.rerun()
else:
    st.success("🎉 No students currently need immediate attention!")

st.divider()

# ═══════════════════════════════════════════════════════════
# SECTION 4: STUDENT ROSTER TABLE (CLICKABLE)
# ═══════════════════════════════════════════════════════════

st.markdown("## 📋 Full Class Roster")

# Create roster DataFrame
df_roster = pd.DataFrame(
    [
        {
            "Name": s["name"],
            "IEP": "✅" if s["has_iep"] else "❌",
            "Reading Level": s["reading_level"],
            "Overall Mastery": f"{s['overall_mastery']*100:.0f}%",
            "Status": "⚠️ Needs Attention" if s["needs_attention"] else "✅ On Track",
        }
        for s in student_roster
    ]
)

st.dataframe(df_roster, use_container_width=True, hide_index=True)

st.markdown("*Click a student name below to view detailed profile:*")

# Student selector
selected_student_name = st.selectbox(
    "Select Student for Detailed View:",
    options=[s["name"] for s in student_roster],
    help="View individual progress and recommendations",
)

# Find selected student
selected_student = next(s for s in student_roster if s["name"] == selected_student_name)
st.session_state.selected_student_id = selected_student["student_id"]

st.divider()

# ═══════════════════════════════════════════════════════════
# SECTION 5: INDIVIDUAL STUDENT PROFILE
# ═══════════════════════════════════════════════════════════

if st.session_state.selected_student_id:
    student = selected_student

    # Mock detailed student data (from Student Model API in production)
    student_detail = {
        "student_id": student["student_id"],
        "name": student["name"],
        "grade": "9",
        "has_iep": student["has_iep"],
        "reading_level": student["reading_level"],
        "primary_disability": "ADHD + Processing Disorder" if student["has_iep"] else None,
        "concept_mastery": [
            {"concept": "Photosynthesis", "mastery": 0.70, "updated": "2024-11-10"},
            {"concept": "Cell Structure", "mastery": 0.45, "updated": "2024-11-08"},
            {"concept": "Genetics", "mastery": 0.25, "updated": "2024-11-05"},
            {"concept": "Evolution", "mastery": 0.50, "updated": "2024-11-01"},
        ],
        "recent_assessments": [
            {
                "date": "2024-11-10",
                "type": "Worksheet",
                "topic": "Photosynthesis",
                "score": "7/10",
                "percentage": 70,
                "tier": "Tier 2",
            },
            {
                "date": "2024-11-08",
                "type": "Quiz",
                "topic": "Cell Structure",
                "score": "12/15",
                "percentage": 80,
                "tier": "Tier 1",
            },
            {
                "date": "2024-11-05",
                "type": "Diagnostic",
                "topic": "Genetics",
                "score": "4/10",
                "percentage": 40,
                "tier": "Tier 3",
            },
        ],
        "iep_accommodations": [
            "Extended Time (1.5x)",
            "Text-to-Speech",
            "Graphic Organizers",
            "Preferential Seating",
        ]
        if student["has_iep"]
        else [],
        "adaptive_recommendations": [
            {
                "type": "tier_change",
                "message": "Student ready to move from Tier 2 to Tier 1 for Photosynthesis",
                "confidence": 0.85,
            },
            {
                "type": "intervention",
                "message": "Needs additional visual support for abstract Genetics concepts",
                "confidence": 0.92,
            },
            {
                "type": "strength",
                "message": "Strong improvement on Cell Structure - consider peer tutoring role",
                "confidence": 0.78,
            },
        ],
    }

    st.markdown(f"## 👤 {student_detail['name']} - Individual Profile")

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Grade Level", student_detail["grade"])
    with col2:
        st.metric("IEP Status", "Active 📋" if student_detail["has_iep"] else "None")
    with col3:
        st.metric("Reading Level", student_detail["reading_level"])
    with col4:
        avg_mastery = sum(c["mastery"] for c in student_detail["concept_mastery"]) / len(
            student_detail["concept_mastery"]
        )
        st.metric("Avg Mastery", f"{avg_mastery*100:.0f}%")

    st.divider()

    # Concept mastery breakdown
    st.markdown("### 📊 Current Mastery by Concept")

    for concept_data in student_detail["concept_mastery"]:
        concept_name = concept_data["concept"]
        mastery = concept_data["mastery"]
        updated = concept_data["updated"]

        # Progress bar with color coding
        if mastery >= 0.75:
            color = "🟢"
            bar_color = "green"
        elif mastery >= 0.5:
            color = "🟡"
            bar_color = "orange"
        else:
            color = "🔴"
            bar_color = "red"

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"{color} **{concept_name}**")
            st.progress(mastery, text=f"{mastery*100:.0f}%")
            st.caption(f"Last updated: {updated}")
        with col2:
            st.metric("Mastery", f"{mastery*100:.0f}%")

    st.divider()

    # Recent assessments
    st.markdown("### 📝 Recent Assessments")

    for assessment in student_detail["recent_assessments"]:
        with st.expander(
            f"{assessment['date']} - {assessment['type']}: {assessment['topic']} ({assessment['score']})",
            expanded=False,
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", assessment["score"])
            with col2:
                st.metric("Percentage", f"{assessment['percentage']}%")
            with col3:
                st.metric("Tier Level", assessment["tier"])

            # Visual score indicator
            if assessment["percentage"] >= 75:
                st.success(f"✅ Strong performance ({assessment['percentage']}%)")
            elif assessment["percentage"] >= 50:
                st.warning(f"⚠️ Needs improvement ({assessment['percentage']}%)")
            else:
                st.error(f"🔴 Significant struggle ({assessment['percentage']}%)")

    st.divider()

    # IEP accommodations (if applicable)
    if student_detail["has_iep"]:
        st.markdown("### 📋 Active IEP Accommodations")

        st.info(f"**Primary Disability:** {student_detail['primary_disability']}")

        cols = st.columns(2)
        for idx, accom in enumerate(student_detail["iep_accommodations"]):
            with cols[idx % 2]:
                st.success(f"✅ {accom}")

        if st.button("🔍 View Full IEP Details", key="view_full_iep"):
            st.switch_page("pages/4_IEP_Manager.py")

        st.divider()

    # Adaptive recommendations (from Engine 4)
    st.markdown("### 💡 Adaptive Recommendations")
    st.caption("Generated by Engine 4: Adaptive Personalization Engine")

    for rec in student_detail["adaptive_recommendations"]:
        if rec["type"] == "tier_change":
            icon = "🔄"
            color = "info"
        elif rec["type"] == "intervention":
            icon = "⚠️"
            color = "warning"
        elif rec["type"] == "strength":
            icon = "⭐"
            color = "success"
        else:
            icon = "💡"
            color = "info"

        if color == "info":
            st.info(f"{icon} **{rec['message']}** (Confidence: {rec['confidence']*100:.0f}%)")
        elif color == "warning":
            st.warning(f"{icon} **{rec['message']}** (Confidence: {rec['confidence']*100:.0f}%)")
        elif color == "success":
            st.success(f"{icon} **{rec['message']}** (Confidence: {rec['confidence']*100:.0f}%)")

    st.divider()

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Export Student Report (PDF)", use_container_width=True):
            st.success(f"Student report for {student_detail['name']} exported!")
    with col2:
        if st.button("📧 Email Progress to Parent", use_container_width=True):
            st.info("Email functionality will be implemented in Phase 2")
    with col3:
        if st.button("📋 Update IEP", use_container_width=True):
            st.switch_page("pages/4_IEP_Manager.py")

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 👥 Student Dashboard")
    st.write("Monitor student progress and identify areas needing support.")

    st.markdown("---")

    st.markdown("#### 📊 Class Statistics")
    st.metric("Total Students", total_students)
    st.metric("Students with IEPs", students_with_ieps, delta=f"{students_with_ieps/total_students*100:.0f}%")
    st.metric("Needing Attention", len(attention_students), delta="-2 from last week", delta_color="inverse")

    st.markdown("---")

    st.markdown("#### 🎯 Quick Filters")
    if st.checkbox("Show only IEP students"):
        st.info("Filter will be applied in production version")
    if st.checkbox("Show only struggling students (<50%)"):
        st.info("Filter will be applied in production version")

    st.markdown("---")

    st.markdown("#### 🔗 Quick Actions")
    if st.button("📝 Generate New Lesson", use_container_width=True):
        st.switch_page("pages/1_Generate_Lesson.py")
    if st.button("📋 Manage IEPs", use_container_width=True):
        st.switch_page("pages/4_IEP_Manager.py")
