from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from django_orgs.models import Invite, Member, Org

User = get_user_model()


# Organization Services
def create_org(
    name: str, handle: str, description: str = "", owner: User = None
) -> Org:
    """Create a new organization and optionally assign an owner."""
    with transaction.atomic():
        org = Org.objects.create(name=name, handle=handle, description=description)
        if owner:
            create_member(org, owner, Member.Roles.OWNER)
        return org


def get_org_by_handle(handle: str) -> Optional[Org]:
    """Get organization by handle."""
    return Org.objects.filter(handle=handle).first()


# Membership Services
def create_member(org: Org, user: User, role: str = Member.Roles.MEMBER) -> Member:
    """Add a user as a member to an organization."""
    return Member.objects.create(org=org, user=user, role=role)


def remove_member(org: Org, user: User) -> bool:
    """Remove a user from an organization."""
    deleted, _ = Member.objects.filter(org=org, user=user).delete()
    return deleted > 0


def change_member_role(org: Org, user: User, new_role: str) -> Optional[Member]:
    """Change a member's role in the organization."""
    member = Member.objects.filter(org=org, user=user).first()
    if member:
        member.role = new_role
        member.save()
    return member


# Invite Services
def create_invite(org: Org, email: str = None, user: User = None) -> Invite:
    """Create an invitation for a user or email address."""
    if not email and not user:
        raise ValueError("Either email or user must be provided")

    return Invite.objects.create(
        org=org,
        email=email,
        user=user,
        status=Invite.Status.PENDING
    )


def accept_invite(invite_id: str) -> Optional[Member]:
    """Accept an organization invitation."""
    with transaction.atomic():
        invite = (
            Invite.objects.select_for_update()
            .filter(id=invite_id, status=Invite.Status.PENDING)
            .first()
        )

        if not invite:
            return None

        invite.status = Invite.Status.ACCEPTED
        invite.save()

        return create_member(
            invite.org, invite.user or User.objects.get(email=invite.email)
        )


def expire_old_invites(days: int = 7) -> int:
    """Expire invites older than specified days."""
    expiry_date = timezone.now() - timezone.timedelta(days=days)
    return Invite.objects.filter(
        created_at__lt=expiry_date, status=Invite.Status.PENDING
    ).update(status=Invite.Status.EXPIRED)


# Query Services
def get_user_orgs(user: User):
    """Get all organizations a user is a member of."""
    return Org.objects.filter(members=user)


def get_org_members(org: Org):
    """Get all members of an organization."""
    return Member.objects.filter(org=org)


def get_pending_invites(org: Org):
    """Get all pending invites for an organization."""
    return Invite.objects.filter(org=org, status=Invite.Status.PENDING)
