from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from django_orgs.models import Invite, Member
from django_orgs.services import (
    accept_invite,
    change_member_role,
    create_invite,
    create_member,
    create_org,
    expire_old_invites,
    get_org_by_handle,
    get_org_members,
    get_pending_invites,
    get_user_orgs,
    remove_member,
)

User = get_user_model()


class ServicesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.org = create_org(
            name="Test Organization",
            handle="test-org",
            description="A test organization",
            owner=self.user,
        )

    def test_create_org(self):
        org = create_org("New Org", "new-org", "Description")
        self.assertEqual(org.name, "New Org")
        self.assertEqual(org.handle, "new-org")
        self.assertEqual(org.description, "Description")
        self.assertEqual(org.members.count(), 0)

    def test_create_org_with_owner(self):
        org = create_org("New Org", "new-org", owner=self.other_user)
        member = Member.objects.get(org=org, user=self.other_user)
        self.assertEqual(member.role, Member.Roles.OWNER)

    def test_get_org_by_handle(self):
        self.assertEqual(get_org_by_handle("test-org"), self.org)
        self.assertIsNone(get_org_by_handle("nonexistent"))

    def test_create_member(self):
        member = create_member(self.org, self.other_user)
        self.assertEqual(member.org, self.org)
        self.assertEqual(member.user, self.other_user)
        self.assertEqual(member.role, Member.Roles.MEMBER)

    def test_remove_member(self):
        create_member(self.org, self.other_user)
        self.assertTrue(remove_member(self.org, self.other_user))
        self.assertFalse(
            Member.objects.filter(org=self.org, user=self.other_user).exists()
        )

    def test_change_member_role(self):
        member = create_member(self.org, self.other_user)
        updated_member = change_member_role(
            self.org, self.other_user, Member.Roles.ADMIN
        )
        self.assertEqual(updated_member.role, Member.Roles.ADMIN)
        
        # Test with nonexistent user
        self.assertIsNone(
            change_member_role(
                self.org, 
                User.objects.create(username="nonexistent"),
                Member.Roles.ADMIN
            )
        )

    def test_create_invite_with_email(self):
        invite = create_invite(self.org, email="new@example.com", user=None)
        self.assertEqual(invite.org, self.org)
        self.assertEqual(invite.email, "new@example.com")
        self.assertIsNone(invite.user)
        self.assertEqual(invite.status, Invite.Status.PENDING)

    def test_create_invite_with_user(self):
        invite = create_invite(self.org, user=self.other_user, email=None)
        self.assertEqual(invite.org, self.org)
        self.assertEqual(invite.user, self.other_user)
        self.assertIsNone(invite.email)
        self.assertEqual(invite.status, Invite.Status.PENDING)

    def test_create_invite_validation(self):
        with self.assertRaises(ValueError):
            create_invite(self.org)

    def test_accept_invite(self):
        # Test with email invite
        new_user = User.objects.create_user(
            username="newuser", email="new@example.com", password="testpass123"
        )
        invite = create_invite(self.org, email="new@example.com", user=None)
        member = accept_invite(invite.id)
        self.assertIsNotNone(member)
        self.assertEqual(member.org, self.org)
        self.assertEqual(member.user, new_user)

        # Test with user invite
        invite = create_invite(self.org, user=self.other_user, email=None)
        member = accept_invite(invite.id)
        self.assertIsNotNone(member)
        self.assertEqual(member.user, self.other_user)

        # Test with invalid invite
        with self.assertRaises(ValidationError):
            accept_invite("nonexistent")

    def test_expire_old_invites(self):
        # Create some old invites
        invite1 = create_invite(self.org, email="test1@example.com")
        invite2 = create_invite(self.org, email="test2@example.com")

        # Modify created_at to make them old
        Invite.objects.filter(id=invite1.id).update(
            created_at=timezone.now() - timezone.timedelta(days=10)
        )
        Invite.objects.filter(id=invite2.id).update(
            created_at=timezone.now() - timezone.timedelta(days=10)
        )

        expired_count = expire_old_invites(days=7)
        self.assertEqual(expired_count, 2)
        self.assertEqual(Invite.objects.filter(status=Invite.Status.EXPIRED).count(), 2)

    def test_get_user_orgs(self):
        org2 = create_org("Second Org", "org2", owner=self.user)
        orgs = get_user_orgs(self.user)
        self.assertEqual(orgs.count(), 2)
        self.assertIn(self.org, orgs)
        self.assertIn(org2, orgs)

    def test_get_org_members(self):
        create_member(self.org, self.other_user)
        members = get_org_members(self.org)
        self.assertEqual(members.count(), 2)  # owner + new member

    def test_get_pending_invites(self):
        create_invite(self.org, email="test1@example.com")
        create_invite(self.org, email="test2@example.com")
        invites = get_pending_invites(self.org)
        self.assertEqual(invites.count(), 2)
