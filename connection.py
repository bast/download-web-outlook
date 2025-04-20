import requests
from flask import session, redirect, url_for
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)


from config import CLIENT_ID, CLIENT_SECRET, AUTHORITY


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def _get_with_retries(url, headers):
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 401:
        raise Exception("Unauthorized - token likely expired")
    response.raise_for_status()
    return response


def _refresh_access_token():
    refresh_token = session.get("refresh_token")
    if not refresh_token:
        logger.warning("No refresh token available.")
        return False

    logger.info("Attempting to refresh access token...")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "https://graph.microsoft.com/.default",
    }

    try:
        token_url = f"{AUTHORITY}/oauth2/v2.0/token"
        response = requests.post(token_url, data=data, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        session["access_token"] = token_data["access_token"]
        session["refresh_token"] = token_data.get(
            "refresh_token", refresh_token
        )  # may not always be returned
        logger.info("Access token refreshed successfully.")
        return True
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return False


def get_data(url):
    if "access_token" not in session:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {session['access_token']}"}

    try:
        res = _get_with_retries(url, headers)
    except Exception as e:
        if "Unauthorized" in str(e):
            logger.warning("Access token may have expired, attempting refresh ...")
            if _refresh_access_token():
                headers["Authorization"] = f"Bearer {session['access_token']}"
                try:
                    res = _get_with_retries(url, headers)
                except Exception as retry_err:
                    return f"Failed after token refresh: {retry_err}"
            else:
                session.pop("access_token", None)
                session.pop("refresh_token", None)
                return redirect(url_for("login"))
        else:
            return f"Network error after retries: {e}"

    return res.json()
