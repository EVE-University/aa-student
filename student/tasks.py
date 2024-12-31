"""Tasks."""

import logging
from datetime import timedelta

from celery import shared_task

from django.db import transaction
from django.utils.timezone import now

from allianceauth.eveonline.models import EveCharacter

from student.app_settings import STUDENTDAYS
from student.models import AppConfig, CurrentMembers

logger = logging.getLogger(__name__)


@shared_task
def delete_excluded_members():
    """
    Deletes CurrentMembers who are not in member_state or belong to the student_title group
    only if they were created more than STUDENTDAYS ago.
    """
    # Get separate querysets for members to delete
    not_in_member_state, with_student_title = (
        CurrentMembers.exclude_by_member_state_or_with_student_title()
    )

    count_not_in_member_state = not_in_member_state.count()
    count_with_student_title = with_student_title.count()

    total_count = count_not_in_member_state + count_with_student_title

    # Log members to be deleted
    if total_count > 0:
        logger.info(
            f"{total_count} CurrentMembers will be deleted after being ineligible for {STUDENTDAYS} days."
        )
    else:
        logger.info("No CurrentMembers met the deletion criteria.")

    # Delete each group of members
    not_in_member_state.delete()
    with_student_title.delete()

    return f"{total_count} CurrentMembers were deleted after being ineligible for {STUDENTDAYS} days."


@shared_task
def give_title_to_all():
    """
    Give the title to all members older than three weeks. This is a single shot task, not to be run regularly.
    """

    student_days_ago = now() - timedelta(days=STUDENTDAYS + 7)

    # Retrieve the current app configuration
    app_config = AppConfig.objects.first()
    if not app_config or not app_config.member_state or not app_config.student_title:
        logger.error("Nothing to add, there is no active student config")
        return None

    members_queryset = EveCharacter.objects.filter(
        userprofile__state=app_config.member_state,
        userprofile__user__date_joined__lt=student_days_ago,
    ).exclude(userprofile__user__groups=app_config.student_title)

    batch_size = 100  # Number of records to process at once
    total_count = 0

    for batch_start in range(0, members_queryset.count(), batch_size):
        members_batch = members_queryset[batch_start : batch_start + batch_size]

        with transaction.atomic():  # Ensure database consistency in each batch
            for member in members_batch:
                member.userprofile.user.groups.add(app_config.student_title)
                member.save()
                total_count += 1

    logger.info(f"Processed {total_count} members.")
    return f"Processed {total_count} members."


@shared_task
def create_studentapp_for_nonstudent():
    """
    Create a student app for the rest of the members who are not old enough. This is a single shot task, not to be run regularly.
    """

    # Retrieve the current app configuration
    app_config = AppConfig.objects.first()
    if not app_config or not app_config.member_state or not app_config.student_title:
        logger.error("Nothing to add, there is no active student config")
        return None

    members_queryset = EveCharacter.objects.filter(
        userprofile__state=app_config.member_state,
    ).exclude(userprofile__user__groups=app_config.student_title)

    for member in members_queryset:
        if not CurrentMembers.objects.filter(member=member).exists():
            application = member.userprofile.user.applications.first()
            # Create a new NewMembers entry
            new_member = CurrentMembers(member=member, member_app=application)
            new_member.save()
            new_member.created_date = member.userprofile.user.date_joined
            new_member.save()
            logger.debug(f"New member added: {new_member}")
