from django.contrib.auth.models import Group
from graphene_django import DjangoObjectType
import graphene
from apps.events.models import Extras, RuleBundle, Event, User, AttendanceEvent, FieldOfStudyRule, Rule, GradeRule
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from .resolvers import resolve_all_events, resolve_gradeRules, resolve_fieldOfStudyRules


class RuleBundleType(DjangoObjectType):
    class Meta:
        model = RuleBundle

    grade_rules = graphene.List(graphene.Int, resolver=resolve_gradeRules)
    field_of_study_rules = graphene.List(graphene.Int, resolver=resolve_fieldOfStudyRules)


class ExtrasType(DjangoObjectType):
    class Meta:
        model = Extras


class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        fields = ('name', 'id')


class AttendanceEventType(DjangoObjectType):
    class Meta:
        model = AttendanceEvent
        fields = ("max_capacity",
                  "waitlist",
                  "guest_attendance",
                  "registration_start",
                  "registration_end",
                  "unattend_deadline",
                  "automatically_set_marks",
                  "rule_bundles",
                  "number_on_waitlist",
                  "number_of_seats_taken",
                  "extras",)


class EventType(DjangoObjectType):
    class Meta:
        model = Event
        interfaces = (relay.Node,)
        exclude = ('author', 'image', 'feedback')

    attendance_event = graphene.Field(AttendanceEventType)

    absolute_url = graphene.String(source='get_absolute_url')
    slug = graphene.String(source='slug')


class EventQuery(graphene.ObjectType):
    all_events = graphene.List(EventType, resolver=resolve_all_events)
