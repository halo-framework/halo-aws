from __future__ import print_function
import json
import logging
#import boto3
import uuid
import base64
import decimal
#import boto3
import botocore
from functools import update_wrapper, wraps
import importlib
import inspect
import os
import time
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from .exceptions import ProviderError
from .settingsx import settingsx
from .base_util import AWSUtil
from .exceptions import HaloAwsException
from .ses import send_mail as send_mailx

logger = logging.getLogger(__name__)

settings = settingsx()

#  kept warm.
try:
    import boto3
    aws_region = settings.AWS_REGION
    if not aws_region:
        aws_region = 'us-east-1'
    aws_session = boto3.Session(region_name=aws_region)
    LAMBDA_CLIENT = aws_session.client('lambda')
    SNS_CLIENT = aws_session.client('sns')
    STS_CLIENT = aws_session.client('sts')
    DYNAMODB_CLIENT = aws_session.client('dynamodb')
    S3_CLIENT = aws_session.client('s3')
    SES_CLIENT = aws_session.client('ses')
except botocore.exceptions.NoRegionError as e:
    logger.error("Unexpected boto client Error")
    raise ProviderError(e)


LAMBDA_ASYNC_PAYLOAD_LIMIT = 256000
SNS_ASYNC_PAYLOAD_LIMIT = 256000
settings.ASYNC_RESPONSE_TABLE

LATEST = '$LATEST'

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

