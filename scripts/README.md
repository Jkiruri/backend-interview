# Utility Scripts

This directory contains utility scripts for the OrderFlow project.

## Scripts Overview

### `check_celery_status.py`
- **Purpose**: Check Celery worker status and task processing
- **Usage**: `python scripts/check_celery_status.py`
- **Description**: Monitors Celery workers, active tasks, and worker statistics

### `set_admin_password.py`
- **Purpose**: Set or update admin user password
- **Usage**: `python scripts/set_admin_password.py`
- **Description**: Creates or updates admin user with default credentials

### `setup_db.py`
- **Purpose**: Database setup and initialization
- **Usage**: `python scripts/setup_db.py`
- **Description**: Handles database migrations and initial setup

## Running Scripts

All scripts should be run from the project root directory:

```bash
# Example: Check Celery status
python scripts/check_celery_status.py

# Example: Set admin password
python scripts/set_admin_password.py

# Example: Setup database
python scripts/setup_db.py
```

## Notes

- All scripts automatically set up the Django environment
- Scripts are designed to be run independently
- Check individual script files for specific requirements or dependencies
