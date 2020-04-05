from apps.events.models import Event, RuleBundle


def resolve_all_events(_, __):
    return Event.objects.all()


def resolve_gradeRules(rulebundle, info):
    return rulebundle.grade_rules.get_queryset().values_list('pk', flat=True)


def resolve_fieldOfStudyRules(rulebundle, info):
    return rulebundle.field_of_study_rules.get_queryset().values_list('pk', flat=True)
