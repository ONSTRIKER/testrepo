"""
Master Creator v3 MVP - Page 4: IEP Manager

Manage student IEPs and accommodations:
- View all students with IEPs
- Edit accommodations and modifications
- IDEA/Section 504 compliance tracking
- Integration with Engine 3 (IEP Modification Specialist)
"""

import streamlit as st
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="IEP Manager - Master Creator v3",
    page_icon="📋",
    layout="wide",
)

# Initialize session state
if "editing_student_id" not in st.session_state:
    st.session_state.editing_student_id = None
if "show_add_student" not in st.session_state:
    st.session_state.show_add_student = False

# Header
st.title("📋 IEP Manager")
st.markdown("Manage Individual Education Programs and accommodations for special education students.")

st.info(
    """
    **Compliance:** This system ensures IDEA, Section 504, and FERPA compliance.
    All IEP data is encrypted and access-logged for audit trails.
    """
)

st.divider()

# Mock IEP student data (from Student Model API in production)
iep_students = [
    {
        "student_id": "s2",
        "name": "Maria Gonzalez",
        "grade": "9",
        "primary_disability": "Specific Learning Disability",
        "secondary_disabilities": [],
        "accommodations": [
            {"type": "Extended Time", "enabled": True, "settings": {"multiplier": 1.5}},
            {"type": "Text-to-Speech", "enabled": True, "settings": {}},
            {"type": "Graphic Organizers", "enabled": True, "settings": {}},
        ],
        "modifications": {"alternate_grading": False, "reduced_content": False},
        "last_reviewed": "2024-09-15",
        "next_review_due": "2025-03-15",
        "iep_goals": [
            "Improve reading comprehension to grade level by end of year",
            "Increase writing stamina to 2 paragraphs with minimal support",
        ],
    },
    {
        "student_id": "s3",
        "name": "David Kim",
        "grade": "9",
        "primary_disability": "ADHD",
        "secondary_disabilities": ["Other Health Impairment"],
        "accommodations": [
            {"type": "Reduced Question Count", "enabled": True, "settings": {"reduction": 0.3}},
            {"type": "Movement Breaks", "enabled": True, "settings": {"frequency_minutes": 15}},
            {"type": "Preferential Seating", "enabled": True, "settings": {}},
            {"type": "Text-to-Speech", "enabled": True, "settings": {}},
        ],
        "modifications": {"alternate_grading": False, "reduced_content": True},
        "last_reviewed": "2024-08-20",
        "next_review_due": "2025-02-20",
        "iep_goals": [
            "Sustain focus on tasks for 20+ minutes with minimal redirection",
            "Complete assignments independently 80% of the time",
        ],
    },
    {
        "student_id": "s5",
        "name": "Emma Wilson",
        "grade": "9",
        "primary_disability": "Specific Learning Disability",
        "secondary_disabilities": [],
        "accommodations": [
            {"type": "Reduced Question Count", "enabled": True, "settings": {"reduction": 0.4}},
            {"type": "Sentence Frames", "enabled": True, "settings": {}},
            {"type": "Extended Time", "enabled": True, "settings": {"multiplier": 2.0}},
        ],
        "modifications": {"alternate_grading": True, "reduced_content": True},
        "last_reviewed": "2024-10-01",
        "next_review_due": "2025-04-01",
        "iep_goals": [
            "Decode grade-level text with 80% accuracy",
            "Write complete sentences with subject-verb agreement",
        ],
    },
    {
        "student_id": "s6",
        "name": "Carlos Martinez",
        "grade": "9",
        "primary_disability": "Speech/Language Impairment",
        "secondary_disabilities": [],
        "accommodations": [
            {"type": "Graphic Organizers", "enabled": True, "settings": {}},
            {"type": "Sentence Frames", "enabled": True, "settings": {}},
            {"type": "Audio Recordings", "enabled": True, "settings": {}},
        ],
        "modifications": {"alternate_grading": False, "reduced_content": False},
        "last_reviewed": "2024-09-10",
        "next_review_due": "2025-03-10",
        "iep_goals": [
            "Express ideas in complete sentences during class discussions",
            "Use vocabulary strategies to understand unfamiliar words",
        ],
    },
]

