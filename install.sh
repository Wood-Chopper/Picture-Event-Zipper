BUCKET_PREFIX=np-$(openssl rand -hex 5)
LAMBDA_PREFIX=np-$(openssl rand -hex 5)
QUEUE=np-$(openssl rand -hex 5)
CWE_PREFIX=np-$(openssl rand -hex 5)
RULE_PREFIX=np-$(openssl rand -hex 5)
LAMBDA_ROLE=np-$(openssl rand -hex 5)
SCHEDULE_PREFIX=np-$(openssl rand -hex 5)
ACCOUNT_ID=$(aws ec2 describe-security-groups --group-names 'Default' --query 'SecurityGroups[0].OwnerId' --output text)
REGION=$(aws configure get default.region)



aws iam create-role --role-name $LAMBDA_ROLE-lambda --assume-role-policy-document file://json/lambda_role.json

aws iam attach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
aws iam attach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess
aws iam attach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/CloudWatchEventsFullAccess
aws iam attach-role-policy --role-name $LAMBDA_ROLE-lambda --policy-arn arn:aws:iam::aws:policy/AWSLambdaFullAccess

aws s3api create-bucket --bucket $BUCKET_PREFIX-static
aws s3api put-object --bucket $BUCKET_PREFIX-static --key bootstrap.css --body s3static/bootstrap.css
aws s3api put-object --bucket $BUCKET_PREFIX-static --key pictureevent.css --body s3static/pictureevent.css
aws s3api put-object --bucket $BUCKET_PREFIX-static --key eventimg.jpg --body s3static/eventimg.jpg
aws s3api put-object --bucket $BUCKET_PREFIX-static --key indeximg.jpg --body s3static/indeximg.jpg
aws s3api put-bucket-website --bucket $BUCKET_PREFIX-static --website-configuration file://json/s3staticweb.json
cat json/s3staticpoltemp.json | replace BUCKETNAME $BUCKET_PREFIX-static > json/s3staticpol.json 
aws s3api put-bucket-policy --bucket $BUCKET_PREFIX-static --policy file://json/s3staticpol.json

aws s3api create-bucket --bucket $BUCKET_PREFIX-images --create-bucket-configuration LocationConstraint=$REGION
aws sqs create-queue --queue-name $QUEUE
cat json/sqspoltemp.json | replace BUCKET $BUCKET_PREFIX-images | replace QUEURARN arn:aws:sqs:$REGION:$ACCOUNT_ID:$QUEUE > json/sqspol.json 
aws sqs set-queue-attributes \
--queue-url https://sqs.$REGION.amazonaws.com/$ACCOUNT_ID/$QUEUE \
--attributes file://json/sqspol.json
cat json/s3imagespoltemp.json | replace BUCKETNAME $BUCKET_PREFIX-images | replace ACCOUNT_ID $ACCOUNT_ID | replace LAMBDA_ROLE $LAMBDA_ROLE-lambda > json/s3imagespol.json 
aws s3api put-bucket-policy --bucket $BUCKET_PREFIX-images --policy file://json/s3imagespol.json
cat json/s3notiftemp.json | replace REGION $REGION | replace ACCOUNT_ID $ACCOUNT_ID | replace SQS $QUEUE > json/s3notif.json 
aws s3api put-bucket-notification --bucket $BUCKET_PREFIX-images \
--notification-configuration file://json/s3notif.json


aws s3api create-bucket --bucket $BUCKET_PREFIX-archives
cat json/s3archivespoltemp.json | replace BUCKETNAME $BUCKET_PREFIX-archives | replace ACCOUNT_ID $ACCOUNT_ID | replace LAMBDA_ROLE $LAMBDA_ROLE-lambda > json/s3archivespol.json 
aws s3api put-bucket-policy --bucket $BUCKET_PREFIX-archives --policy file://json/s3archivespol.json
aws s3api put-object --bucket $BUCKET_PREFIX-archives --key index.html --body s3archives/index.html
aws s3api put-bucket-website --bucket $BUCKET_PREFIX-archives --website-configuration file://json/s3archivesweb.json


cat lambda/zippertemp.py | replace [[QUEUE]] \'$QUEUE\' | replace [[BUCKET_IMAGES]] \'$BUCKET_PREFIX-images\' | replace [[BUCKET_ARCHIVES]] \'$BUCKET_PREFIX-archives\' > lambda/zipper.py
cd lambda
zip zipper.zip zipper.py
cd ..

cat lambda/managertemp.py | replace [[QUEUE]] \'$QUEUE\' | replace [[BUCKET_LAMBDA]] \'$BUCKET_PREFIX-lambda\' | replace [[LAMBDA_PREFIX]] \'$LAMBDA_PREFIX\' | replace [[SCHEDULE_PREFIX]] \'$SCHEDULE_PREFIX\' > lambda/manager.py
cd lambda
zip manager.zip manager.py
cd ..

aws s3api create-bucket --bucket $BUCKET_PREFIX-lambda --create-bucket-configuration LocationConstraint=$REGION
aws s3api put-object --bucket $BUCKET_PREFIX-lambda --key zipper.zip --body lambda/zipper.zip
aws s3api put-object --bucket $BUCKET_PREFIX-lambda --key manager.zip --body lambda/manager.zip

aws lambda create-function \
--function-name $LAMBDA_PREFIX \
--runtime 'python2.7' \
--role arn:aws:iam::$ACCOUNT_ID:role/$LAMBDA_ROLE-lambda \
--handler zipper.lambda_handler \
--code S3Bucket=$BUCKET_PREFIX-lambda,S3Key=zipper.zip \
--timeout 60 \
--memory-size 512

aws events put-rule --name $SCHEDULE_PREFIX \
--schedule-expression "rate(1 minute)" \
--state ENABLED

aws events put-targets --rule $SCHEDULE_PREFIX \
--targets Id=Invoke-0,Arn=arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$LAMBDA_PREFIX

aws events enable-rule --name $SCHEDULE_PREFIX

aws lambda add-permission --function-name $LAMBDA_PREFIX \
--statement-id Trigger \
--action "lambda:*" \
--principal "*"

aws lambda create-function \
--function-name manager-$LAMBDA_PREFIX \
--runtime 'python2.7' \
--role arn:aws:iam::$ACCOUNT_ID:role/$LAMBDA_ROLE-lambda \
--handler manager.lambda_handler \
--code S3Bucket=$BUCKET_PREFIX-lambda,S3Key=manager.zip \
--timeout 60

aws events put-rule --name manager$SCHEDULE_PREFIX \
--schedule-expression "rate(1 minute)" \
--state ENABLED

aws events put-targets --rule manager$SCHEDULE_PREFIX \
--targets Id=Invoke-0,Arn=arn:aws:lambda:$REGION:$ACCOUNT_ID:function:manager-$LAMBDA_PREFIX

aws events enable-rule --name manager$SCHEDULE_PREFIX

aws lambda add-permission --function-name manager-$LAMBDA_PREFIX \
--statement-id Trigger \
--action "lambda:*" \
--principal "*"

