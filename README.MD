## MS Teams Notifications for Buildkite

Currently Buildkite does not support direct notifications to MS Teams. For those using buildkite in an Enterprise environment, this means building something custom.

This CloudFormation Template and Lambda function support Build Complete notifications to MS Teams using the Buildkite AWS EventBridge integration.

At the moment, the EventBus event has all the normal notification content, however it is missing the username sent in notifications sent using Slack. To implement this you would need to perform additional API calls to obtain this information.

## To Implement

1. Setup the Buildkite AWS EventBridge Notification Services.
https://buildkite.com/docs/integrations/amazon-eventbridge
You will need the Partner event source name to deploy the CloudFormation Template Parameters.

2. Create an MS Teams 'Incoming Webhook' for Buildkite.
https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook
It is recommended to call this 'Buildkite Notification' or similar and use the buildkite.png in this repo (./image/buildkite.png) as the image. Save the WebHook URL for use with the CloudFormation Template

3. Install requirements for the Lambda function by running pip install from the function-msteams folder. This will install the pymsteams library and it's dependencies. ```pip install -r requirements.txt -t .```

4. Using SAM or CloudFormation Build, build the template and deploy the Lambda function zip file

5. Deploy the Cloudformation Template

6. Enjoy your MS Teams Build Notifications
