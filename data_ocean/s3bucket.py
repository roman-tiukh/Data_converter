import logging
import string
import random
import pathlib
from django.utils import timezone
import boto3
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


PUBLIC_READ = 'public-read'
PRIVATE = 'private'
ACLS = (
    PUBLIC_READ,  # public access
    PRIVATE,      # private access
)

INLINE = 'inline'
ATTACHMENT = 'attachment'
CONTENT_DISPOSITION = (
    INLINE,       # open file in browser window
    ATTACHMENT,   # download file
)

CONTENT_TYPES = {
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


HASH_LENGTH = 16


def save_file(file_path: str, file_body, content_disposition: str = ATTACHMENT,
              acl: str = PUBLIC_READ, hashing: bool = True) -> str:

    bucket_name = settings.AWS_S3_BUCKET_NAME
    bucket_region = settings.AWS_S3_REGION_NAME
    access_key_id = settings.AWS_S3_ACCESS_KEY_ID
    secret_access_key = settings.AWS_S3_SECRET_ACCESS_KEY

    if content_disposition not in CONTENT_DISPOSITION:
        content_disposition = ATTACHMENT

    if acl not in ACLS:
        acl = PUBLIC_READ

    file_path_str = str(file_path).strip('/')
    if not file_path_str:
        raise ValueError('File path cannot be empty!')

    file_path = pathlib.Path(file_path_str)

    # add hash to file name
    if hashing:
        f_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=HASH_LENGTH))
        file_name_hashed = f'{file_path.stem}_{f_hash}{file_path.suffix}'
        if str(file_path.parent) == '.':
            file_path_str = file_name_hashed
        else:
            file_path_str = f'{file_path.parent}/{file_name_hashed}'

    # auto ContentType
    if file_path.suffix in CONTENT_TYPES:
        content_type = CONTENT_TYPES[file_path.suffix]
    else:
        content_type = 'application/octet-stream',
        content_disposition = ATTACHMENT

    s3 = boto3.resource(
        's3',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=bucket_region,
    )
    if s3.Bucket(bucket_name).creation_date is None:
        raise ValueError('This bucket does not exist!')

    logger.info(f'[{timezone.now()}] s3bucket save file: {file_path} ...')

    s3.Bucket(bucket_name).put_object(
        Key=file_path_str,
        Body=file_body,
        ACL=acl,
        ContentDisposition=content_disposition,
        ContentType=content_type,
    )

    url = f'https://{bucket_name}.s3.{bucket_region}.amazonaws.com/{file_path_str}'
    logger.warning(f'[{timezone.now()}] s3bucket file URL: {url}')

    return url
