"""
This file has helper functions to report values to the monitoring system
"""
import os
import datetime
import getpass
import logging
import socket
import pprint
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# This hard-coded webhook aims at the "Webhook Test Channel" as part of the "Maritime Smart Use of Data"-team:
teams_url = "https://outlook.office.com/webhook/ce6d787c-786b-44e2-82ce-2f6338c4b1bf@adf10e2b-b6e9-41d6-be2f-c12bb566019c/IncomingWebhook/114a520f4d624a74bb3685e282e86cf9/58e827e7-c478-4e4c-91fc-49455afdb33f"


def report(module: str, value_name: str, value, is_info_message=False):
    """
    Report one value from a module (e.g "GetSources") with a name
    (e.g "InvalidNPSVesselDataRows") and a value (e.g 5)

    If is_message is True then the report is assumed to be a text to
    be shown to users, e.g. pushed to a Teams group chat. Otherwise
    it is just reported as a value to be used for monitoring (e.g.
    plotting number of predictions over time, each point in the plot
    being one full run of the Luigi pipeline)
    """
    data = {
        "reported_at": datetime.datetime.now(),
        "process": "SMoUD Webhook Test Process",
        "module": module,
        "name": value_name,
        "value": value,
        "is_info_message": is_info_message,
        "host": socket.gethostname(),
        "user": getpass.getuser(),
    }
    _report_data(data)


def _report_data(data: dict):
    """
    Report data to the monitoring system

    If data["is_info_message"] is True, then post to MS Teams. If not, redirect to the
    proper monitoring system (not implemented!).
    """
    logger.info(f"Sending report:\n{pprint.pformat(data)}")

    # Get the Teams URL - modify as needed.
    # teams_url = os.getenv("teams_webhook_url", False)

    if teams_url and data["is_info_message"]:
        try:
            _post_report_to_ms_teams(data, teams_url)
        except Exception as e:
            logger.debug("Unable to post report to MS Teams. Exception: %s", e)

    # Report numeric values as datapoints to a graphing/monitoring service
    if not data["is_info_message"]:
        logger.warning("TODO: implement way to report this numeric value to a monitoring system")


def _post_report_to_ms_teams(data: dict, url: str):
    """
    A preliminary function for posting to a MS Teams webhook.

    - Card designer tool: https://amdesigner.azurewebsites.net/
    - Documentation: https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using

    Parameters
    ----------
    data : dict
        Data to post. See implementation to customize/change.
    url : str
        URL to MS Teams Webhook.
        Example: https://outlook.office.com/webhook/ce6d787c-786b-44e2-82ce-2f6338c4b1bf@adf10e2b-b6e9-41d6-be2f-c12bb566019c/IncomingWebhook/bccedd8094f84b85bfaabb7bb1654c80/58e827e7-c478-4e4c-91fc-49455afdb33f
    """
    # """

    message = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "IHS Engine test message",
        "sections": [
            {
                "activityTitle": "Module: " + data.get("module", ""),
                "activitySubtitle": "A monitoring message from the IHS Engine monitoring system",
                "activityImage": "https://i.ibb.co/FYk85j3/IHS.png",
                "facts": [
                    {"name": "Process", "value": data.get("process", "")},
                    {"name": "Reported at", "value": str(data.get("reported_at", ""))},
                    {"name": "Host", "value": str(data.get("host", ""))},
                    {"name": "User", "value": str(data.get("user", ""))},
                    {"name": "Topic", "value": data.get("name", "")},
                    {"name": "Value", "value": data.get("value", "")},
                ],
                "markdown": True,
            }
        ],
    }
    headers = {"Content-Type": "application/json"}

    # The request returns "1" as r.text if the post was successful.
    r = requests.post(url, headers=headers, json=message, verify=True)

    logger.debug("Response from MS Teams webhook: %s, %s, %s", r.text, r.status_code, r.reason)
