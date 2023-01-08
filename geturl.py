import boto3, secret

def presign():
    key = input("input key")
    s3 = boto3.client("s3", region_name=secret.getRegionName(), aws_access_key_id=secret.getAccessKey(), aws_secret_access_key=secret.getSecretKey(), endpoint_url='https://s3.' + secret.getRegionName() + '.amazonaws.com')
    bucket = secret.getBucket()

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket, 'Key': key,},
        ExpiresIn=3600,
    )
    print(url)