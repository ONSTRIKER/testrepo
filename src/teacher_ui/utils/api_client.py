"""API client for Teacher UI to communicate with FastAPI backend."""

import requests
from typing import Dict, List, Optional, Any
import os


class APIClient:
    """Client for making API requests to the backend."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize API client.

        Args:
            base_url: Base URL for API. Defaults to environment variable or localhost.
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_prefix = "/api/v1"
        self.timeout = 300  # 5 minutes for AI generation tasks

    def _get_url(self, endpoint: str) -> str:
        """Construct full URL for endpoint."""
        return f"{self.base_url}{self.api_prefix}{endpoint}"

    # ==================== ENGINE 0: UNIT PLANNER ====================

    def generate_unit(
        self,
        topic: str,
        duration: int,
        grade: int,
        subject: str,
        standards: List[str]
    ) -> Dict[str, Any]:
        """Generate a multi-lesson unit plan.

        Args:
            topic: Unit topic
            duration: Number of days (3, 5, 7, or 10)
            grade: Grade level (9-12)
            subject: Subject area
            standards: List of standards to address

        Returns:
            Unit plan with daily lesson outlines
        """
        payload = {
            "topic": topic,
            "duration": duration,
            "grade": grade,
            "subject": subject,
            "standards": standards
        }
        response = requests.post(
            self._get_url("/generate-unit"),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== ENGINE 1: LESSON GENERATOR ====================

    def generate_lesson(
        self,
        topic: str,
        grade: int,
        subject: str,
        standards: List[str],
        duration: int,
        class_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a single lesson plan.

        Args:
            topic: Lesson topic
            grade: Grade level (9-12)
            subject: Subject area
            standards: Standards to address
            duration: Lesson duration in minutes
            class_id: Optional class roster ID

        Returns:
            Complete lesson plan with 10 sections
        """
        payload = {
            "topic": topic,
            "grade": grade,
            "subject": subject,
            "standards": standards,
            "duration": duration,
            "class_id": class_id
        }
        response = requests.post(
            self._get_url("/generate-lesson"),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== ENGINE 5: DIAGNOSTIC ASSESSMENT ====================

    def run_diagnostic(
        self,
        lesson_id: str,
        class_id: str
    ) -> Dict[str, Any]:
        """Run diagnostic assessment for a class.

        Args:
            lesson_id: ID of the lesson
            class_id: ID of the class roster

        Returns:
            Diagnostic results with student readiness levels
        """
        payload = {
            "lesson_id": lesson_id,
            "class_id": class_id
        }
        response = requests.post(
            self._get_url("/run-diagnostic"),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== ENGINES 2 & 3: WORKSHEET GENERATION ====================

    def generate_worksheet(
        self,
        lesson_id: str,
        class_id: str,
        tier: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate differentiated worksheets.

        Args:
            lesson_id: ID of the lesson
            class_id: ID of the class roster
            tier: Optional specific tier (1, 2, or 3)

        Returns:
            Worksheet(s) with tier-specific content
        """
        payload = {
            "lesson_id": lesson_id,
            "class_id": class_id,
            "tier": tier
        }
        response = requests.post(
            self._get_url("/generate-worksheet"),
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_worksheet(self, worksheet_id: str) -> Dict[str, Any]:
        """Retrieve a generated worksheet.

        Args:
            worksheet_id: ID of the worksheet

        Returns:
            Worksheet data
        """
        response = requests.get(
            self._get_url(f"/worksheet/{worksheet_id}"),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def update_worksheet(
        self,
        worksheet_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update worksheet content.

        Args:
            worksheet_id: ID of the worksheet
            updates: Dictionary of updates to apply

        Returns:
            Updated worksheet data
        """
        response = requests.put(
            self._get_url(f"/worksheet/{worksheet_id}"),
            json=updates,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def export_worksheet(
        self,
        worksheet_id: str,
        format: str = "pdf"
    ) -> bytes:
        """Export worksheet to file.

        Args:
            worksheet_id: ID of the worksheet
            format: Export format ('pdf' or 'docx')

        Returns:
            File content as bytes
        """
        response = requests.post(
            self._get_url("/worksheet/export"),
            json={"worksheet_id": worksheet_id, "format": format},
            timeout=60
        )
        response.raise_for_status()
        return response.content

    # ==================== STUDENT DASHBOARD ====================

    def get_class_dashboard(self, class_id: str) -> Dict[str, Any]:
        """Get class overview dashboard data.

        Args:
            class_id: ID of the class

        Returns:
            Class mastery distribution and alerts
        """
        response = requests.get(
            self._get_url(f"/students/{class_id}/dashboard"),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        """Get individual student profile.

        Args:
            student_id: ID of the student

        Returns:
            Student profile with recent assessments
        """
        response = requests.get(
            self._get_url(f"/students/{student_id}/profile"),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_student_mastery(self, student_id: str) -> Dict[str, Any]:
        """Get student mastery levels.

        Args:
            student_id: ID of the student

        Returns:
            Mastery data by concept
        """
        response = requests.get(
            self._get_url(f"/students/{student_id}/mastery"),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    # ==================== IEP MANAGEMENT ====================

    def get_student_iep(self, student_id: str) -> Dict[str, Any]:
        """Get student IEP details.

        Args:
            student_id: ID of the student

        Returns:
            IEP accommodations and modifications
        """
        response = requests.get(
            self._get_url(f"/students/{student_id}/iep"),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def update_student_iep(
        self,
        student_id: str,
        iep_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update student IEP.

        Args:
            student_id: ID of the student
            iep_data: IEP data to update

        Returns:
            Updated IEP data
        """
        response = requests.put(
            self._get_url(f"/students/{student_id}/iep"),
            json=iep_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_accommodation_templates(self) -> List[Dict[str, Any]]:
        """Get available accommodation templates.

        Returns:
            List of accommodation templates
        """
        response = requests.get(
            self._get_url("/accommodations/templates"),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    # ==================== ROSTER & SETTINGS ====================

    def import_students(self, csv_file) -> Dict[str, Any]:
        """Import students from CSV file.

        Args:
            csv_file: CSV file object

        Returns:
            Import results
        """
        files = {"file": csv_file}
        response = requests.post(
            self._get_url("/students/import"),
            files=files,
            timeout=60
        )
        response.raise_for_status()
        return response.json()

    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update system settings.

        Args:
            settings: Settings to update

        Returns:
            Updated settings
        """
        response = requests.put(
            self._get_url("/settings"),
            json=settings,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_settings(self) -> Dict[str, Any]:
        """Get current system settings.

        Returns:
            Current settings
        """
        response = requests.get(
            self._get_url("/settings"),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_classes(self) -> List[Dict[str, Any]]:
        """Get list of all classes.

        Returns:
            List of class rosters
        """
        response = requests.get(
            self._get_url("/classes"),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
