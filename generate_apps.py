import os

apps = ["accounts", "employees", "projects", "finance", "suppliers", "fleet", "audit", "dashboard"]

for app in apps:
    app_dir = os.path.join("apps", app)
    # Create __init__.py
    with open(os.path.join(app_dir, "__init__.py"), "w") as f:
        pass
    # Create apps.py
    class_name = app.capitalize() + "Config"
    apps_py_content = f"""from django.apps import AppConfig

class {class_name}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app}'
"""
    with open(os.path.join(app_dir, "apps.py"), "w") as f:
        f.write(apps_py_content)
    # Create admin.py, models.py, views.py, urls.py
    for file_name in ["admin.py", "models.py", "views.py"]:
        with open(os.path.join(app_dir, file_name), "w") as f:
            f.write("from django.db import models\n" if file_name == "models.py" else "")

print("Apps created successfully.")
