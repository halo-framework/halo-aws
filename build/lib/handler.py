from zappa.handler import LambdaHandler
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def lambda_handler(event=None, context=None):
    logger.debug('start lambda_handler : ' + str(event))
    lh = LambdaHandler()
    if event.get('platform', None):
        response = lh.run_function(load_lambda_handler, event, context)
    else:
        response = lh.handler(event, context)
    logger.debug('finish lambda_handler : ' + str(response))
    return response

def load_lambda_handler(event, context):
    logger.debug('load_lambda_handler : ' + str(event))


    from commonapi.views import TaskLink
    vars = event#json.dumps(event)
    t = TaskLink()
    ret = t.execute_var_task(vars)

    logger.debug('finish lambda_handler : ' + str(ret))