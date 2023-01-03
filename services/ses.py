import logging

import boto3


class SESservice:
    def __init__(self):
        self.client = boto3.client('ses',
                                   aws_access_key_id='',
                                   aws_secret_access_key='',
                                   region_name="eu-central-1")

    def send_email(self, email, order=False):
        response = self.client.send_email(
            Source="stanchev2607@gmail.com",
            Destination={
                'ToAddresses': [
                    email,
                ],
            },
            Message={
                'Subject': {
                    'Data': 'Welcome to Stanchev Watches',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': "We received your purchase request;we'll be in touch shortly!" if order else 'Enjoy',
                        'Charset': 'UTF-8'
                    }
                }
            },

        )
