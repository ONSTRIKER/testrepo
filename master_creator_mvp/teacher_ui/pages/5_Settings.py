"""
Master Creator v3 MVP - Page 5: Settings & Roster Management

System configuration and student roster management:
- CSV bulk import for class rosters
- Manual student addition
- Teacher preferences (tier logic, export formats, defaults)
- System settings
"""

import streamlit as st
import pandas as pd
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Settings - Master Creator v3",
    page_icon="⚙️",
    layout="wide",
)

# Initialize session state
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# Header
st.title("⚙️ Settings & Roster Management")
st.markdown("Configure system preferences and manage student rosters.")

# Create tabs for different settings sections
tab1, tab2, tab3 = st.tabs(["📥 Import Students", "➕ Add Student Manually", "⚙️ System Preferences"])

# ═══════════════════════════════════════════════════════════
# TAB 1: CSV BULK IMPORT
# ═══════════════════════════════════════════════════════════

with tab1:
    st.markdown("## 📥 Bulk Import Student Roster")
    st.info(
        """
        Upload a CSV file with your class roster. The system will automatically create student profiles
        and assign them to your class. Students with IEPs will be flagged for accommodation setup.
        """
    )

    # Instructions
    with st.expander("📖 CSV Format Instructions", expanded=False):
        st.markdown(
            """
            ### Required Columns:
            - `student_name` - Full name (First Last)
            - `grade_level` - Grade (9, 10, 11, or 12)

            ### Optional Columns:
            - `reading_level` - Proficiency (Below Basic, Basic, Proficient, Advanced)
            - `iep_status` - IEP indicator (Yes or No)
            - `primary_disability` - If IEP=Yes (Learning Disability, ADHD, Autism, etc.)
            - `student_id` - Unique identifier (auto-generated if blank)

            ### Example:
            ```
            student_name,grade_level,reading_level,iep_status,primary_disability
            Maria Gonzalez,9,Basic,Yes,Specific Learning Disability
            Alex Chen,9,Proficient,No,
            David Kim,9,Below Basic,Yes,ADHD
            ```
            """
        )

    st.divider()

    # Template download
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("### 1️⃣ Download CSV Template")
        st.write("Start with our template to ensure correct formatting.")
    with col2:
        # Create sample template
        template_data = pd.DataFrame(
            {
                "student_name": ["Maria Gonzalez", "Alex Chen", "David Kim"],
                "grade_level": ["9", "9", "9"],
                "reading_level": ["Basic", "Proficient", "Below Basic"],
                "iep_status": ["Yes", "No", "Yes"],
                "primary_disability": ["Specific Learning Disability", "", "ADHD"],
            }
        )

        csv_template = template_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Template CSV",
            data=csv_template,
            file_name="student_roster_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()

    # File upload
    st.markdown("### 2️⃣ Upload Your Class Roster")

    col1, col2 = st.columns([3, 2])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=["csv"],
            help="Upload a CSV file with student roster data",
        )

    with col2:
        class_assignment = st.selectbox(
            "Assign to Class:",
            options=[
                "Period 3 Biology",
                "Period 5 Chemistry",
                "Period 7 Physics",
                "Create New Class...",
            ],
            help="Which class should these students be added to?",
        )

        if class_assignment == "Create New Class...":
            new_class_name = st.text_input("New Class Name:", placeholder="e.g., Period 1 Math")

    # Process uploaded file
    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_data = df

            st.success(f"✅ File uploaded successfully! Found {len(df)} students.")

            # Display preview
            st.markdown("### 👀 Preview Data")
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Validation checks
            st.markdown("### ✅ Validation Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Required columns check
                required_cols = ["student_name", "grade_level"]
                has_required = all(col in df.columns for col in required_cols)

                if has_required:
                    st.success(f"✅ Required columns present")
                else:
                    missing = [col for col in required_cols if col not in df.columns]
                    st.error(f"❌ Missing columns: {', '.join(missing)}")

            with col2:
                # IEP students count
                iep_count = df[df.get("iep_status", "No") == "Yes"].shape[0] if "iep_status" in df.columns else 0
                st.info(f"📋 {iep_count} students with IEPs")

            with col3:
                # Grade distribution
                if "grade_level" in df.columns:
                    grade_dist = df["grade_level"].value_counts().to_dict()
                    st.info(f"📊 Grades: {', '.join([f'{k}({v})' for k, v in grade_dist.items()])}")

            # Import button
            st.divider()
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("🚀 Import Students", type="primary", use_container_width=True):
                    with st.spinner("Importing students..."):
                        import time

                        time.sleep(2)  # Simulate API call

                        # In production: POST /api/v1/students/import
                        st.success(f"✅ Successfully imported {len(df)} students!")
                        st.info(
                            f"Students added to: {class_assignment if class_assignment != 'Create New Class...' else new_class_name}"
                        )

                        # Show summary
                        st.markdown("#### Import Summary:")
                        st.write(f"- **Total students:** {len(df)}")
                        st.write(f"- **Students with IEPs:** {iep_count}")
                        st.write(f"- **Failed imports:** 0")

                        if iep_count > 0:
                            st.warning(
                                f"⚠️ {iep_count} students flagged for IEP setup. Visit the IEP Manager to complete accommodations."
                            )
                            if st.button("Go to IEP Manager →"):
                                st.switch_page("pages/4_IEP_Manager.py")

                        st.balloons()

        except Exception as e:
            st.error(f"❌ Error processing CSV file: {str(e)}")
            st.info("Please check that your file matches the template format.")

    else:
        st.info("👆 Upload a CSV file to preview and import students")

# ═══════════════════════════════════════════════════════════
# TAB 2: MANUAL STUDENT ADDITION
# ═══════════════════════════════════════════════════════════

with tab2:
    st.markdown("## ➕ Add Individual Student")
    st.info("Manually add a single student to your class roster.")

    st.divider()

    # Student form
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👤 Basic Information")

        manual_name = st.text_input("Student Name *", placeholder="First Last")
        manual_student_id = st.text_input(
            "Student ID",
            placeholder="Auto-generated if blank",
            help="Unique identifier (optional)",
        )
        manual_grade = st.selectbox("Grade Level *", options=["9", "10", "11", "12"])
        manual_class = st.selectbox(
            "Assign to Class *",
            options=["Period 3 Biology", "Period 5 Chemistry", "Period 7 Physics"],
        )

    with col2:
        st.markdown("### 📚 Academic Profile")

        manual_reading = st.selectbox(
            "Reading Level",
            options=["Below Basic", "Basic", "Proficient", "Advanced"],
            index=2,
            help="Current reading proficiency",
        )

        manual_learning_prefs = st.multiselect(
            "Learning Preferences",
            options=["Visual", "Auditory", "Reading/Writing", "Kinesthetic"],
            default=["Visual"],
            help="Primary learning modalities (VARK)",
        )

    st.divider()

    # IEP section
    st.markdown("### 📋 IEP / Special Education")

    manual_has_iep = st.checkbox("Student has an IEP or 504 Plan")

    if manual_has_iep:
        col1, col2 = st.columns(2)

        with col1:
            manual_disability = st.selectbox(
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
            st.write("**Quick Accommodations:**")
            manual_extended_time = st.checkbox("Extended Time")
            manual_text_to_speech = st.checkbox("Text-to-Speech")
            manual_graphic_org = st.checkbox("Graphic Organizers")

        st.info(
            "💡 Complete accommodation setup in the IEP Manager after creating the student profile."
        )

    st.divider()

    # Submit button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("➕ Add Student", type="primary", use_container_width=True):
            if not manual_name:
                st.error("❌ Student name is required!")
            else:
                # In production: POST /api/v1/students
                st.success(f"✅ {manual_name} added to {manual_class}!")

                if manual_has_iep:
                    st.warning("📋 Don't forget to complete IEP setup in the IEP Manager")

                st.balloons()

# ═══════════════════════════════════════════════════════════
# TAB 3: SYSTEM PREFERENCES
# ═══════════════════════════════════════════════════════════

with tab3:
    st.markdown("## ⚙️ System Preferences")
    st.info("Configure default settings for lesson generation and system behavior.")

    st.divider()

    # Lesson generation defaults
    st.markdown("### 📝 Lesson Generation Defaults")

    col1, col2 = st.columns(2)

    with col1:
        default_duration = st.selectbox(
            "Default Lesson Duration",
            options=["30 minutes", "45 minutes", "60 minutes", "90 minutes"],
            index=1,
            help="Pre-fill this duration in lesson generator",
        )

        default_subject = st.selectbox(
            "Default Subject",
            options=["English Language Arts", "Mathematics", "Science", "Social Studies", "Elective"],
            index=2,
        )

    with col2:
        default_grade = st.selectbox(
            "Default Grade Level",
            options=["9", "10", "11", "12"],
            index=0,
        )

        enable_unit_planner = st.checkbox(
            "Show Unit Planner by default",
            value=False,
            help="Expand unit planner section on lesson generator page",
        )

    st.divider()

    # Tier assignment logic
    st.markdown("### 🎯 Tier Assignment Logic")
    st.caption("How should students be assigned to differentiation tiers?")

    tier_logic = st.radio(
        "Assignment Mode:",
        options=[
            "Automatic (Engine 5 assigns based on mastery)",
            "Manual (Teacher assigns all students)",
            "Hybrid (Engine suggests, teacher approves)",
        ],
        index=0,
        help="Determines how students are placed into Tier 1, 2, or 3",
    )

    if "Automatic" in tier_logic:
        col1, col2 = st.columns(2)
        with col1:
            tier1_threshold = st.slider(
                "Tier 1 Minimum Mastery", min_value=60, max_value=90, value=75, step=5, help=">= this % → Tier 1"
            )
        with col2:
            tier3_threshold = st.slider(
                "Tier 3 Maximum Mastery", min_value=30, max_value=60, value=45, step=5, help="<= this % → Tier 3"
            )

        st.caption(f"Tier 2 range: {tier3_threshold+1}% to {tier1_threshold-1}%")

    st.divider()

    # Export preferences
    st.markdown("### 📥 Export Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Export Formats:**")
        export_pdf = st.checkbox("PDF", value=True)
        export_docx = st.checkbox("DOCX (Word)", value=True)
        export_gdocs = st.checkbox("Google Docs", value=False)

    with col2:
        st.write("**Export Options:**")
        include_answer_key = st.checkbox("Include answer keys", value=True)
        separate_tiers = st.checkbox("Export tiers as separate files", value=False)

    st.divider()

    # Display preferences
    st.markdown("### 🎨 Display Preferences")

    col1, col2 = st.columns(2)

    with col1:
        theme_mode = st.selectbox("Theme", options=["Light", "Dark", "Auto (system)"], index=0)

        show_concept_ids = st.checkbox(
            "Show concept IDs in dashboards",
            value=False,
            help="Display technical concept identifiers for debugging",
        )

    with col2:
        date_format = st.selectbox(
            "Date Format", options=["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"], index=0
        )

        enable_animations = st.checkbox("Enable animations (balloons, confetti)", value=True)

    st.divider()

    # API and performance
    st.markdown("### ⚡ Performance & Cost Settings")

    col1, col2 = st.columns(2)

    with col1:
        enable_caching = st.checkbox(
            "Enable prompt caching",
            value=True,
            help="Reduces API costs by caching repeated prompts",
        )

        max_cost_per_lesson = st.number_input(
            "Max cost per lesson ($)",
            min_value=0.10,
            max_value=2.00,
            value=0.50,
            step=0.10,
            help="Stop generation if cost exceeds this limit",
        )

    with col2:
        enable_rate_limiting = st.checkbox("Enable rate limiting", value=True)

        concurrent_students = st.number_input(
            "Max concurrent students",
            min_value=10,
            max_value=500,
            value=2250,
            step=10,
            help="Maximum simultaneous student data queries",
        )

    st.divider()

    # Compliance settings
    st.markdown("### ⚖️ Compliance & Privacy")

    col1, col2 = st.columns(2)

    with col1:
        enable_audit_logs = st.checkbox(
            "Enable audit trails (FERPA)",
            value=True,
            disabled=True,
            help="Required for FERPA compliance (cannot disable)",
        )

        enable_encryption = st.checkbox(
            "Encrypt PII at rest",
            value=True,
            disabled=True,
            help="Required for data security (cannot disable)",
        )

    with col2:
        data_retention_days = st.number_input(
            "Data retention (days)",
            min_value=30,
            max_value=730,
            value=365,
            step=30,
            help="How long to keep assessment history",
        )

        require_parent_consent = st.checkbox(
            "Require parental consent (COPPA)",
            value=True,
            help="For students under 13 years old",
        )

    st.divider()

    # Save button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("💾 Save All Settings", type="primary", use_container_width=True):
            # In production: PUT /api/v1/settings
            st.success("✅ Settings saved successfully!")
            st.info("Changes will take effect immediately.")
            st.balloons()

    st.divider()

    # Reset defaults
    with st.expander("🔄 Reset to Defaults", expanded=False):
        st.warning(
            "⚠️ This will reset ALL settings to factory defaults. This action cannot be undone."
        )
        if st.button("Reset All Settings", type="secondary"):
            st.error("Settings reset to defaults")

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.write("Configure system preferences and manage student rosters.")

    st.markdown("---")

    st.markdown("#### 📊 Account Info")
    st.write("**Teacher:** Demo User")
    st.write("**School:** Pilot School #1")
    st.write("**License:** Pilot Program")
    st.write("**API Budget:** $850 remaining")

    st.markdown("---")

    st.markdown("#### 🔗 Quick Actions")
    if st.button("📝 Generate Lesson", use_container_width=True):
        st.switch_page("pages/1_Generate_Lesson.py")
    if st.button("👥 Student Dashboard", use_container_width=True):
        st.switch_page("pages/3_Student_Dashboard.py")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")

    st.markdown("---")

    st.markdown("#### 💡 Tips")
    st.info(
        """
        - Import rosters before generating lessons
        - Complete IEP setup for accurate tier assignment
        - Enable prompt caching to reduce costs
        - Check audit logs regularly for compliance
        """
    )
