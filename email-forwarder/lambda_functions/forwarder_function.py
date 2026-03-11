import boto3
import os
from email import message_from_bytes

s3 = boto3.client('s3')
ses = boto3.client('ses', region_name='us-east-1')

def lambda_handler(event, context):
    # ENV variables
    gorgias_addr = os.environ.get('GORGIAS_FORWARD_ADDR')
    support_addr = os.environ.get('SUPPORT_FORWARD_ADDR') # "support@sydneycastles.com"
    # support_bucket_prefix = os.environ.get('SUPPORT_BUCKET_PREFIX') or "inbound/" # "inbound/support/"
    inbound_bucket_prefix = os.environ.get('INBOUND_BUCKET_PREFIX') or "inbound/" # "inbound/"
    bucket_name = os.environ.get('BUCKET_NAME') # "recovryzone-email-server"
    show_full_debug = os.environ.get('SHOW_FULL_DEBUG') or False # "true"

    if not gorgias_addr or not support_addr or not bucket_name:
        raise ValueError("Missing required environment variables")

    if not inbound_bucket_prefix.endswith('/'):
        inbound_bucket_prefix += '/'

    # Check Recipient Address
    try:
        recipients = event['Records'][0]['ses']['receipt']['recipients']
        original_recipient = recipients[0]
        if show_full_debug:
            print(f"This email was sent to: {original_recipient}")

        if original_recipient != support_addr:
            if show_full_debug:
                print(f"This email was not sent to the support address. Skipping forwarding...")
            return

    except KeyError as e:
        print(f"Error: {e}")
        raise e

    # Get Bucket Prefix
    original_recipient_chunks = original_recipient.split('@')
    original_recipient_user = original_recipient_chunks[0]
    original_recipient_domain = original_recipient_chunks[1].split('.')[0]
    bucket_prefix = f"{inbound_bucket_prefix}{original_recipient_domain}/{original_recipient_user}/" # "inbound/sydneycastles/support/

    # Get Message ID to retrieve from S3
    try:
        message_id = event['Records'][0]['ses']['mail']['messageId']
        object_key = f"{bucket_prefix}{message_id}"
        
        if show_full_debug:
            print(f"Attempting to fetch {object_key} from {bucket_name}")
        
    except KeyError as e:
        print(f"Error: {event}")
        raise e

    # Get Object from S3
    try:
        email_obj = s3.get_object(Bucket=bucket_name, Key=object_key)
        raw_email_data = email_obj['Body'].read()  
    except Exception as e:
        print(f"Error: {e}")
        raise e

    # Forward to Gorgias
    try:
        msg = message_from_bytes(raw_email_data)
        original_sender = msg['From']
        del msg['From']
        msg['From'] = support_addr
        del msg['Reply-To']
        msg['Reply-To'] = original_sender
        del msg['Return-Path']
        msg['Return-Path'] = support_addr

        ses.send_raw_email(
            Source=support_addr,
            Destinations=[gorgias_addr],
            RawMessage={
                'Data': msg.as_bytes()
            }
        )

        if show_full_debug:
            print(f"Successfully forwarded email {object_key} to {gorgias_addr}")

    except Exception as e:
        if show_full_debug:
            print(f"Error processing email {object_key}: {str(e)}")
        raise e
