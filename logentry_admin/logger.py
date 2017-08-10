from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User
from django.forms.models import model_to_dict


def diff_changes_model(obj_a, obj_b):
    klass = obj_a.__class__

    diff_map = {}

    if obj_a and not obj_b:
        return model_to_dict(obj_a)

    for field in klass._meta.fields:
        display = "get_%s_display"

        def default_func():
            return None

        val_a = (
            getattr(obj_a, display % field.name, default_func)() or
            getattr(obj_a, field.name, None)
        )
        val_b = (
            getattr(obj_b, display % field.name, default_func)() or
            getattr(obj_b, field.name, None)
        )

        if val_a != val_b:
            diff = u"{0} --> {1}".format(val_a, val_b)
            diff_map[field.name] = diff

    return diff_map


def construct_change_message(obj, formsets, add, dic_changes={}):
    """
    Construct a JSON structure describing changes from a changed object.
    Translations are deactivated so that strings are stored untranslated.
    Translation happens later on LogEntry access.
    """
    change_message = []
    if add:
        change_message.append({'added': dic_changes})
    elif obj:
        change_message.append({'changed': {'fields': dic_changes}})

    return change_message


def log_changes(request, obj_start, obj_end, add=True):
    obj_changes = u''

    modeladmin = ModelAdmin(User, ModelAdmin)
    if add:
        obj_changes = u'Objeto adicionado'
        modeladmin.log_addition(request, obj_end)
    else:
        obj_changes = diff_changes_model(obj_start, obj_end)

        modeladmin.log_change(request, obj_end, {'changed': obj_changes})
    return obj_changes


def log_changes_before_save(request, obj_end):
    klass = obj_end.__class__
    obj_start = klass.objects.filter(pk=obj_end.pk).first()
    add = not obj_start

    return log_changes(request, obj_start, obj_end, add=add)
