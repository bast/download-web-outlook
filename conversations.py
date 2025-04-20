from collections import defaultdict
from flask import redirect, url_for


from connection import get_data
from message import get_metadata


def collect_emails(max_num_emails, batch_size):
    url = f"https://graph.microsoft.com/v1.0/me/messages?$top={batch_size}&$select=subject,id,from,receivedDateTime,conversationId&$orderby=receivedDateTime desc"

    conversations = defaultdict(list)
    num_emails = 0

    while url:
        data = get_data(url)

        try:
            messages = data.get("value", [])
        except AttributeError:
            return None, redirect(url_for("login"))

        for message in messages:
            message_id, conversation_id, subject, from_email, received = get_metadata(
                message
            )
            conversations[conversation_id].append(
                (
                    message_id,
                    subject,
                    from_email,
                    received,
                )
            )

            num_emails += 1
            if num_emails >= max_num_emails:
                return conversations, None

        # will be none when no more pages
        url = data.get("@odata.nextLink")

    return conversations, None
