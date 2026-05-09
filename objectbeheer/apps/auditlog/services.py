from .models import AuditLog


def write_audit_log(action, user=None, obj=None, message="", old_value=None, new_value=None):
    object_type = ""
    object_id = ""

    if obj is not None:
        object_type = obj.__class__.__name__
        object_id = str(obj.pk)

    return AuditLog.objects.create(
        action=action,
        object_type=object_type,
        object_id=object_id,
        message=message,
        old_value=old_value,
        new_value=new_value,
        created_by=user,
    )
