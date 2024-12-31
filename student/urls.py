"""Routes."""

from django.urls import path

from . import views

app_name = "student"

urlpatterns = [
    path("", views.index, name="index"),
    path("apply-title/<int:member_id>/", views.apply_title, name="apply_title"),
    path("undo-title/<int:member_id>/", views.undo_title, name="undo_title"),
]
