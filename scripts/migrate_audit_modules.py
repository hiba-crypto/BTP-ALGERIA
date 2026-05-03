from apps.audit.models import AuditLog
mapping = {
    'accounts': 'admin',
    'employees': 'rh',
    'projects': 'chef_projet',
    'finance': 'comptable',
    'suppliers': 'achats',
    'fleet': 'parc'
}
for old, new in mapping.items():
    count = AuditLog.objects.filter(module=old).update(module=new)
    if count > 0:
        print(f"Updated {count} records from '{old}' to '{new}'")
print("Update complete")
