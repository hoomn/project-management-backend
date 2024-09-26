from django.test import TestCase

from accounts.models import User
from pm.models import Domain, Project


class TestCase(TestCase):
    def setUp(self):

        # Create a test user
        self.user = User.objects.create_user(email="test_user@test.com", password="12345")

        Domain.objects.create(title="domain 1", description="test domain one")
        domain_one = Domain.objects.get(title="domain 1")

        Project.objects.create(
            domain=domain_one, title="project 1", description="test project one", created_by=self.user
        )
        Project.objects.create(
            domain=domain_one, title="project 2", description="test project two", created_by=self.user
        )

    def test_domain_description(self):
        """Domain with correct description identified"""
        domain_one = Domain.objects.get(title="domain 1")
        self.assertEqual(domain_one.description, "test domain one")

    def test_projects_description(self):
        """Projects with correct description identified"""
        project_one = Project.objects.get(title="project 1")
        project_two = Project.objects.get(title="project 2")
        self.assertEqual(project_one.description, "test project one")
        self.assertEqual(project_two.description, "test project two")
