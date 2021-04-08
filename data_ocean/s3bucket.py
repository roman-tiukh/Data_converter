import logging
import string
import random
import pathlib
from datetime import timedelta
from django.utils import timezone
import boto3
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def save_file(file_path='', file_body='', content_disposition: str = 'attachment',
              acl: str = 'public-read', expires_days: int = 7) -> str:

    acls = ('public-read', 'private')
    content_dispositions = ('inline', 'attachment')
    content_types = {
        '.csv': 'text/csv',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.json': 'application/json',
        '.html': 'text/html',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.xlsx',
        '.xml': 'application/xml',
        '.zip': 'application/zip',
    }
    bucket_name = settings.AWS_S3_BUCKET_NAME
    bucket_region = settings.AWS_S3_REGION_NAME
    access_key_id = settings.AWS_S3_ACCESS_KEY_ID
    secret_access_key = settings.AWS_S3_SECRET_ACCESS_KEY
    hash_length = 16

    if acl not in acls:
        acl = 'public-read'

    if content_disposition not in content_dispositions:
        content_disposition = 'attachment'

    file_path = str(file_path).strip('/')
    if not file_path:
        raise Exception('File path cannot be empty!')

    # insert hash to filepath
    file_path_suffix = pathlib.Path(file_path).suffix
    file_path_wo_suffix = file_path[:-len(file_path_suffix)]
    hash = ''.join(random.choices(string.ascii_letters + string.digits, k=hash_length))
    file_path_hashed = f'{file_path_wo_suffix}_{hash}{file_path_suffix}'

    # auto ContentType
    if file_path_suffix in content_types:
        content_type = content_types[file_path_suffix]
    else:
        content_type = 'application/octet-stream',
        content_disposition = 'attachment'

    s3 = boto3.resource(
        's3',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=bucket_region,
    )
    if s3.Bucket(bucket_name).creation_date is None:
        raise Exception('This bucket does not exist!')

    logger.info(f'[{timezone.now()}] s3bucket save file: {file_path_hashed} ...')

    s3.Bucket(bucket_name).put_object(
        Key=file_path_hashed,
        Body=file_body,
        ACL=acl,
        ContentDisposition=content_disposition,
        ContentType=content_type,
        Expires=timezone.now()+timedelta(days=expires_days),
    )

    url = f'https://{bucket_name}.s3.{bucket_region}.amazonaws.com/{file_path_hashed}'
    logger.warning(f'[{timezone.now()}] s3bucket file URL: {url}')

    return url
