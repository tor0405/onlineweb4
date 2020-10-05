# -*- coding: utf-8 -*-
import locale
import logging

from django.utils import timezone

from apps.authentication.models import OnlineGroup
from apps.events.models import AttendanceEvent
from apps.marks.models import Mark, MarkUser
from apps.mommy import schedule
from apps.mommy.registry import Task
from apps.notifications.constants import PermissionType
from apps.notifications.utils import send_message_to_groups, send_message_to_users


class SetEventMarks(Task):
    @staticmethod
    def run():
        logger = logging.getLogger()
        logger.info("Attendance mark setting started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        # Get all active attendance events that are supposed to give automatic marks.
        attendance_events = SetEventMarks().active_events()

        for attendance_event in attendance_events:
            SetEventMarks.set_marks(attendance_event, logger)
            message = SetEventMarks.generate_message(attendance_event)

            if message.send:
                send_message_to_users(
                    title=message.subject,
                    content=str(message),
                    from_email=message.organizer,
                    recipients=message.not_attended_users,
                    permission_type=PermissionType.NEW_MARK,
                )
                logger.info("Emails sent to: " + str(message.not_attended_users))
            else:
                logger.info("Everyone met. No mails sent to users")

            if message.organizer_message:
                send_message_to_groups(
                    title=message.subject,
                    content=message.organizer_message,
                    from_email="online@online.ntnu.no",
                    groups=[message.organizer],
                )
                logger.info("Email sent to: " + message.organizer_mail)

    @staticmethod
    def set_marks(attendance_event: AttendanceEvent, logger=logging.getLogger()):
        event = attendance_event.event
        logger.info(f'Proccessing "{event.title}"')
        mark = Mark()
        mark.title = f"Manglende oppmøte på {event.title}"
        mark.category = event.event_type
        mark.description = (
            f"Du har fått en prikk på grunn av manglende oppmøte på {event.title}."
        )
        mark.save()

        for user in attendance_event.not_attended():
            user_entry = MarkUser()
            user_entry.user = user
            user_entry.mark = mark
            user_entry.save()
            logger.info("Mark given to: " + str(user_entry.user))

        attendance_event.marks_has_been_set = True
        attendance_event.save()

    @staticmethod
    def generate_message(attendance_event: AttendanceEvent):
        message = Message()

        not_attended_users = attendance_event.not_attended()
        event = attendance_event.event
        title = str(event.title)

        # return if everyone attended
        if not not_attended_users:
            return message

        message.not_attended_users = not_attended_users

        message.organizer_mail = event.feedback_mail()
        message.organizer = OnlineGroup.objects.get(pk=event.organizer.pk)
        not_attended_string = "\n".join(
            [user.get_full_name() for user in not_attended_users]
        )

        message.subject = title
        message.intro = (
            'Hei\n\nPå grunn av manglende oppmøte på "%s" har du fått en prikk'
            % (title)
        )
        message.contact = "\n\nEventuelle spørsmål sendes til %s " % (
            message.organizer_mail
        )
        message.send = True
        message.organizer_message = (
            'På grunn av manglende oppmøte på "%s" har følgende brukere fått en prikk:\n'
            % (event.title)
        )
        message.organizer_message += not_attended_string
        return message

    @staticmethod
    def active_events():
        return AttendanceEvent.objects.filter(
            automatically_set_marks=True,
            marks_has_been_set=False,
            event__event_end__lt=timezone.now(),
        )


class Message:
    subject = ""
    intro = ""
    contact = ""
    not_attended_users = []
    send = False
    end = "\n\nMvh\nLinjeforeningen Online"
    results_message = False

    organizer: OnlineGroup = None
    organizer_mail: str = None
    organizer_message: str = None

    def __str__(self):
        message = "%s %s %s" % (self.intro, self.contact, self.end)
        return message


schedule.register(SetEventMarks, day_of_week="mon-sun", hour=8, minute=0o5)
