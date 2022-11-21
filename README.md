# Picture Event Zipper

An application that allows any user to create an event and share the link of this event to his friends. Each user with the link can add pictures and download the archive containing all the images of the event.

The application run in the AWS cloud and is fully scalable.

For more information about the projetct, see the file Cloud_P2.pdf

## Installation

To run the application, you must have awscli and awsebcli installed. awscli must be configured.

Simply execute

    $./install.sh

in the root of the project.

Normally, the installation takes approximately 20 to 30 minutes. Sometimes, the CloudFront take more time to be fully deployed.

When the application is fully deployed and that the CDN are ready, the application automatically launch to the default browser.

## Uninstallation

To unistall the application, execute

    $./aws_clean.sh

in the root of the project.

## Architecture

![alt tag](/pics/Arch.png?raw=true "Architecture")

