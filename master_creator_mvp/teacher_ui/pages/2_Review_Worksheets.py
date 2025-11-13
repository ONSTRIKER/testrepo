"""
Master Creator v3 MVP - Page 2: Worksheet Review

Displays differentiated worksheets in 3 tiers (Engine 2 + 3 output):
- Tier 1: Light support (6 students)
- Tier 2: Moderate support (8 students, IEP accommodations)
- Tier 3: Heavy support (4 students, IEP accommodations)

Teachers can review, edit, reassign students, and export materials.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Review Worksheets - Master Creator v3",
    page_icon="📄",
    layout="wide",
)

# Header
st.title("📄 Review Differentiated Worksheets")
st.markdown("Three-tier scaffolded materials with IEP accommodations applied.")

# Mock worksheet data (in production, this comes from API)
# This simulates Engine 2 + Engine 3 output
mock_worksheet_data = {
    "worksheet_id": "ws_001",
    "lesson_topic": "Photosynthesis Process",
    "grade": "9",
    "class_name": "Period 3 Biology",
    "total_students": 18,
    "tier_1": {
        "tier_name": "Tier 1 - Light Support",
        "student_count": 6,
        "students": [
            {"name": "Alex Chen", "has_iep": False, "mastery": 0.85},
            {"name": "Jordan Rivera", "has_iep": False, "mastery": 0.78},
            {"name": "Sam Parker", "has_iep": False, "mastery": 0.82},
            {"name": "Taylor Kim", "has_iep": False, "mastery": 0.75},
            {"name": "Morgan Lee", "has_iep": False, "mastery": 0.80},
            {"name": "Casey Johnson", "has_iep": False, "mastery": 0.77},
        ],
        "questions": [
            {
                "number": 1,
                "type": "Constructed Response",
                "text": "Explain the role of chlorophyll in photosynthesis. Use the diagram below to support your answer.",
                "scaffolding": [
                    "Labeled diagram provided",
                    "Word bank: chlorophyll, light energy, glucose, carbon dioxide, oxygen",
                    "Expected 3-4 sentence response",
                ],
                "standards": "NGSS-HS-LS1-5",
            },
            {
                "number": 2,
                "type": "Multiple Choice",
                "text": "Which of the following best describes the relationship between photosynthesis and cellular respiration?",
                "options": [
                    "A) They are opposite processes that cycle matter and energy",
                    "B) They both produce glucose as their main product",
                    "C) They occur in different organisms and are unrelated",
                    "D) They both require sunlight to function",
                ],
                "scaffolding": ["Diagram showing both processes side-by-side"],
            },
            {
                "number": 3,
                "type": "Short Answer",
                "text": "Identify three inputs and three outputs of photosynthesis.",
                "scaffolding": ["Table format provided", "No word bank"],
            },
        ],
    },
    "tier_2": {
        "tier_name": "Tier 2 - Moderate Support",
        "student_count": 8,
        "students": [
            {
                "name": "Maria Gonzalez",
                "has_iep": True,
                "iep_accommodations": ["Extended Time (1.5x)", "Text-to-Speech", "Graphic Organizers"],
                "mastery": 0.55,
            },
            {
                "name": "Carlos Martinez",
                "has_iep": True,
                "iep_accommodations": ["Graphic Organizers", "Sentence Frames"],
                "mastery": 0.48,
            },
            {
                "name": "Aisha Patel",
                "has_iep": False,
                "mastery": 0.62,
            },
            {
                "name": "Jamal Washington",
                "has_iep": True,
                "iep_accommodations": ["Extended Time (1.5x)", "Word Bank"],
                "mastery": 0.51,
            },
            {
                "name": "Sofia Rodriguez",
                "has_iep": False,
                "mastery": 0.58,
            },
            {
                "name": "Liam O'Connor",
                "has_iep": True,
                "iep_accommodations": ["Calculator", "Visual Supports"],
                "mastery": 0.47,
            },
            {
                "name": "Priya Singh",
                "has_iep": False,
                "mastery": 0.61,
            },
            {
                "name": "Marcus Thompson",
                "has_iep": True,
                "iep_accommodations": ["Extended Time (1.5x)", "Reduced Questions"],
                "mastery": 0.49,
            },
        ],
        "questions": [
            {
                "number": 1,
                "type": "Fill in the Blank",
                "text": "Complete the following sentences about photosynthesis:\n\nChlorophyll is _______ (green/red) in color and helps plants _______ (make/eat) their own food. During photosynthesis, plants take in _______ (oxygen/carbon dioxide) and release _______ (oxygen/carbon dioxide).",
                "scaffolding": [
                    "Word bank with 6 terms provided",
                    "Color-coded diagram with labels",
                    "Sentence frames for support",
                ],
                "accommodations_applied": [
                    "Extended time enabled for Maria, Jamal, Marcus",
                    "Text-to-speech compatible formatting",
                    "Graphic organizer showing process flow",
                ],
            },
            {
                "number": 2,
                "type": "Matching",
                "text": "Match each part of the photosynthesis equation with its role:",
                "pairs": [
                    "Carbon Dioxide → Input (what goes in)",
                    "Glucose → Output (what comes out)",
                    "Light Energy → Energy source",
                    "Chloroplast → Where it happens",
                ],
                "scaffolding": ["Visual diagram", "Only 4 pairs instead of 6"],
            },
            {
                "number": 3,
                "type": "Short Answer with Frames",
                "text": "Use the sentence frame below to explain photosynthesis:\n\n'Plants use _______ from the sun and _______ from the air to make _______. This process is called _______ and it happens in the _______ of plant cells.'",
                "scaffolding": [
                    "Word bank: photosynthesis, chloroplasts, light energy, carbon dioxide, glucose",
                    "Labeled diagram of plant cell",
                ],
            },
        ],
        "iep_summary": "8 students • 5 with IEPs • Accommodations: Extended time (3), Graphic organizers (2), Text-to-speech (1)",
    },
    "tier_3": {
        "tier_name": "Tier 3 - Heavy Support",
        "student_count": 4,
        "students": [
            {
                "name": "David Kim",
                "has_iep": True,
                "iep_accommodations": [
                    "Text-to-Speech",
                    "Reduced Question Count",
                    "Visual Supports",
                    "Preferential Seating",
                ],
                "mastery": 0.32,
                "primary_disability": "ADHD + Processing Disorder",
            },
            {
                "name": "Emma Wilson",
                "has_iep": True,
                "iep_accommodations": [
                    "Reduced Question Count",
                    "Sentence Frames",
                    "Extended Time (2x)",
                ],
                "mastery": 0.28,
                "primary_disability": "Learning Disability",
            },
            {
                "name": "Tyler Brown",
                "has_iep": True,
                "iep_accommodations": [
                    "Visual Supports",
                    "Movement Breaks",
                    "Audio Recordings",
                ],
                "mastery": 0.35,
                "primary_disability": "Autism Spectrum Disorder",
            },
            {
                "name": "Isabella Garcia",
                "has_iep": True,
                "iep_accommodations": ["Text-to-Speech", "Graphic Organizers", "Calculator"],
                "mastery": 0.30,
                "primary_disability": "Intellectual Disability",
            },
        ],
        "questions": [
            {
                "number": 1,
                "type": "Visual Multiple Choice",
                "text": "Look at the picture of a green leaf. What color is the chlorophyll inside the leaf?",
                "options": [
                    {"text": "A) Green", "has_image": True},
                    {"text": "B) Red", "has_image": True},
                    {"text": "C) Blue", "has_image": True},
                ],
                "scaffolding": [
                    "Large, clear photograph with arrows",
                    "Only 3 options instead of 4",
                    "Picture for each answer choice",
                ],
                "accommodations_applied": [
                    "Text-to-speech enabled for David and Isabella",
                    "Visual supports emphasized for all students",
                ],
            },
            {
                "number": 2,
                "type": "Circle the Correct Picture",
                "text": "Which picture shows a plant making food from sunlight?",
                "scaffolding": [
                    "Three large pictures to choose from",
                    "Step-by-step instructions numbered",
                    "Read-aloud available",
                ],
            },
            {
                "number": 3,
                "type": "Fill in One Word",
                "text": "Plants make their food using light from the _______.",
                "options": ["sun", "moon", "ground"],
                "scaffolding": [
                    "Only one blank per question",
                    "Three word choices with pictures",
                    "Extra large font (18pt)",
                ],
            },
        ],
        "iep_summary": "4 students • All have IEPs • Disabilities: ADHD (1), LD (1), ASD (1), ID (1)",
        "special_notes": [
            "✅ All materials use visual supports",
            "✅ Question count reduced from 10 to 6",
            "✅ Text-to-speech enabled for 2 students",
            "✅ Movement breaks recommended every 15 minutes",
        ],
    },
}

# Display lesson information
st.info(
    f"**Lesson:** {mock_worksheet_data['lesson_topic']} (Grade {mock_worksheet_data['grade']})  \n"
    f"**Class:** {mock_worksheet_data['class_name']} ({mock_worksheet_data['total_students']} students)"
)

st.divider()

# ═══════════════════════════════════════════════════════════
# THREE-TIER TABS
# ═══════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs(
    [
        f"📗 Tier 1 - Light Support ({mock_worksheet_data['tier_1']['student_count']} students)",
        f"📘 Tier 2 - Moderate Support ({mock_worksheet_data['tier_2']['student_count']} students)",
        f"📕 Tier 3 - Heavy Support ({mock_worksheet_data['tier_3']['student_count']} students)",
    ]
)

# ───────────────────────────────────────────────────────────
# TAB 1: TIER 1 (LIGHT SUPPORT)
# ───────────────────────────────────────────────────────────

with tab1:
    tier_data = mock_worksheet_data["tier_1"]

    st.markdown(f"### {tier_data['tier_name']}")
    st.markdown("**Target:** Students with 75%+ mastery, minimal scaffolding needed")

    # Student list
    st.markdown("#### 👥 Students in Tier 1")
    cols = st.columns(3)
    for idx, student in enumerate(tier_data["students"]):
        with cols[idx % 3]:
            mastery_color = "🟢" if student["mastery"] >= 0.8 else "🟡"
            st.write(f"{mastery_color} **{student['name']}** ({student['mastery']*100:.0f}% mastery)")

    st.divider()

    # Questions
    st.markdown("#### 📝 Worksheet Questions")

    for q in tier_data["questions"]:
        with st.expander(f"**Question {q['number']}** - {q['type']}", expanded=True):
            st.markdown(f"**{q['text']}**")

            if q["type"] == "Multiple Choice" and "options" in q:
                for option in q["options"]:
                    st.write(option)

            # Scaffolding provided
            st.markdown("**Scaffolding:**")
            for scaffold in q["scaffolding"]:
                st.write(f"• {scaffold}")

            # Edit button
            if st.button(f"✏️ Edit Question {q['number']}", key=f"edit_t1_q{q['number']}"):
                st.info("Inline editor will open here in production version")

    st.divider()

    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("♻️ Reassign Students to Different Tier", key="reassign_t1"):
            st.info("Student reassignment dialog will open")
    with col2:
        if st.button("📥 Export Tier 1 Worksheet (PDF)", key="export_t1"):
            st.success("Tier 1 worksheet exported!")

# ───────────────────────────────────────────────────────────
# TAB 2: TIER 2 (MODERATE SUPPORT)
# ───────────────────────────────────────────────────────────

with tab2:
    tier_data = mock_worksheet_data["tier_2"]

    st.markdown(f"### {tier_data['tier_name']}")
    st.markdown("**Target:** Students with 45-75% mastery, moderate scaffolding and IEP support")

    # IEP summary badge
    st.info(f"📋 **IEP Summary:** {tier_data['iep_summary']}")

    # Student list with IEP badges
    st.markdown("#### 👥 Students in Tier 2")

    for student in tier_data["students"]:
        with st.container():
            col1, col2 = st.columns([3, 5])
            with col1:
                mastery_color = "🟡" if student["mastery"] >= 0.5 else "🔴"
                iep_badge = "📋 IEP" if student["has_iep"] else ""
                st.write(f"{mastery_color} **{student['name']}** {iep_badge}")
                st.caption(f"Mastery: {student['mastery']*100:.0f}%")

            with col2:
                if student["has_iep"] and "iep_accommodations" in student:
                    st.caption("**Accommodations:**")
                    for accom in student["iep_accommodations"]:
                        st.caption(f"✅ {accom}")

    st.divider()

    # Questions
    st.markdown("#### 📝 Worksheet Questions")

    for q in tier_data["questions"]:
        with st.expander(f"**Question {q['number']}** - {q['type']}", expanded=True):
            st.markdown(f"**{q['text']}**")

            if "pairs" in q:
                st.write("*Match the following:*")
                for pair in q["pairs"]:
                    st.write(f"• {pair}")

            # Scaffolding
            st.markdown("**Scaffolding Provided:**")
            for scaffold in q["scaffolding"]:
                st.write(f"• {scaffold}")

            # IEP accommodations applied
            if "accommodations_applied" in q:
                st.markdown("**🎯 IEP Accommodations Applied:**")
                for accom in q["accommodations_applied"]:
                    st.success(f"✅ {accom}")

            if st.button(f"✏️ Edit Question {q['number']}", key=f"edit_t2_q{q['number']}"):
                st.info("Inline editor will open here")

    st.divider()

    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("♻️ Reassign Students", key="reassign_t2"):
            st.info("Student reassignment dialog will open")
    with col2:
        if st.button("📋 View Individual IEP Modifications", key="view_iep_t2"):
            st.info("This will show per-student modifications from Engine 3")
    with col3:
        if st.button("📥 Export Tier 2 (PDF)", key="export_t2"):
            st.success("Tier 2 worksheet exported!")

# ───────────────────────────────────────────────────────────
# TAB 3: TIER 3 (HEAVY SUPPORT)
# ───────────────────────────────────────────────────────────

with tab3:
    tier_data = mock_worksheet_data["tier_3"]

    st.markdown(f"### {tier_data['tier_name']}")
    st.markdown("**Target:** Students with <45% mastery, maximum scaffolding and intensive IEP support")

    # IEP summary badge (highlighted)
    st.error(f"📋 **IEP Summary:** {tier_data['iep_summary']}")

    # Special notes
    st.markdown("#### ⚠️ Special Accommodations Applied")
    for note in tier_data["special_notes"]:
        st.write(note)

    st.divider()

    # Student list with detailed IEP info
    st.markdown("#### 👥 Students in Tier 3")

    for student in tier_data["students"]:
        with st.expander(f"📋 {student['name']} (Mastery: {student['mastery']*100:.0f}%)", expanded=False):
            st.write(f"**Primary Disability:** {student.get('primary_disability', 'Not specified')}")
            st.write(f"**Current Mastery:** {student['mastery']*100:.0f}%")

            st.markdown("**Active IEP Accommodations:**")
            for accom in student["iep_accommodations"]:
                st.success(f"✅ {accom}")

            if st.button(f"🔍 View Full IEP Details", key=f"view_iep_{student['name']}"):
                st.info("This will open the full IEP page (Page 4)")

    st.divider()

    # Questions (simplified, visual)
    st.markdown("#### 📝 Worksheet Questions (Simplified)")

    for q in tier_data["questions"]:
        with st.expander(f"**Question {q['number']}** - {q['type']}", expanded=True):
            st.markdown(f"**{q['text']}**")

            if "options" in q:
                st.write("*Choose one:*")
                for option in q["options"]:
                    if isinstance(option, dict):
                        icon = "🖼️" if option.get("has_image") else ""
                        st.write(f"{icon} {option['text']}")
                    else:
                        st.write(f"• {option}")

            # Scaffolding (heavy)
            st.markdown("**Scaffolding Provided:**")
            for scaffold in q["scaffolding"]:
                st.write(f"• {scaffold}")

            # IEP accommodations
            if "accommodations_applied" in q:
                st.markdown("**🎯 IEP Accommodations:**")
                for accom in q["accommodations_applied"]:
                    st.success(f"✅ {accom}")

            if st.button(f"✏️ Edit Question {q['number']}", key=f"edit_t3_q{q['number']}"):
                st.info("Inline editor will open here")

    st.divider()

    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("♻️ Reassign Students", key="reassign_t3"):
            st.info("Reassignment requires IEP team approval")
    with col2:
        if st.button("📋 View Per-Student Modifications", key="view_mods_t3"):
            st.info("This shows Engine 3 individualized modifications")
    with col3:
        if st.button("📥 Export Tier 3 (PDF)", key="export_t3"):
            st.success("Tier 3 worksheet exported!")

# ═══════════════════════════════════════════════════════════
# BOTTOM ACTIONS (ACROSS ALL TIERS)
# ═══════════════════════════════════════════════════════════

st.divider()
st.markdown("### 🚀 Finalize & Share")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📦 Export All Tiers as PDF", type="primary", use_container_width=True):
        st.success("✅ All 3 tiers exported as single PDF package!")
        st.info("Teachers receive: worksheet_photosynthesis_all_tiers.pdf (32 pages)")

with col2:
    if st.button("🖨️ Print All Worksheets", use_container_width=True):
        st.info("Print dialog will open with tier-separated sections")

with col3:
    if st.button("📧 Email to Students", use_container_width=True):
        st.info("Email functionality will send tier-appropriate materials to each student")

with col4:
    if st.button("➡️ Continue to Student Dashboard", use_container_width=True):
        st.switch_page("pages/3_Student_Dashboard.py")

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 📄 Worksheet Review")
    st.write("Review differentiated materials before distributing to students.")

    st.markdown("---")

    st.markdown("#### 📊 Tier Distribution")
    st.metric("Tier 1 (Light)", "6 students", delta="33%")
    st.metric("Tier 2 (Moderate)", "8 students", delta="44%")
    st.metric("Tier 3 (Heavy)", "4 students", delta="22%")

    st.markdown("---")

    st.markdown("#### 💡 Teacher Tips")
    st.info(
        """
        - **Tier placement** is based on current mastery (Engine 5)
        - **IEP accommodations** are automatically applied (Engine 3)
        - **Same learning objective** across all tiers, different scaffolds
        - Students can move between tiers as mastery improves
        """
    )

    st.markdown("---")

    st.markdown("#### 🔗 Quick Actions")
    if st.button("🔙 Back to Lesson Generator", use_container_width=True):
        st.switch_page("pages/1_Generate_Lesson.py")
    if st.button("📋 View IEP Details", use_container_width=True):
        st.switch_page("pages/4_IEP_Manager.py")
