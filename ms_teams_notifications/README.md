# Introduction 
Basic setup using plain `requests` library to submit messages to Microsoft Teams Webhooks.

Contains a convenience module for easy submission with some extra system-info passed along with the message, and a couple of examples of how to format a "connector card" which is what Teams will display.

# Useful resources
- Card designer tool: https://amdesigner.azurewebsites.net/
- Documentation: https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using

# Installation
Only `requests` and `pandas` are needed for a basic run of the examples.
```
pip install -r requirements.txt
python main.py
```

## Teams webhook URL
A test-webhook-URL is hard-coded into `monitoring.py`.

Getting a webhook URL from Teams is easy:
1. Make sure you have access to create "connectors" on a channel level (You might need to be "Owner" of the Team).
1. Click the "three dots" right next to the channel name in the team/channel overview, or click the "three dots" in the top right corner after entering into a channel. Select "Connectors".
1. Click "Configure" or "Add" next to the connector named "Incoming Webhook".
1. Give the connector a name, and a URL will show. Use this URL as the target of a webhook POST action, e.g. in the python code provided.
