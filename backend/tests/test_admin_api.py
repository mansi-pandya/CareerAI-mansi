import unittest
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.auth.dependencies import get_current_user
from app.core.security import create_access_token
from app.database.database import Base
from app.models.user import User, Role
from app.models.profile import StudentProfile
from app.models.jobs import Job, JobSource, SavedJob
from app.models.interviews import Interview
from app.models.resume import Resume, ATSScore
from app.models.opportunities import OpportunityCheck


class AdminApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        def override_get_db():
            db = self.Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides.clear()
        app.dependency_overrides.update({__import__("app.database.database", fromlist=["get_db"]).get_db: override_get_db})

        with self.Session() as db:
            admin = User(
                full_name="Admin User",
                email="admin@example.com",
                hashed_password="hashed",
                role=Role.admin,
                is_active=True,
            )
            student = User(
                full_name="Student User",
                email="student@example.com",
                hashed_password="hashed",
                role=Role.student,
                is_active=True,
            )
            db.add_all([admin, student])
            db.flush()
            db.add(StudentProfile(user_id=student.id, is_profile_complete=True))
            db.add(JobSource(name="Demo", slug="demo", is_active=True))
            db.flush()
            db.add(Job(
                source_id=1,
                title="Developer",
                company="Example",
                location="Remote",
                description="Example",
            ))
            db.flush()
            db.add_all([
                Resume(user_id=student.id, title="Resume"),
                SavedJob(user_id=student.id, job_id=1),
                Interview(user_id=student.id, target_career="Developer", status="in_progress"),
                OpportunityCheck(user_id=student.id, input_type="text", raw_input="Example"),
            ])
            db.flush()
            db.add(ATSScore(resume_id=1, overall_score=85.0, structure_score=90.0, formatting_score=80.0,
                             keyword_score=85.0, skills_score=90.0, projects_score=80.0,
                             experience_score=75.0, education_score=70.0, contact_score=90.0,
                             job_alignment_score=80.0))
            db.commit()

        self.admin_token = create_access_token({"sub": "1", "role": Role.admin.value})
        self.student_token = create_access_token({"sub": "2", "role": Role.student.value})
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_admin_overview_requires_admin_role(self):
        response = self.client.get(
            "/api/admin/overview",
            headers={"Authorization": f"Bearer {self.student_token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_overview_returns_aggregated_counts(self):
        response = self.client.get(
            "/api/admin/overview",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_students"], 1)
        self.assertEqual(data["active_users"], 2)
        self.assertGreater(data["resume_analyses"], 0)
        self.assertGreater(data["ats_analyses"], 0)
        self.assertGreater(data["job_searches"], 0)
        self.assertGreater(data["saved_jobs"], 0)
        self.assertGreater(data["opportunity_checks"], 0)
        self.assertGreater(data["interview_sessions"], 0)
        self.assertIn("popular_careers", data)
        self.assertIn("popular_skills", data)
        self.assertIn("common_skill_gaps", data)
        self.assertIn("verification_outcomes", data)
        self.assertIn("api_status", data)


if __name__ == "__main__":
    unittest.main()
