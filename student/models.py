"""Models."""

from datetime import timedelta

from django.contrib.auth.models import Group
from django.db import models
from django.utils.timezone import now

from allianceauth.authentication.models import State
from allianceauth.eveonline.models import EveCharacter
from allianceauth.hrapplications.models import Application

from student.app_settings import STUDENTDAYS, STUDENTLIMIT


class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)


class AppConfig(models.Model):

    member_state = models.OneToOneField(
        State, on_delete=models.SET_NULL, null=True, blank=True, unique=True
    )

    student_title = models.OneToOneField(
        Group, on_delete=models.SET_NULL, null=True, blank=True, unique=True
    )

    def __str__(self):
        configs = []

        if self.member_state:
            configs.append(f"Member State: {self.member_state}")
        if self.student_title:
            configs.append(f"Title to apply: {self.student_title}")

        # Return a concatenated string of all active configurations
        return ", ".join(configs) if configs else "No Configuration Set"

    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configuration"


class CurrentMembers(models.Model):
    """A model for listing members who don't have the student title"""

    member = models.OneToOneField(EveCharacter, on_delete=models.CASCADE)

    member_app = models.OneToOneField(
        Application, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def filter_by_member_state_and_no_student_title(cls):
        """Returns members who are in member_state and do not have the student_title."""
        # Retrieve the current app configuration
        app_config = AppConfig.objects.first()
        if (
            not app_config
            or not app_config.member_state
            or not app_config.student_title
        ):
            return (
                cls.objects.none()
            )  # Return an empty queryset if the config is incomplete

        student_days_ago = now() - timedelta(days=STUDENTDAYS)

        # Filter members
        return cls.objects.filter(
            member__userprofile__state=app_config.member_state,
            created_date__lt=student_days_ago,
        ).exclude(member__userprofile__user__groups=app_config.student_title)[
            :STUDENTLIMIT
        ]

    @classmethod
    def filter_by_member_state_and_student_title(cls):
        """Returns members who are in member_state and have the student_title."""
        # Retrieve the current app configuration
        app_config = AppConfig.objects.first()
        if (
            not app_config
            or not app_config.member_state
            or not app_config.student_title
        ):
            return (
                cls.objects.none()
            )  # Return an empty queryset if the config is incomplete

        student_days_ago = now() - timedelta(days=STUDENTDAYS)

        # Filter members
        return cls.objects.filter(
            member__userprofile__state=app_config.member_state,
            created_date__lt=student_days_ago,
            member__userprofile__user__groups=app_config.student_title,
        )[:STUDENTLIMIT]

    @classmethod
    def exclude_by_member_state_or_with_student_title(cls):
        """Returns two querysets:
        1. Members who are not in member_state
        2. Members who have the student_title."""
        app_config = AppConfig.objects.first()
        if (
            not app_config
            or not app_config.member_state
            or not app_config.student_title
        ):
            return (
                cls.objects.none(),
                cls.objects.none(),
            )  # Return empty querysets if the config is incomplete

        student_days_ago = now() - timedelta(days=STUDENTDAYS)

        # Members not in member_state
        not_in_member_state = cls.objects.filter(
            created_date__lt=student_days_ago
        ).exclude(member__userprofile__state=app_config.member_state)

        # Members with student_title
        with_student_title = cls.objects.filter(
            member__userprofile__user__groups=app_config.student_title
        )

        return not_in_member_state, with_student_title

    def __str__(self) -> str:
        if self.member and self.member.character_name:
            return self.member.character_name
        return "No Character"

    class Meta:
        ordering = ["member__character_name"]
        verbose_name_plural = "Members without title"
