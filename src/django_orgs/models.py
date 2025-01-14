import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django import VERSION as DJANGO_VERSION

from django_orgs.conf import settings as django_orgs_settings


class Org(models.Model):
    id = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(_("Name"), max_length=200)
    handle = models.SlugField(
        _("Handle"),
        max_length=200,
        unique=True,
        help_text=_("The URL-ready handle for the organization"),
    )
    description = models.TextField(_("Description"), blank=True)

    # Members through a many-to-many relationship
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Member",
        related_name=django_orgs_settings.DJANGO_ORGS_ORG_MEMBERS_RELATED_NAME,
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Member(models.Model):
    class Roles(models.TextChoices):
        OWNER = "owner", _("Owner")
        ADMIN = "admin", _("Admin")
        MEMBER = "member", _("Member")

    id = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False, primary_key=True)

    org = models.ForeignKey(
        Org,
        on_delete=models.CASCADE,
        related_name=django_orgs_settings.DJANGO_ORGS_MEMBER_ORG_RELATED_NAME,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name=django_orgs_settings.DJANGO_ORGS_MEMBER_USER_RELATED_NAME,
    )
    role = models.CharField(
        _("Role"),
        max_length=20,
        choices=Roles.choices,
        default=Roles.MEMBER,
    )
    joined_at = models.DateTimeField(_("Joined at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Organization Membership")
        verbose_name_plural = _("Organization Memberships")
        unique_together = ["org", "user"]

    def __str__(self):
        return f"{self.user} - {self.org} ({self.role})"


INVITE_CHECK_CONSTRAINT = {
    'name': 'invite_has_email_xor_user',
    'condition': (models.Q(email__isnull=False, user__isnull=True) | 
    models.Q(email__isnull=True, user__isnull=False))
}
class Invite(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        ACCEPTED = "accepted", _("Accepted")
        EXPIRED = "expired", _("Expired")

    id = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False, primary_key=True)
    org = models.ForeignKey(
        Org,
        on_delete=models.CASCADE,
        related_name=django_orgs_settings.DJANGO_ORGS_INVITES_RELATED_NAME,
    )
    email = models.EmailField(_("Email"), blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="invites",
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Organization Invite")
        verbose_name_plural = _("Organization Invites")
        constraints = [
            models.UniqueConstraint(
                fields=["org", "email"],
                condition=models.Q(email__isnull=False),
                name="unique_org_email_invite",
            ),
            models.UniqueConstraint(
                fields=["org", "user"],
                condition=models.Q(user__isnull=False),
                name="unique_org_user_invite",
            ),
            models.CheckConstraint(
                name="invite_has_email_xor_user",
                condition=(models.Q(email__isnull=False, user__isnull=True) | 
                models.Q(email__isnull=True, user__isnull=False))
            ),
        ]
