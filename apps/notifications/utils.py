from typing import Iterable

from django.conf import settings
from django.core.mail import send_mail, EmailMessage

from apps.authentication.models import OnlineGroup as Group
from apps.authentication.models import OnlineUser as User

from .constants import PermissionType
from .models import (
    Notification,
    Permission,
    UserPermission,
    Attachment,
    MessageAttachment,
)
from .tasks import dispatch_email_notification_task, dispatch_push_notification_task


def send_message_to_users(
    title: str,
    content: str,
    recipients: Iterable[User],
    permission_type: PermissionType,
    from_email=settings.DEFAULT_FROM_EMAIL,
    image=None,
    url="/",
    tag=None,
    attachments=[],
    force_override_dont_send_email=False,
    force_override_dont_send_push=False,
):
    permission, created = Permission.objects.get_or_create(
        permission_type=permission_type
    )
    attachments = [
        Attachment.objects.create(file=attachment_file)
        for attachment_file in attachments
    ]
    recipient_users = User.objects.filter(
        pk__in=[user.id for user in recipients]
    ).distinct()

    for recipient in recipient_users:
        # Make sure all permissions exists for the user before sending anything.
        # Available permissions might have changed since the user last loaded their permission dashboard.
        UserPermission.create_all_for_user(recipient)

        user_permission = UserPermission.objects.get(
            user=recipient, permission=permission
        )

        has_push_permission = permission.allow_push and (
            (permission.force_push or user_permission.allow_push)
            and not force_override_dont_send_push
        )
        has_email_permission = permission.allow_email and (
            (permission.force_email or user_permission.allow_email)
            and not force_override_dont_send_email
        )

        if not has_push_permission and not has_email_permission:
            # Don't create notification at all if permission for none of the types is given
            continue

        notification = Notification.objects.create(
            title=title,
            body=content,
            recipient=recipient,
            from_email=from_email,
            permission=permission,
            image=image,
            url=url,
            tag=tag,
        )

        for attachment in attachments:
            MessageAttachment.objects.create(
                notification=notification, attachment=attachment
            )

        if has_push_permission:
            dispatch_push_notification_task.delay(notification_id=notification.id)

        if has_email_permission:
            dispatch_email_notification_task.delay(notification_id=notification.id)


def send_message_to_groups(
    title: str,
    content: str,
    groups: Iterable[Group],
    permission_type=PermissionType.GROUP_MESSAGE,
    from_email=settings.DEFAULT_FROM_EMAIL,
    image=None,
    url="/",
    tag=None,
    attachments=[],
):
    for group in groups:
        EmailMessage(
            subject=title,
            body=content,
            from_email=from_email,
            to=[group.email],
            attachments=attachments,
        ).send(fail_silently=False)

    recipients = []
    for group in groups:
        for member in group.members.all():
            recipients.append(member.user)
    recipient_users = User.objects.filter(
        pk__in=[user.id for user in recipients]
    ).distinct()

    send_message_to_users(
        title=title,
        content=content,
        recipients=recipient_users,
        permission_type=permission_type,
        image=image,
        url=url,
        tag=tag,
        force_override_dont_send_email=True,
    )
