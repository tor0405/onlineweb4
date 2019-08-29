from django.core.management.base import BaseCommand
from django.utils import dateparse, timezone

from apps.approval.models import MembershipApproval
from apps.approval.views import get_expiry_date
from apps.authentication.constants import FieldOfStudyType
from apps.authentication.models import AllowedUsername, OnlineUser as User


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        before_error = dateparse.parse_datetime('2018-09-19T00:00:00.000Z')
        applications = MembershipApproval.objects.filter(
            approved=True,
            field_of_study=FieldOfStudyType.SOCIAL_MEMBER,
            created__gte=before_error,
        ).order_by('processed_date')

        for application in applications:
            user: User = application.applicant
            application: MembershipApproval = application

            if user.field_of_study == FieldOfStudyType.SOCIAL_MEMBER:

                membership = AllowedUsername.objects.filter(username=user.ntnu_username).first()
                if membership:
                    self.handle_existing_membership(application, membership)
                else:
                    self.handle_new_membership(application)

    @staticmethod
    def handle_existing_membership(application: MembershipApproval, membership: AllowedUsername):
        started_year = application.started_date.year
        expiration_date = get_expiry_date(started_year, 1)
        membership.expiration_date = expiration_date
        if not membership.description:
            membership.description = ''
        membership.description += f'''  
-------------------
Updated by Dotkom fixing script

Approved on {timezone.now().date()}.

Old notes:
{membership.note}
'''
        membership.note = f'{application.applicant.get_field_of_study_display()} {application.applicant.started_date}'
        membership.save()

    @staticmethod
    def handle_new_membership(application: MembershipApproval):
        started_year = application.started_date.year
        expiration_date = get_expiry_date(started_year, 1)
        membership = AllowedUsername.objects.create(
            username=application.applicant.ntnu_username,
            expiration_date=expiration_date,
            registered=application.processed_date.date(),
        )
        membership.note = f'{application.applicant.get_field_of_study_display()} {application.applicant.started_date}'
        membership.description = f'''Created by Dotkom fixing script

Approved on {timezone.now().date()}.'''
        membership.save()
