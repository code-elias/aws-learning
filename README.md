# Personal AWS Learning & Sandbox

## Commands to remember

### Bucket

```bash
aws s3api get-bucket-policy --bucket BUCKET_NAME --region us-east-1
```

```bash
aws s3 ls BUCKET_NAME --recursive --region us-east-1
```

### Lambda functions

```bash
aws iam get-role --role-name email-forwarder-runtime --query 'Role.Arn' --output text
```

```bash
zip -j function.zip lambda_function.py
```

Create
```bash
aws lambda create-function \
    --function-name email-forwarder \
    --runtime python3.12 \
    --role arn:aws:iam::755118747882:role/email-forwarder-runtime \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --environment "Variables={BUCKET_NAME=recovryzone-email-server,GORGIAS_FORWARD_ADDR=mvr4w50ppdyo6z7l@email.gorgias.com,SUPPORT_PREFIX=support,INBOUND_BUCKET_PREFIX=inbound/,SHOW_FULL_DEBUG=true}" \
    --timeout 15 \
    --region us-east-1
```

Update
```bash
aws lambda update-function-configuration \
    --function-name email-forwarder \
    --environment "Variables={BUCKET_NAME=recovryzone-email-server,GORGIAS_FORWARD_ADDR=mvr4w50ppdyo6z7l@email.gorgias.com,SUPPORT_PREFIX=support,INBOUND_BUCKET_PREFIX=inbound/,SHOW_FULL_DEBUG=true}" \
    --region us-east-1
```

Delete
```bash
aws lambda delete-function \
    --function-name email-forwarder \
    --region us-east-1
```

Get config
```bash
aws lambda get-function-configuration \
    --function-name email-forwarder \
    --region us-east-1 \
    --query "Environment.Variables"
```

Attach permissions
```bash
aws lambda add-permission \
    --function-name email-forwarder \
    --statement-id AllowSESInvoke \
    --action "lambda:InvokeFunction" \
    --principal ses.amazonaws.com \
    --region us-east-1
```

```bash
aws lambda get-function-configuration \
    --function-name email-forwarder \
    --region us-east-1 \
    --query '{State: State, LastUpdateStatus: LastUpdateStatus, Reason: LastUpdateStatusReason}'
```

### Receipt Rules

```bash
aws ses list-receipt-rule-sets --region us-east-1

aws ses describe-active-receipt-rule-set --region us-east-1
```

Add Rule
```bash
aws ses create-receipt-rule \
    --rule-set-name email-forwarder-rules \
    --rule file://support_rule.json \
    --region us-east-1
```

Delete
```bash
aws ses delete-receipt-rule \
    --rule-set-name email-forwarder-rules \
    --rule-name RuleName \
    --region us-east-1
```

### Logs

```bash
aws logs tail /aws/lambda/email-forwarder --follow --region us-east-1
```