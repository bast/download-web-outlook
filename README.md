# download-web-outlook

Python script to download emails and attachments from Outlook on the web using
the MS Graph API.

![too many emails](emails.gif)


## Pros and cons of this approach

There are much easier alternatives than this script to download emails from
Outlook on the web:
- Use Outlook desktop client on macOS or Windows.
- Get a copy of the mailbox in PST format.
- Use one of the official Python SDKs and libraries (but I could not get them
  to work for my use case).
- Script is written as a Flask app. There are many other ways to do this.

I have used this script to successfully archive 44k emails from Outlook on the
web to a Linux operating system. I implemented this as a relatively lightweight
web app because I wanted the authentication to happen in the web browser.  It
may or may not work on other operating systems.

**The script is brittle**: The download can take hours and it may be necessary
to run the script multiple times after authentication times out. Improvements
to the script are welcome.

What I like about this approach:
- All emails are downloaded in plain text format which I can easily search with
  standard tools like `grep` and `find`.
- The script gives me full control over how I want to store the emails and
  attachments. I chose: `email-archive/YYYY/MM/DD/Subject/time-stamp.txt` for emails and
  `email-archive/YYYY/MM/DD/Subject/attachments/` for attachments.
- The script will write a file `email-archive/archived_emails.txt` holding IDs of
  all downloaded emails. This way I can easily check which emails I have
  already downloaded and which ones I still need to download. This means you can restart the script
  many times and it will continue where it left off and not download messages that are already
  listed in `archived_emails.txt`.


## Installation

Dependencies are listed in [requirements.txt](requirements.txt).
I recommend installing them using [uv](https://docs.astral.sh/uv/).


## What you will need to make this work

You will need the following information and credentials to use the script
and for this adjust `config.cfg`:
- Tenant ID
- Client ID
- Client Secret
- Redirect URI

You will need the "Mail.Read" API permission for the app registration in Azure
AD.

The script is tested with the redirect URI set to `http://localhost:36367`. If
you choose a different redirect URI, you might need to adjust the Flask app
part.

Another thing you can modify are `max_num_emails` and `batch_size` in
[main.py](main.py).  For testing/debugging it can be useful to set
`max_num_emails` to a small number and first see whether the script works at
all. The script will always start with the most recent emails, so you can set
`max_num_emails` to a small number and then increase it later.


## Example usage

```bash
$ python main.py
```

Then in your browser visit `http://localhost:36367/login` to authenticate.

Then you can watch the progress bar in the terminal where you started the
script.


## Example result

The script will download emails and attachments to the `download_folder` specified
in `config.cfg` and group emails by conversation/subject ("email thread") and
neatly organize them in folders by year, month, and day according to the time-stamp
of the newest email in the thread:
```
email-archive
├── YYYY
│   ├── MM
│   │   ├── DD
│   │   │   ├── Some subject
│   │   │   │   └── 2016-01-13T10:41:18Z.txt
│   │   │   ├── Re: Another subject
│   │   │   │   └── 2016-01-13T16:58:45Z.txt
│   │   │   ├── Re: Some question
│   │   │   │   ├── 2016-01-13T10:09:05Z.txt
│   │   │   │   ├── 2016-01-13T10:38:44Z.txt
│   │   │   │   ├── 2016-01-13T10:45:45Z.txt
│   │   │   │   └── 2016-01-13T10:46:15Z.txt
│   │   │   ├── Yet another subject
│   │   │   │   ├── 2015-11-30T07:31:05Z.txt
│   │   │   │   ├── 2015-11-30T11:57:24Z.txt
│   │   │   │   ├── 2016-01-13T14:58:26Z.txt
│   │   │   │   └── attachments
│   │   │   │       └── Summary.docx
│   │   │   ├── And another subject
│   │   │   │   ├── 2016-01-13T14:44:56Z.txt
│   │   │   │   ├── 2016-01-13T14:48:19Z.txt
│   │   │   │   └── attachments
│   │   │   │       └── scan.pdf
...
```


## Acknowledgements

Big thanks to my colleague Raymond for his help to get this working.
