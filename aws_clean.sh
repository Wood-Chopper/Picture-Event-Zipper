BUCKET_PREFIX=$(cat install/BUCKET_PREFIX)
LAMBDA_PREFIX=$(cat install/LAMBDA_PREFIX)
QUEUE=$(cat install/QUEUE)
RULE_PREFIX=$(cat install/RULE_PREFIX)
LAMBDA_ROLE=$(cat install/LAMBDA_ROLE)
SCHEDULE_PREFIX=$(cat install/SCHEDULE_PREFIX)
REGION=$(cat install/REGION)
ACCOUNT_ID=$(cat install/ACCOUNT_ID)
CDN_STATIC=$(cat install/CDN_STATIC_ID)
CDN_ARCHIVES=$(cat install/CDN_ARCHIVES_ID)

aws iam detach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam detach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
aws iam detach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess
aws iam detach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/CloudWatchEventsFullAccess
aws iam detach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/AWSLambdaFullAccess
aws iam delete-role --role-name $LAMBDA_ROLE-lambda

aws s3 rm s3://$BUCKET_PREFIX-static --recursive
aws s3api delete-bucket --bucket $BUCKET_PREFIX-static
aws s3 rm s3://$BUCKET_PREFIX-images --recursive
aws s3api delete-bucket --bucket $BUCKET_PREFIX-images
aws s3 rm s3://$BUCKET_PREFIX-archives --recursive
aws s3api delete-bucket --bucket $BUCKET_PREFIX-archives
aws s3 rm s3://$BUCKET_PREFIX-lambda --recursive
aws s3api delete-bucket --bucket $BUCKET_PREFIX-lambda

aws sqs delete-queue --queue-url https://sqs.$REGION.amazonaws.com/$ACCOUNT_ID/$QUEUE
aws lambda delete-function --function-name $LAMBDA_PREFIX
aws lambda delete-function --function-name manager-$LAMBDA_PREFIX

aws events remove-targets --rule $SCHEDULE_PREFIX --ids Invoke-0
aws events remove-targets --rule manager$SCHEDULE_PREFIX --ids Invoke-manager
aws events delete-rule --name $SCHEDULE_PREFIX
aws events delete-rule --name manager$SCHEDULE_PREFIX

rm install/*
rmdir install

./local_clean.sh

aws elasticbeanstalk terminate-environment --environment-name group-A

echo "Do not forget to disable and delete the two CloudFront distribution $CDN_STATIC and $CDN_ARCHIVES "