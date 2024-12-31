
# **EVE Uni Student Plugin for Alliance Auth**

This is a plugin app for Alliance Auth designed to assist with managing member student titles within EVE University.

---

## **Features**
- Automatically manages student titles based on configurable eligibility criteria.
- Periodically cleans up old member entries using Celery.

---

## **Installation**

1. **Add the app to your `INSTALLED_APPS`:**
   Add the `student` app to the `INSTALLED_APPS` section in your `settings.py` file:
   ```python
   INSTALLED_APPS += [
       'student',
   ]
   ```

2. **Apply migrations and collect static files:**
   Run the following commands in your terminal:
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

---

## **Configuration**

### **Student Eligibility Days**
Set the number of days a member must wait before being eligible for the student title. Add the following to your `settings.py`:
```python
STUDENTDAYS = 14
```
By default, this is set to **14 days**.


Set the number of people visible in the student page. Add the following to your `settings.py`:
```python
STUDENTLIMIT = 50
```
By default, this is set to **50 people**.


---

## **Celery Integration**

### **Schedule Automatic Cleanup**
To enable periodic cleanup of ineligible members, add the following task to your Celery schedule in `settings.py`:
```python
from celery.schedules import crontab

CELERYBEAT_SCHEDULE["delete_excluded_members"] = {
    "task": "student.tasks.delete_excluded_members",
    "schedule": crontab(minute=0, hour=0),  # Runs daily at midnight
}
```

Ensure your Celery worker and beat services are running.
