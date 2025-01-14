from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from django_orgs.models import Member, Org
from django_orgs.services import create_org

User = get_user_model()


class OrgModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.org = create_org(
            name="Test Organization",
            handle="test-org",
            description="A test organization",
            owner=self.user,
        )

    def test_org_creation(self):
        self.assertEqual(self.org.handle, "test-org")
        self.assertEqual(self.org.name, "Test Organization")
        self.assertEqual(self.org.description, "A test organization")
        # Test that owner was created
        member = Member.objects.get(org=self.org, user=self.user)
        self.assertEqual(member.role, Member.Roles.OWNER)
        self.assertIsNotNone(self.org.created_at)
        self.assertIsNotNone(self.org.updated_at)
        # Test related names
        self.assertEqual(list(self.user.members.all()), [self.org])
        self.assertEqual(list(self.org.members.all()), [self.user])

    def test_org_str_representation(self):
        self.assertEqual(str(self.org), "Test Organization")

    def test_unique_handle_constraint(self):
        # Try to create an org with the same handle
        with self.assertRaises(ValidationError):
            duplicate_org = Org(name="Duplicate Org", handle="test-org")
            duplicate_org.full_clean()

    def test_org_ordering(self):
        # Create another org with a name that should come first alphabetically
        another_org = create_org(
            name="Acme Organization",
            handle="acme-org",
            owner=self.user
        )
        orgs = list(Org.objects.all())
        self.assertEqual(orgs[0].name, "Acme Organization")
        self.assertEqual(orgs[1].name, "Test Organization")