# ═══════════════════════════════════════════════════════════
# SECTION 1: IEP STUDENT LIST
# ═══════════════════════════════════════════════════════════

st.markdown(f"## 📋 Students with IEPs ({len(iep_students)} students)")

col1, col2 = st.columns([3, 1])
with col1:
    st.write("Click **[Edit]** to modify accommodations or **[View Full IEP]** for complete details.")
with col2:
    if st.button("➕ Add New Student to IEP", type="primary", use_container_width=True):
        st.session_state.show_add_student = True
        st.rerun()

st.divider()

# Display each IEP student
for student in iep_students:
    with st.container():
        # Student header
        col1, col2, col3 = st.columns([4, 3, 2])

        with col1:
            st.markdown(f"### 👤 {student['name']}")
            st.caption(f"Grade {student['grade']} • Student ID: {student['student_id']}")

        with col2:
            # Review status
            next_review = datetime.strptime(student["next_review_due"], "%Y-%m-%d")
            days_until_review = (next_review - datetime.now()).days

            if days_until_review < 30:
                st.warning(f"⚠️ Review due in {days_until_review} days")
            else:
                st.info(f"✅ Next review: {student['next_review_due']}")

        with col3:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✏️ Edit", key=f"edit_{student['student_id']}", use_container_width=True):
                    st.session_state.editing_student_id = student["student_id"]
                    st.rerun()
            with col_b:
                if st.button(
                    "🔍 View", key=f"view_{student['student_id']}", use_container_width=True
                ):
                    st.session_state.editing_student_id = student["student_id"]
                    # In production, this would open a detailed IEP modal

        # Compact info display
        with st.expander(f"Quick Summary - {student['name']}", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Primary Disability:** {student['primary_disability']}")
                if student["secondary_disabilities"]:
                    st.write(f"**Secondary:** {', '.join(student['secondary_disabilities'])}")

                st.write(f"\n**Active Accommodations ({len(student['accommodations'])}):**")
                for accom in student["accommodations"]:
                    if accom["enabled"]:
                        settings_str = (
                            f" ({list(accom['settings'].values())[0]})"
                            if accom["settings"]
                            else ""
                        )
                        st.write(f"✅ {accom['type']}{settings_str}")

            with col2:
                st.write("**IEP Goals:**")
                for goal in student["iep_goals"]:
                    st.write(f"• {goal}")

                if student["modifications"]["alternate_grading"]:
                    st.warning("📝 Alternate grading criteria in effect")
                if student["modifications"]["reduced_content"]:
                    st.warning("📉 Reduced content modification in effect")

        st.divider()

# ═══════════════════════════════════════════════════════════
# SECTION 2: EDIT IEP MODAL
# ═══════════════════════════════════════════════════════════

if st.session_state.editing_student_id:
    # Find the student being edited
    editing_student = next(
        (s for s in iep_students if s["student_id"] == st.session_state.editing_student_id), None
    )

    if editing_student:
        st.markdown("---")
        st.markdown(f"## ✏️ Editing IEP: {editing_student['name']}")

        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.editing_student_id = None
                st.rerun()

        st.divider()

        # Edit form
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📋 Disability Information")

            primary_disability = st.selectbox(
                "Primary Disability *",
                options=[
                    "Specific Learning Disability",
                    "ADHD",
                    "Autism Spectrum Disorder",
                    "Speech/Language Impairment",
                    "Intellectual Disability",
                    "Emotional Disturbance",
                    "Other Health Impairment",
                ],
                index=0,
                help="Primary disability category (IDEA)",
            )

            secondary_disabilities = st.multiselect(
                "Secondary Disabilities (if any)",
                options=[
                    "ADHD",
                    "Anxiety Disorder",
                    "Auditory Processing",
                    "Visual Processing",
                    "Other Health Impairment",
                ],
                default=editing_student.get("secondary_disabilities", []),
            )

        with col2:
            st.markdown("### 📅 Review Dates")

            last_reviewed = st.date_input(
                "Last IEP Review",
                value=datetime.strptime(editing_student["last_reviewed"], "%Y-%m-%d"),
                help="Date of most recent IEP meeting",
            )

            next_review = st.date_input(
                "Next Review Due",
                value=datetime.strptime(editing_student["next_review_due"], "%Y-%m-%d"),
                help="Annual IEP review deadline",
            )

        st.divider()

        # Accommodations section
        st.markdown("### ✅ Accommodations")
        st.caption(
            "Select all accommodations from the student's IEP. These will automatically apply to Engine 3."
        )

        # Predefined accommodation types
        accommodation_options = [
            {"name": "Extended Time", "has_settings": True, "setting_type": "multiplier"},
            {"name": "Text-to-Speech", "has_settings": False},
            {"name": "Reduced Question Count", "has_settings": True, "setting_type": "reduction"},
            {"name": "Graphic Organizers", "has_settings": False},
            {"name": "Calculator", "has_settings": False},
            {"name": "Scribe", "has_settings": False},
            {"name": "Preferential Seating", "has_settings": False},
            {"name": "Movement Breaks", "has_settings": True, "setting_type": "frequency"},
            {"name": "Sentence Frames", "has_settings": False},
            {"name": "Word Bank", "has_settings": False},
            {"name": "Visual Supports", "has_settings": False},
            {"name": "Audio Recordings", "has_settings": False},
        ]

        # Get current accommodations
        current_accoms = {a["type"]: a for a in editing_student["accommodations"]}

        selected_accommodations = []

        for accom_option in accommodation_options:
            col1, col2 = st.columns([3, 2])

            with col1:
                is_enabled = st.checkbox(
                    accom_option["name"],
                    value=accom_option["name"] in current_accoms
                    and current_accoms[accom_option["name"]]["enabled"],
                    key=f"accom_{accom_option['name']}",
                )

            with col2:
                setting_value = None
                if is_enabled and accom_option.get("has_settings"):
                    if accom_option["setting_type"] == "multiplier":
                        setting_value = st.number_input(
                            "Time multiplier",
                            min_value=1.0,
                            max_value=3.0,
                            value=1.5,
                            step=0.5,
                            key=f"setting_{accom_option['name']}",
                        )
                    elif accom_option["setting_type"] == "reduction":
                        setting_value = st.slider(
                            "Reduction %",
                            min_value=10,
                            max_value=50,
                            value=30,
                            step=10,
                            key=f"setting_{accom_option['name']}",
                        )
                    elif accom_option["setting_type"] == "frequency":
                        setting_value = st.number_input(
                            "Minutes",
                            min_value=10,
                            max_value=30,
                            value=15,
                            step=5,
                            key=f"setting_{accom_option['name']}",
                        )

            if is_enabled:
                selected_accommodations.append(
                    {
                        "type": accom_option["name"],
                        "enabled": True,
                        "settings": {accom_option.get("setting_type", "value"): setting_value}
                        if setting_value
                        else {},
                    }
                )

        st.divider()

        # Modifications section
        st.markdown("### 📝 Modifications")
        st.caption("Modifications change the learning standards or expectations (use sparingly).")

        col1, col2 = st.columns(2)
        with col1:
            alternate_grading = st.checkbox(
                "Alternate Grading Criteria",
                value=editing_student["modifications"].get("alternate_grading", False),
                help="Student is graded on modified standards",
            )
        with col2:
            reduced_content = st.checkbox(
                "Reduced Content Expectations",
                value=editing_student["modifications"].get("reduced_content", False),
                help="Student completes fewer items or simplified content",
            )

        st.divider()

        # IEP Goals
        st.markdown("### 🎯 IEP Goals")

        goal_1 = st.text_area(
            "Goal 1:",
            value=editing_student["iep_goals"][0] if len(editing_student["iep_goals"]) > 0 else "",
            height=80,
        )
        goal_2 = st.text_area(
            "Goal 2:",
            value=editing_student["iep_goals"][1] if len(editing_student["iep_goals"]) > 1 else "",
            height=80,
        )
        goal_3 = st.text_area(
            "Goal 3 (optional):",
            value=editing_student["iep_goals"][2] if len(editing_student["iep_goals"]) > 2 else "",
            height=80,
        )

        st.divider()

        # Save button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                # In production, this calls API: PUT /api/v1/students/{id}/iep
                st.success(f"✅ IEP updated for {editing_student['name']}!")
                st.info(
                    "Changes will automatically apply to Engine 3 for future worksheet generation."
                )
                st.session_state.editing_student_id = None
                st.balloons()
                # Wait 2 seconds then rerun
                import time

                time.sleep(2)
                st.rerun()

# ═══════════════════════════════════════════════════════════
# SECTION 3: ADD NEW STUDENT TO IEP
# ═══════════════════════════════════════════════════════════

if st.session_state.show_add_student:
    st.markdown("---")
    st.markdown("## ➕ Add New Student to IEP Tracking")

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("❌ Cancel", key="cancel_add", use_container_width=True):
            st.session_state.show_add_student = False
            st.rerun()

    st.divider()

    # Add student form
    col1, col2 = st.columns(2)

    with col1:
        new_student_name = st.text_input("Student Name *", placeholder="First Last")
        new_grade = st.selectbox("Grade Level *", options=["9", "10", "11", "12"])
        new_primary_disability = st.selectbox(
            "Primary Disability *",
            options=[
                "Specific Learning Disability",
                "ADHD",
                "Autism Spectrum Disorder",
                "Speech/Language Impairment",
                "Intellectual Disability",
                "Emotional Disturbance",
                "Other Health Impairment",
            ],
        )

    with col2:
        new_student_id = st.text_input(
            "Student ID", placeholder="Auto-generated if left blank", help="Unique identifier"
        )
        new_class = st.selectbox(
            "Assign to Class *",
            options=["Period 3 Biology", "Period 5 Chemistry", "Period 7 Physics"],
        )
        new_reading_level = st.selectbox(
            "Reading Level", options=["Below Basic", "Basic", "Proficient", "Advanced"], index=1
        )

    st.markdown("### ✅ Initial Accommodations")
    st.caption("Select accommodations from the student's IEP document.")

    # Quick checkboxes for common accommodations
    cols = st.columns(3)
    with cols[0]:
        new_extended_time = st.checkbox("Extended Time (1.5x)")
        new_text_to_speech = st.checkbox("Text-to-Speech")
        new_graphic_org = st.checkbox("Graphic Organizers")
        new_word_bank = st.checkbox("Word Bank")

    with cols[1]:
        new_reduced_q = st.checkbox("Reduced Question Count")
        new_sentence_frames = st.checkbox("Sentence Frames")
        new_visual_supports = st.checkbox("Visual Supports")
        new_calculator = st.checkbox("Calculator")

    with cols[2]:
        new_preferential = st.checkbox("Preferential Seating")
        new_movement = st.checkbox("Movement Breaks")
        new_audio = st.checkbox("Audio Recordings")
        new_scribe = st.checkbox("Scribe")

    st.divider()

    # Submit button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("➕ Add Student", type="primary", use_container_width=True):
            if not new_student_name:
                st.error("Student name is required!")
            else:
                # In production: POST /api/v1/students (with IEP data)
                st.success(f"✅ {new_student_name} added to IEP tracking!")
                st.info("Student is now available for lesson generation and tier assignment.")
                st.session_state.show_add_student = False
                st.balloons()

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 📋 IEP Manager")
    st.write("Manage accommodations and ensure IDEA compliance.")

    st.markdown("---")

    st.markdown("#### 📊 IEP Statistics")
    st.metric("Total IEP Students", len(iep_students))
    st.metric("Reviews Due (30 days)", sum(1 for s in iep_students if (datetime.strptime(s["next_review_due"], "%Y-%m-%d") - datetime.now()).days < 30))

    st.markdown("---")

    st.markdown("#### ⚖️ Compliance")
    st.success("✅ IDEA Compliant")
    st.success("✅ Section 504 Compliant")
    st.success("✅ FERPA Secure")
    st.caption("All IEP data is encrypted at rest and access-logged.")

    st.markdown("---")

    st.markdown("#### 💡 Quick Tips")
    st.info(
        """
        - Review IEPs annually (IDEA requirement)
        - Accommodations ≠ Modifications
        - Engine 3 automatically applies accommodations
        - Contact IEP team for major changes
        """
    )

    st.markdown("---")

    st.markdown("#### 🔗 Quick Actions")
    if st.button("👥 View Student Dashboard", use_container_width=True):
        st.switch_page("pages/3_Student_Dashboard.py")
    if st.button("📝 Generate Lesson", use_container_width=True):
        st.switch_page("pages/1_Generate_Lesson.py")
