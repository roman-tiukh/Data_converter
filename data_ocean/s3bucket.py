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

BUCKET_NAME = settings.AWS_S3_BUCKET_NAME
BUCKET_REGION = settings.AWS_S3_REGION_NAME
ACCESS_KEY_ID = settings.AWS_S3_ACCESS_KEY_ID
SECRET_ACCESS_KEY = settings.AWS_S3_SECRET_ACCESS_KEY
HASH_LENGTH = 16


def save_file(file_path: str, file_body, content_disposition: str = ATTACHMENT,
              acl: str = PUBLIC_READ, hashing: bool = True) -> str:

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
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name=BUCKET_REGION,
    )
    if s3.Bucket(BUCKET_NAME).creation_date is None:
        raise ValueError('This bucket does not exist!')

    logger.info(f'[{timezone.now()}] s3bucket save file: {file_path} ...')

    s3.Bucket(BUCKET_NAME).put_object(
        Key=file_path_str,
        Body=file_body,
        ACL=acl,
        ContentDisposition=content_disposition,
        ContentType=content_type,
    )

    url = f'https://{BUCKET_NAME}.s3.{BUCKET_REGION}.amazonaws.com/{file_path_str}'
    logger.warning(f'[{timezone.now()}] s3bucket file URL: {url}')

    return url
