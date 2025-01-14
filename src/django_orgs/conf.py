from __future__ import annotations

from functools import lru_cache

from django.conf import settings as django_settings


class Settings:
    """
    Shadow Django's settings with a little logic
    """

    @property
    def DJANGO_ORGS_ORG_MEMBERS_RELATED_NAME(self) -> str:
        """
        The related name for the orgs
        """
        return getattr(django_settings, "DJANGO_ORGS_ORG_MEMBERS_RELATED_NAME", "members")

    
    @property
    def DJANGO_ORGS_MEMBER_ORG_RELATED_NAME(self) -> str:
        """
        The related name for the members
        e.g. org.members.first().org
        """
        return getattr(django_settings, "DJANGO_ORGS_MEMBER_ORG_RELATED_NAME", "organization")


    @property
    def DJANGO_ORGS_MEMBER_USER_RELATED_NAME(self) -> str:
        """
        The related name for the members
        e.g. user.organization_memberships.all()
        """
        return getattr(django_settings, "DJANGO_ORGS_MEMBER_USER_RELATED_NAME", "organization_memberships")

    @property
    def DJANGO_ORGS_INVITES_RELATED_NAME(self) -> str:
        """
        The related name for the org invites
        """
        return getattr(django_settings, "DJANGO_ORGS_INVITES_RELATED_NAME", "invites")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
