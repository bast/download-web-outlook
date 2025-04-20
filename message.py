from pathlib import Path
import base64
from bs4 import BeautifulSoup
import re


from connection import get_data


def write_message_to_file(
    file_name, message_id, from_email, to, cc, bcc, subject, text
):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"id: {message_id}\n")
        f.write(f"from: {from_email}\n")
        f.write(f"to: {to}\n")
        f.write(f"cc: {cc}\n")
        f.write(f"bcc: {bcc}\n")
        f.write(f"subject: {subject}\n")
        f.write(f"\n{text}\n")


def get_metadata(message):
    message_id = message["id"]

    conversation_id = message.get("conversationId", "No Conversation ID")
    subject = message.get("subject", "No Subject")

    from_email = (
        message.get("from", {}).get("emailAddress", {}).get("address", "Unknown Sender")
    )

    received = message.get("receivedDateTime", "")

    return message_id, conversation_id, subject, from_email, received


def download_attachments(message_id, download_folder):
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments"
    data = get_data(url)

    attachments = data["value"]

    if len(attachments) > 0:
        Path(download_folder).mkdir(parents=True, exist_ok=True)

    for attachment in attachments:
        if attachment["@odata.type"] == "#microsoft.graph.fileAttachment":
            filename = attachment["name"]
            content_bytes = attachment["contentBytes"]
            file_path = Path(download_folder) / filename

            with open(file_path, "wb") as f:
                f.write(base64.b64decode(content_bytes))


def _format_recipients(label, recipients):
    result = []
    for r in recipients:
        name = r["emailAddress"].get("name", "")
        address = r["emailAddress"].get("address", "")
        result.append(f"{name} <{address}>")
    return result


def get_message_details(message_id):
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}?$select=body,toRecipients,ccRecipients,bccRecipients,from"
    data = get_data(url)

    body = data["body"]
    content = body["content"]
    content_type = body["contentType"]

    if content_type == "html":
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text()
    else:
        text = content

    # normalize line endings
    text = re.sub(r"\r\n?|\n", "\n", text)

    to = _format_recipients("To", data.get("toRecipients", []))
    cc = _format_recipients("Cc", data.get("ccRecipients", []))
    bcc = _format_recipients("Bcc", data.get("bccRecipients", []))

    return to, cc, bcc, text
