from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosServiceError

from bug_manage import settings
from bug_manage.settings import COS_SECRET_KEY, COS_SECRET_ID
from sts.sts.sts import Sts


def upload_file(bucket_path, file_path, filename, region='ap-nanjing'):
    """
    上传文件
    :param cos_path:
    :param file_path:
    :param filename:
    :return:
    """

    config = CosConfig(Region=region, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
    client = CosS3Client(config)
    #### 高级上传接口（推荐）
    # 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
    response = client.upload_file_from_buffer(
        Bucket=bucket_path,
        Body=file_path,
        Key=filename,
    )
    return f'https://{bucket_path}.cos.{region}.myqcloud.com/{filename}'


def create_bucket(bucket, region='ap-nanjing'):
    """
    创建桶
    :param bucket:桶名称
    :param region: 区域
    :return:
    """
    config = CosConfig(Region=region, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
    client = CosS3Client(config)
    # response = \
    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'
    )
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': "*",
                'ExposeHeader': "*",
                'MaxAgeSeconds': 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def delete_bucket_one(bucket, key, token=None, region='ap-nanjing'):
    config = CosConfig(Region=region, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY, Token=token)
    client = CosS3Client(config)
    response = client.delete_object(
        Bucket=bucket,
        Key=key
    )


def delete_bucket_many(bucket, key_object, token=None, region='ap-nanjing'):
    config = CosConfig(Region=region, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY, Token=token)
    client = CosS3Client(config)
    response = client.delete_objects(
        Bucket=bucket,
        Delete={
            'Object': key_object,
            'Quiet': 'true'
        }
    )


def credential(bucket, region='ap-nanjing'):
    """ 获取cos上传临时凭证 """

    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 1800,
        # 固定密钥 id
        'secret_id': settings.COS_SECRET_ID,
        # 固定密钥 key
        'secret_key': settings.COS_SECRET_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # "name/cos:PutObject",
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],

    }

    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict


def check_etag(bucket, key, region='ap-nanjing'):
    config = CosConfig(Region=region, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
    client = CosS3Client(config)
    response = client.head_object(
        Bucket=bucket,
        Key=key
    )
    return response


def delete_cos(bucket, region='ap-nanjing'):
    config = CosConfig(Region=region, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
    client = CosS3Client(config)
    try:
        while True:
            part_objects = client.list_objects(bucket)
            contents = part_objects.get('Contents')
            if not contents:
                break
            objects = {'Object': [{'Key': i['Key']} for i in contents],
                       'Quiet': 'true'
                       }
            print(objects)
            client.delete_objects(Bucket=bucket, Delete=objects)

            if part_objects['IsTruncated'] == 'false':
                break
        while True:
            part_uploads = client.list_multipart_uploads(bucket)
            uploads = part_uploads.get('Upload')
            if not uploads:
                break
            for item in uploads:
                client.abort_multipart_upload(bucket, item['Key'], item['UploadId'])
            if part_uploads['IsTruncated'] == 'false':
                break
        client.delete_bucket(bucket)
    except CosServiceError as e:
        pass
