from __future__ import print_function
import logging
from AlexaDeploymentHandler import AlexaDeploymentHandler


"""
Main entry point for the Lambda function.
In the AWS Lamba console, under the 'Configuration' tab there is an
input field called, 'Handler'.  That should be:  main.lambda_handler

Handler: main.lambda_handler
Role: lambda_basic_execution
"""

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logging.info("Executing main lambda_handler for AlexaDeploymentHandler class")

    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.90257981-6dee-4cc2-8ba3-be7cdfef4192"):
        raise ValueError("Invalid Application ID")

    alexa = AlexaDeploymentHandler()
    alexa_response = alexa.process_request(event, context)

    return alexa_response
