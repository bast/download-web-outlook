from pathlib import Path
from tqdm import tqdm


from app import app, run
from message import get_message_details, download_attachments, write_message_to_file
from conversations import collect_emails
from config import DOWNLOAD_FOLDER
from timestamp import extract_ymd


@app.route("/emails")
def emails():
    conversations, redirect = collect_emails(max_num_emails=50000, batch_size=200)
    if redirect is not None:
        return redirect
    archive_emails(conversations)
    return f"Fetched {len(conversations)} conversations."


def archive_emails(conversations):
    Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    summary_file = Path(DOWNLOAD_FOLDER) / "archived_emails.txt"

    already_archived = set()
    if summary_file.exists():
        with open(summary_file, "r") as f:
            already_archived = set(f.read().splitlines())

    with open(summary_file, "a") as f:
        for _, messages in tqdm(conversations.items()):
            thread_subject = oldest_subject(messages)
            thread_subject = thread_subject.replace("/", "_").replace("\\", "_")

            timestamp = newest_timestamp(messages)

            year, month, day = extract_ymd(timestamp)
            archive_path = Path(DOWNLOAD_FOLDER) / year / month / day / thread_subject
            Path(archive_path).mkdir(parents=True, exist_ok=True)
            attachments_path = archive_path / "attachments"

            for message_id, subject, from_email, received in messages:
                if message_id in already_archived:
                    continue
                else:
                    to, cc, bcc, text = get_message_details(message_id)

                    file_name = archive_path / f"{received}.txt"
                    write_message_to_file(
                        file_name, message_id, from_email, to, cc, bcc, subject, text
                    )

                    download_attachments(message_id, attachments_path)
                    f.write(f"{message_id}\n")


def oldest_subject(messages):
    """
    We take the oldest subject in a thread since that one is least likely to be
    changed with endless Re: Fwd: Fwd: Fwd: Fwd: Fwd: Fwd: Fwd: Fwd:
    """
    result = "unknown"
    for _, subject, _, _ in messages:
        result = subject
    if result is None:
        return "unknown"
    else:
        return result


def newest_timestamp(messages):
    """
    An email thread will be archived under the year/month/day of the newest email
    in the thread.
    """
    for _, _, _, received in messages:
        return received


if __name__ == "__main__":
    run()
