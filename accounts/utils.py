from django.conf import settings
from django.forms import ValidationError

from requests.exceptions import RequestException, Timeout

import requests
import logging


logger = logging.getLogger(__name__)


def validate_recaptcha(token):
    """
    Validates the reCAPTCHA token with Google's reCAPTCHA API.
    :param token: The reCAPTCHA token received from the frontend.
    :return: True if the token is valid and meets the required score, raise `ValidationError` otherwise.
    """

    ERROR_MSG = {"recaptcha": "reCAPTCHA validation failed. Please try again."}
    RECAPTCHA_API_URL = "https://www.google.com/recaptcha/api/siteverify"
    TIMEOUT_SECONDS = 5

    if not token:
        raise ValidationError(ERROR_MSG)

    payload = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": token,
    }
    try:
        response = requests.post(RECAPTCHA_API_URL, data=payload, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()

        if response.status_code == 200:
            result = response.json()

            score = result.get("score", 0)
            if settings.DEBUG:
                logger.debug(f"reCAPTCHA score: {score}")

        # Check if the response is successful and meets the required score
        if result.get("success", False) and score >= settings.RECAPTCHA_REQUIRED_SCORE:
            return True

    except Timeout:
        logger.error("Google reCAPTCHA API request timed out.")

    except RequestException as e:
        logger.error(f"Google reCAPTCHA API request failed: {e}")

    raise ValidationError(ERROR_MSG)
