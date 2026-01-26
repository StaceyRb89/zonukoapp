from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """Custom storage for Digital Ocean Spaces"""
    location = 'media'
    file_overwrite = False
