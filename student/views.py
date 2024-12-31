from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from student.app_settings import STUDENTLIMIT
from student.models import AppConfig, CurrentMembers


@login_required
@permission_required("student.basic_access")
def index(request):
    """List all NewMembers ordered by creation date."""
    filtered_members = CurrentMembers.filter_by_member_state_and_no_student_title()
    filtered_members_with_title = (
        CurrentMembers.filter_by_member_state_and_student_title()
    )
    return render(
        request,
        "student/index.html",
        {
            "members_without_title": filtered_members,
            "members_with_title": filtered_members_with_title,
            "limit": STUDENTLIMIT,
        },
    )


@login_required
@permission_required("student.basic_access")
@require_POST
def apply_title(request, member_id):
    """Apply the student title to the selected member."""
    member = get_object_or_404(CurrentMembers, id=member_id)
    app_config = AppConfig.objects.first()

    if not app_config or not app_config.student_title:
        messages.error(request, "Student title configuration is missing.")
        return redirect("student:index")

    # Add the student title to the user's groups
    user = member.member.userprofile.user
    user.groups.add(app_config.student_title)
    messages.success(
        request, f"Student title applied to {member.member.character_name}."
    )

    return redirect("student:index")


@login_required
@permission_required("student.basic_access")
@require_POST
def undo_title(request, member_id):
    """Remove the student title from the selected member."""
    member = get_object_or_404(CurrentMembers, id=member_id)
    app_config = AppConfig.objects.first()

    if not app_config or not app_config.student_title:
        messages.error(request, "Student title configuration is missing.")
        return redirect("student:index")

    # Remove the student title from the user's groups
    user = member.member.userprofile.user
    user.groups.remove(app_config.student_title)
    messages.success(
        request, f"Student title removed from {member.member.character_name}."
    )

    return redirect("student:index")
