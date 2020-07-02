from __future__ import print_function
import json
import logging
import boto3
import uuid
from botocore.exceptions import ClientError
from .exceptions import ProviderError
from .settingsx import settingsx
from .base_util import AWSUtil
import decimal
from boto3.dynamodb.conditions import Key, Attr
from .exceptions import HaloAwsException

logger = logging.getLogger(__name__)

settings = settingsx()

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

class AWSProvider() :

    PROVIDER_NAME = "AWS"

    dynamodb = None

    def __init__(self):
        try:
            self.dynamodb = boto3.client('dynamodb', region_name=settings.AWS_REGION)
        except ClientError as e:
            logger.error("Unexpected boto dynamodb client Error")
            raise ProviderError(e)

    def show(self):
        raise NotImplementedError

    @staticmethod
    def get_context():
        """

        :return:
        """
        return AWSUtil().get_context()

    def get_header_name(self, request, name):
        if not name:
            raise HaloAwsException("empty header name")
        return 'HTTP_'+name

    def get_request_id(self, request):
        return uuid.uuid4().__str__()

    @staticmethod
    def send_event(ctx,messageDict,service_name,version=None):
        try:
            client = boto3.client('lambda', region_name=settings.AWS_REGION)
            ret = client.invoke(
                FunctionName=service_name,
                InvocationType='Event',
                LogType='None',
                ClientContext=ctx.toJSON(),
                Payload=bytes(json.dumps(messageDict), "utf8"),
                Qualifier=version
            )
            return ret
        except ClientError as e:
            #logger.error("Unexpected boto client Error", extra=dict(ctx, messageDict, e))
            raise ProviderError(e)

    @staticmethod
    def send_mail(req_context, vars, from1=None, to=None):
        from .ses import send_mail as send_mailx
        return send_mailx(req_context, vars, from1, to)

    @staticmethod
    def get_timeout(request):
        return AWSUtil().get_timeout(request)

    @staticmethod
    def get_func_region():
        return AWSUtil().get_func_region()

    @staticmethod
    def get_func_name():
        return AWSUtil().get_func_name()

    # s3

    def upload_file(self,file,file_name, bucket_name, object_name=None):
        """Upload a file to an S3 bucket

        :param file: File to upload
        :param file_name: Filename to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            s3_client.upload_fileobj(file, bucket_name, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def create_presigned_url(self,bucket_name, object_name, expiration=3600):
        """Generate a presigned URL to share an S3 object

        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """

        # Generate a presigned URL for the S3 object
        s3_client = boto3.client('s3')
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name,
                                                                'Key': object_name},
                                                        ExpiresIn=expiration)
            #response = s3_client.generate_presigned_url(
            #    ClientMethod='get_object',
            #    ExpiresIn=expiration,
            #    Params={
            #        'Bucket': bucket_name,
            #        'Key': object_name,
            #        'ResponseContentDisposition': 'attachment;filename={}'.format(filename),
            #        'ResponseContentType': 'application/octet-stream',
            #    }
            #)
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL
        return response



    # database

    def create_db_table(self, table_name,key_schema,attribute_definitions,provisioned_throughput):
        try:
            existing_tables = self.dynamodb.list_tables()['TableNames']
            if table_name not in existing_tables:
                table = self.dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=key_schema,
                    AttributeDefinitions=attribute_definitions,
                    ProvisionedThroughput=provisioned_throughput
                )

            return
        except ClientError as e:
            raise ProviderError(e.response['Error']['Message'])

    def get_db_item(self, item_id, table_name):
        """

        :return:
        """
        try:
            resp = self.dynamodb.get_item(
                TableName=table_name,
                Key={
                    'ItemId': {'S': item_id}
                }
            )
            item = resp.get('Item')
            if not item:
                raise ProviderError('Item does not exist')

            return item
        except ClientError as e:
            raise ProviderError(e.response['Error']['Message'])

    def put_db_item(self, item, table_name):
        try:
            resp = self.dynamodb.put_item(
                TableName=table_name,
                Item=item
            )

            itemx = resp.get('Item')
            if not itemx:
                raise ProviderError('Item does not save')

            return itemx
        except ClientError as e:
            raise ProviderError(e.response['Error']['Message'])

    def update_db_item(self,key, item, table_name):
        try:
            resp = self.dynamodb.update_item(
                TableName=table_name,
                Key=key,
                UpdateExpression="set info.rating = :r, info.plot=:p, info.actors=:a",
                ExpressionAttributeValues={
                    ':r': decimal.Decimal(5.5),
                    ':p': "Everything happens all at once.",
                    ':a': ["Larry", "Moe", "Curly"]
                },
                ReturnValues="UPDATED_NEW"
            )

            itemx = resp.get('Item')
            if not itemx:
                raise ProviderError('Item does not save')

            return itemx
        except ClientError as e:
            raise ProviderError(e.response['Error']['Message'])

    def query_db(self, table_name, proj=None, express=None,keycond=None):
        try:
            resp = self.dynamodb.query(TableName=table_name,
                ProjectionExpression=proj,#"#yr, title, info.genres, info.actors[0]",
                ExpressionAttributeNames=express,#{"#yr": "year"},  # Expression Attribute Names for Projection Expression only.
                KeyConditionExpression=keycond#Key('year').eq(1992) & Key('title').between('A', 'L')
            )

            items = []
            for i in resp[u'Items']:
                items.append(json.dumps(i, cls=DecimalEncoder))

            return items
        except ClientError as e:
            raise ProviderError(e.response['Error']['Message'])

    @staticmethod
    def invoke_sync(ctx, messageDict, service_name,version=None):
        try:
            client = boto3.client('lambda', region_name=settings.AWS_REGION)
            ret = client.invoke(
                FunctionName=service_name,
                InvocationType='RequestResponse',
                LogType='None',
                ClientContext=ctx.toJSON(),
                Payload=bytes(json.dumps(messageDict), "utf8"),
                Qualifier=version
            )
            return ret
        except ClientError as e:
            # logger.error("Unexpected boto client Error", extra=dict(ctx, messageDict, e))
            raise ProviderError(e)


    # invoke
    """
    response = client.invoke(
    FunctionName='string',
    InvocationType='Event'|'RequestResponse'|'DryRun',
    LogType='None'|'Tail',
    ClientContext='string',
    Payload=b'bytes'|file,
    Qualifier='string'
    )
    """


