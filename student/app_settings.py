"""App settings."""

from django.conf import settings

STUDENTDAYS = getattr(settings, "STUDENTDAYS", 14)
STUDENTLIMIT = getattr(settings, "STUDENTLIMIT", 50)