class AWSProvider() :

    PROVIDER_NAME = "AWS"
    util = None

    def __init__(self, aws_region=None, **kwargs):
        if not aws_region:
            self.aws_region = settings.AWS_REGION
        else:
            self.aws_region = aws_region
        if kwargs.get('boto_session'):
            self.lambda_client = kwargs.get('boto_session').client('lambda')
            self.sns_client = kwargs.get('boto_session').client('sns')
            self.sts_client = kwargs.get('boto_session').client('sts')
            self.dynamodb_client = kwargs.get('boto_session').client('dynamodb')
            self.s3_client = kwargs.get('boto_session').client('s3')
            self.ses_client = kwargs.get('boto_session').client('ses')
        else:
            self.lambda_client = LAMBDA_CLIENT
            self.sns_client = SNS_CLIENT
            self.sts_client = STS_CLIENT
            self.dynamodb_client = DYNAMODB_CLIENT
            self.s3_client = S3_CLIENT
            self.ses_client = SES_CLIENT
        self.util = AWSUtil()

    def show(self):
        raise NotImplementedError

    def get_context(self):
        """

        :return:
        """
        return self.util.get_context()

    def get_header_name(self, request, name):
        if not name:
            raise HaloAwsException("empty header name")
        return 'HTTP_'+name

    def get_request_id(self, request):
        return uuid.uuid4().__str__()

    def send_event(self,ctx,messageDict,service_name,version=LATEST,capture_response=None):
        payload = self.pre_send(messageDict, capture_response)
        if len(payload) > LAMBDA_ASYNC_PAYLOAD_LIMIT:  # pragma: no cover
            raise ProviderError("Payload too large for async Lambda call")
        context = AWSProvider.lambda_context({"context": ctx.toJSON(), "msg": messageDict},
                                   {settings.ENV_TYPE: settings.ENV_NAME}, {})
        try:
            ret = self.lambda_client.invoke(
                FunctionName=service_name,
                InvocationType='Event',
                LogType='None',
                ClientContext=context,
                Payload=payload,
                Qualifier=version
            )
            sent = (ret.get('StatusCode', 0) == 202)
            return ret,sent
        except ClientError as e:
            logger.error("Unexpected boto client Error:"+e.__str__(), extra=ctx.toJSON())
            raise ProviderError(e)
        except Exception as e:
            logger.error("Unexpected boto client Error:"+e.__str__(), extra=ctx.toJSON())
            raise ProviderError(e)

    def get_topic_name(self,lambda_name):
        """ Topic name generation """
        return '%s-halo-async' % lambda_name

    def publish(self,ctx, messageDict, arn=None,capture_response=False,lambda_function_name=None):
        if not arn:
            if lambda_function_name:
                AWS_ACCOUNT_ID = self.sts_client.get_caller_identity()['Account']
                arn = 'arn:aws:sns:{region}:{account}:{topic_name}'.format(
                    region=self.aws_region,
                    account=AWS_ACCOUNT_ID,
                    topic_name=self.get_topic_name(lambda_function_name)
                )
            else:
                raise ProviderError("no arn for sns")
        payload = self.pre_send(messageDict, capture_response)
        if len(payload) > LAMBDA_ASYNC_PAYLOAD_LIMIT:
            raise ProviderError("Payload too large for SNS")
        try:
            ret = self.sns_client.publish(
                TargetArn=arn,
                Message=str(payload)
            )
            sent = ret.get('MessageId')
            return ret,sent
        except ClientError as e:
            logger.error("Unexpected boto client Error:"+e.__str__(), extra=ctx.toJSON())
            raise ProviderError('invoke_sync', e)
        except Exception as e:
            logger.error("Unexpected client Error:"+e.__str__(), extra=ctx.toJSON())
            raise ProviderError('invoke_sync', e)

    def pre_send(self,msg,capture_response=None):
        if capture_response:
            if settings.ASYNC_RESPONSE_TABLE is None:
                print(
                    "Warning! Attempted to capture a response without "
                    "async_response_table configured in settings (you won't "
                    "capture async responses)."
                )
                capture_response = False
                response_id = "MISCONFIGURED"

            else:
                response_id = str(uuid.uuid4())
            msg['capture_response'] = capture_response
            msg['response_id'] = response_id
        else:
            response_id = None
        payload = bytes(json.dumps(msg), "utf8")
        return payload

    @staticmethod
    def lambda_context(custom=None,env=None,client=None):
        client_context = dict(
            custom=custom,
            env=env,
            client=client)
        json_context = json.dumps(client_context).encode('utf-8')
        return base64.b64encode(json_context).decode('utf-8')

    """
    env and custom in the Client Context dict object could be anything. For client, only the following keys can be accepted:
    app_version_name
    app_title
    app_version_code
    app_package_name
    installation_id
    if your lambda function is implemented in Python. The Client Context object may 
    be referred as context.client_context. env(context.cilent_context.env) and custom(context.client_context.custom) are two dict objects. 
    If any of env, custom, or client is not passed from boto3's invoke method, the corresponding one in the context.client_context would be a None.
    """

    def invoke_sync(self,ctx, messageDict, lambda_function_name,version=LATEST):
        payload = self.pre_send(messageDict)
        context = AWSProvider.lambda_context({"context":ctx.toJSON()},{settings.ENV_TYPE:settings.ENV_NAME},{})
        try:
            ret = self.lambda_client.invoke(
                FunctionName=lambda_function_name,
                InvocationType='RequestResponse',
                LogType='None',
                ClientContext=context,
                Payload=payload,
                Qualifier=version
            )
            return ret
        except ClientError as e:
            # logger.error("Unexpected boto client Error", extra=dict(ctx, messageDict, e))
            raise ProviderError('invoke_sync',e)


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


    @staticmethod
    def event(messageDict):
        #{"method":method,"url":url,"data":datay,"headers":headers,"auth":auth}
        return {
            "body": messageDict["data"],
            "headers": messageDict["headers"],
            "httpMethod": messageDict["method"],
            "isBase64Encoded": False,
            "path": AWSProvider.get_path(messageDict["url"]),
            "pathParameters": {"proxy": "some/path"},
            "queryStringParameters": AWSProvider.get_params(messageDict["url"]),
            "requestContext": {
                "accountId": "16794",
                "apiId": "3z6kd9fbb1",
                "httpMethod": messageDict["method"],
                "identity": {
                    "accessKey": None,
                    "accountId": None,
                    "apiKey": None,
                    "caller": None,
                    "cognitoAuthenticationProvider": None,
                    "cognitoAuthenticationType": None,
                    "cognitoIdentityId": None,
                    "cognitoIdentityPoolId": None,
                    "sourceIp": "76.20.166.147",
                    "user": None,
                    "userAgent": "PostmanRuntime/3.0.11-hotfix.2",
                    "userArn": None,
                },
                "authorizer": {"principalId": "wile_e_coyote"},
                "requestId": "ad2db740-10a2-11e7-8ced-35048084babb",
                "resourceId": "r4kza9",
                "resourcePath": "/{proxy+}",
                "stage": settings.ENV_NAME,
            },
            "resource": "/{proxy+}",
            "stageVariables": None,
        }

    def send_mail(self,req_context, vars, from1=None, to=None):
        return send_mailx(self.ses_client,req_context, vars, from1, to)

    def get_timeout(self,request):
        return self.util.get_timeout(request)

    def get_func_region(self):
        return self.util.get_func_region()

    def get_func_name(self):
        return self.util.get_func_name()

    def get_lambda_context(self,request):
        return self.util.get_lambda_context(request)

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
        try:
            self.s3_client.upload_fileobj(file, bucket_name, object_name)
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
        try:
            response = self.s3_client.generate_presigned_url('get_object',
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
            existing_tables = self.dynamodb_client.list_tables()['TableNames']
            if table_name not in existing_tables:
                table = self.dynamodb_client.create_table(
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
            resp = self.dynamodb_client.get_item(
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
            resp = self.dynamodb_client.put_item(
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
            resp = self.dynamodb_client.update_item(
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
            resp = self.dynamodb_client.query(TableName=table_name,
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
    def get_path(url):
        from urllib.parse import urlparse
        o = urlparse(url)
        return o.path

    @staticmethod
    def get_params(url):
        from urllib.parse import urlparse
        o = urlparse(url)
        ret = {}
        if o.query:
            arr = o.query.split("&")
            if len(arr) > 0:
                for p in arr:
                    nv = p.split("=")
                    ret[nv[0]] = nv[1]
        return  ret