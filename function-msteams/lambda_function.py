""" AWS Lambda function to send Buildkite Build Notifications to MS Teams """
import os
import sys
from base64 import b64decode
import boto3
import pymsteams  # https://pypi.org/project/pymsteams/

def get_hookurl():
    """ Get the Hook URL from the OS ENV either encrypted or not, and pass it through """
    if 'HookUrl' in os.environ:
        hook_url = os.environ['HookUrl']
    elif 'kmsEncryptedHookUrl' in os.environ:
        encrypted_hook_url = os.environ['kmsEncryptedHookUrl']
        hook_url = "https://" + boto3.client('kms'). \
            decrypt(CiphertextBlob=b64decode(encrypted_hook_url))['Plaintext'].decode('utf-8')
    else:
        print("No Teams Hook Defined in Environment")
        sys.exit(10)
    if "https://" not in hook_url:
        print("Request Failed - Webhook URL is not a valid URL")
        sys.exit(12)
    return hook_url

def send_buildkite_buildfinish_message(webhook_url,event):
    """ Build MS Teams message to send from Buildkite event """
    teams_message = pymsteams.connectorcard(webhook_url)
    teams_message.title("Buildkite Builds")
    try:
        pipe_name = event['detail']['pipeline']['slug']
        branch_name = event['detail']['build']['branch']
        pipe_buildno = event['detail']['build']['number']
        commit_message = event['detail']['build']['message'].strip()
        commit_user = ""  # Not Current Available from event
        commit_id = event['detail']['build']['commit']
        if len(commit_id) > 10:
            commit_id = commit_id[:7]
        buildkite_org = event['detail']['organization']['slug']
        pipeline_state = event['detail']['build']['state']
        msgprefix = ""
        # Emojis https://apps.timwhitlock.info/emoji/tables/unicode
        if pipeline_state == "failed":
            teams_message.color("#ee3333")
            msgprefix = "&#x1F622; "  # Crying Face
        elif pipeline_state == "passed":
            teams_message.color("#33ee33")
            msgprefix = "&#x1F603; "  # Happy Face
        elif pipeline_state == "blocked":
            teams_message.color("#3333ee")
            msgprefix = "&#x270B; "  # Raised Hand
        else:
            print("Ignoring Event - not a pipeline state")
            sys.exit(0)
        message = f"{msgprefix}**{pipe_name} ({branch_name}) #{pipe_buildno}**<br /> \
        {commit_message} - {commit_user} ({commit_id})"
        pipe_link = f"https://buildkite.com/{buildkite_org}/{pipe_name}/builds/{str(pipe_buildno)}"
        teams_message.addLinkButton("View Build", pipe_link)
    except KeyError:
        # If any errors from above - it means the payload from Buildkite is not valid
        message = f"Event Payload is not a valid Buildkite Build Event. \
            See https://buildkite.com/docs/integrations/amazon-eventbridge#example-event-payloads-build-finished\n \
            {event}"

    teams_message.text(message)
    print("SENDING: ",end='')
    teams_message.printme()
    # send the message.
    teams_message.send()
    last_status_code = teams_message.last_http_response.status_code
    print(F"HTTP Response: {last_status_code}")
    if last_status_code != 200:
        sys.exit(last_status_code)

# Event Must Be a Buildkite 'Build event'
def lambda_handler(event, context):
    """ Main Function for AWS to call to start our function """
    del context
    webhook_url = get_hookurl()
    send_buildkite_buildfinish_message(webhook_url,event)

if __name__ == "__main__":
    lambda_handler("", "")
