import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from allianceauth.hrapplications.models import Application

from student.models import CurrentMembers

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Application)
def app_change(instance, **kwargs):
    if instance.approved is not None:
        if instance.approved:
            main = instance.main_character
            # Check if a NewMembers entry already exists for this application
            if not CurrentMembers.objects.filter(member_app=instance).exists():
                # Create a new NewMembers entry
                new_member = CurrentMembers(member=main, member_app=instance)
                new_member.save()
                logger.debug(f"New member added: {instance}")
            else:
                logger.debug(f"New member already exists: {instance}")
        else:
            # Remove any NewMembers entry if not approved
            try:
                new_member = CurrentMembers.objects.get(member_app=instance)
                new_member.delete()
                logger.debug(f"New member entry deleted: {instance}")
            except CurrentMembers.DoesNotExist:
                logger.debug(
                    f"No NewMembers entry to delete for application: {instance}"
                )
