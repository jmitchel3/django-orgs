from __future__ import annotations

from django.test import TestCase, override_settings

from django_orgs.conf import Settings, get_settings, settings


class SettingsTests(TestCase):
    def test_singleton_settings(self):
        """Test that get_settings returns the same instance"""
        settings1 = get_settings()
        settings2 = get_settings()
        self.assertIs(settings1, settings2)
        self.assertIs(settings, settings1)

    def test_default_settings(self):
        """Test default values for all settings"""
        s = Settings()

        self.assertEqual(s.DJANGO_ORGS_ORG_MEMBERS_RELATED_NAME, "members")
        self.assertEqual(s.DJANGO_ORGS_MEMBER_ORG_RELATED_NAME, "organization")
        self.assertEqual(s.DJANGO_ORGS_MEMBER_USER_RELATED_NAME, "organization_memberships")
        self.assertEqual(s.DJANGO_ORGS_INVITES_RELATED_NAME, "invites")

    @override_settings(
        DJANGO_ORGS_ORG_MEMBERS_RELATED_NAME="custom_members",
        DJANGO_ORGS_MEMBER_ORG_RELATED_NAME="custom_org",
        DJANGO_ORGS_MEMBER_USER_RELATED_NAME="custom_memberships",
        DJANGO_ORGS_INVITES_RELATED_NAME="custom_invites",
    )
    def test_custom_settings(self):
        """Test that custom settings override defaults"""
        s = Settings()

        self.assertEqual(s.DJANGO_ORGS_ORG_MEMBERS_RELATED_NAME, "custom_members")
        self.assertEqual(s.DJANGO_ORGS_MEMBER_ORG_RELATED_NAME, "custom_org")
        self.assertEqual(s.DJANGO_ORGS_MEMBER_USER_RELATED_NAME, "custom_memberships")
        self.assertEqual(s.DJANGO_ORGS_INVITES_RELATED_NAME, "custom_invites")
