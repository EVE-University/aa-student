from django.apps import AppConfig

from student import __version__


class StudentConfig(AppConfig):
    name = "student"
    label = "student"
    verbose_name = "aa-student V" + __version__

    def ready(self):
        import student.signals  # noqa: F401
