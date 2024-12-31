"""Tasks."""

import logging

from celery import shared_task

from student.app_settings import STUDENTDAYS
from student.models import CurrentMembers

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
