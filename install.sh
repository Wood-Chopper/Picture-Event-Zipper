BUCKET_PREFIX=np-$(openssl rand -hex 5)
LAMBDA_PREFIX=np-$(openssl rand -hex 5)
QUEUE=np-$(openssl rand -hex 5)
CWE_PREFIX=np-$(openssl rand -hex 5)
RULE_PREFIX=np-$(openssl rand -hex 5)

aws s3api create-bucket --bucket $BUCKET_PREFIX-siteres
aws s3api create-bucket --bucket $BUCKET_PREFIX-images
aws s3api create-bucket --bucket $BUCKET_PREFIX-archives
aws s3api create-bucket --bucket $BUCKET_PREFIX-lambda

aws sqs create-queue --queue-name $QUEUE

#roles lambda

#SQS

#S3

#Lambda

#Deploy