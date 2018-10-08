from .apis import ApiMngr
from .exceptions import ApiError
from .exceptions import HaloError

"""
We'll need a transaction log for the saga
this is our coordinator for the saga Functions
Because the compensating requests can also fail  we need to be able to retry them until success, which means they have to be idempotent.
we implements backward recovery only.
For forward recovery you also need to ensure the requests are imdempotent.
"""
class SagaError(HaloError):
    """
    Raised when an action failed and at least one compensation also failed.
    """

    def __init__(self, exception, compensation_exceptions):
        """
        :param exception: BaseException the exception that caused this SagaException
        :param compensation_exceptions: list[BaseException] all exceptions that happened while executing compensations
        """
        self.action = exception
        self.compensations = compensation_exceptions


class Action(object):
    """
    Groups an action with its corresponding compensation. For internal use.
    """

    def __init__(self, name, action, compensation, next):
        """

        :param action: Callable a function executed as the action
        :param compensation: Callable a function that reverses the effects of action
        """
        self.__kwargs = None
        self.__action = action
        self.__compensation = compensation
        self.__name = name
        self.__next = next

    def act(self, **kwargs):
        """
        Execute this action

        :param kwargs: dict If there was an action executed successfully before this action, then kwargs contains the
                            return values of the previous action
        :return: dict optional return value of this action
        """
        print("act " + self.__name)
        self.__kwargs = kwargs
        return self.__action(**kwargs)

    def compensate(self, error):
        """
        Execute the compensation.
        :return: None
        """
        for comp in self.__compensation:
            for error_code in comp["error"]:
                if error_code == "States.ALL" or error_code == error:
                    return comp["next"]
        raise SagaError("no compenation for : " + self.__name)

    def next(self):
        return self.__next


class Saga(object):
    """
    Executes a series of Actions.
    If one of the actions raises, the compensation for the failed action and for all previous actions
    are executed in reverse order.
    Each action can return a dict, that is then passed as kwargs to the next action.
    While executing compensations possible Exceptions are recorded and raised wrapped in a SagaException once all
    compensations have been executed.
    """

    def __init__(self, actions, start):
        """
        :param actions: list[Action]
        """
        self.actions = actions
        self.start = start

    def execute(self, req_context, payloads, apis):
        """
        Execute this Saga.
        :return: None
        """
        kwargs = {'result_key': None}
        name = self.start
        for action_index in range(len(self.actions)):
            try:
                print("execute=" + name)
                kwargs['req_context'] = req_context
                kwargs['payload'] = payloads[name]
                kwargs['exec_api'] = apis[name]
                kwargs = self.__get_action(name).act(**kwargs) or {}
                print("kwargs=" + str(kwargs))
                name = self.__get_action(name).next()
                if name is True:
                    print("finished")
                    break
            except ApiError as e:
                print("ApiError=" + str(e))
                name = self.__get_action(name).compensate(e.status_code)
            except BaseException as e:
                print("e=" + str(e))
                # compensation_exceptions = self.__run_compensations(action_index)
                # raise SagaError(e, compensation_exceptions)


            if type(kwargs) is not dict:
                raise TypeError('action return type should be dict or None but is {}'.format(type(kwargs)))

    def __get_action(self, name):
        """
        Returns an action by index.

        :param index: int
        :return: Action
        """
        return self.actions[name]

    def __run_compensations(self, last_action_index):
        """
        :param last_action_index: int
        :return: None
        """
        print("run_compensations")
        compensation_exceptions = []
        for compensation_index in range(last_action_index, -1, -1):
            try:
                self.__get_action(compensation_index).compensate()
            except BaseException as ex:
                compensation_exceptions.append(ex)
        return compensation_exceptions


class SagaBuilder(object):
    """
    Build a Saga.
    """

    def __init__(self):
        self.actions = {}

    @staticmethod
    def create():
        return SagaBuilder()

    def action(self, name, action, compensation, next):
        """
        Add an action and a corresponding compensation.

        :param action: Callable an action to be executed
        :param compensation: Callable an action that reverses the effects of action
        :return: SagaBuilder
        """
        actionx = Action(name, action, compensation, next)
        self.actions[name] = actionx
        return self

    def build(self, start):
        """
        Returns a new Saga ready to execute all actions passed to the builder.
        :return: Saga
        """
        return Saga(self.actions, start)


def load_saga(jsonx):
    try:
        if "StartAt" in jsonx:
            start = jsonx["StartAt"]
        else:
            raise HaloError("can not build saga. No StartAt")
        saga = SagaBuilder.create()
        for state in jsonx["States"]:
            print(str(state))
            if jsonx["States"][state]["Type"] == "Task":
                api_name = jsonx["States"][state]["Resource"]
                print("api_name=" + api_name)
                api_instance_name = ApiMngr.get_api(api_name)
                print("api_instance_name=" + str(api_instance_name))
                # result_key = 'result'#jsonx["States"][state]["ResultPath"]
                # action = lambda req_context, payload, api=api_instance_name: ApiMngr(req_context).get_api_instance(api).post(payload)
                action = lambda req_context, payload, exec_api, result_key, api=api_instance_name: exec_api(
                    ApiMngr(req_context).get_api_instance(api), result_key, payload)
                comps = []
                if "Catch" in jsonx["States"][state]:
                    for item in jsonx["States"][state]["Catch"]:
                        comp = {"error": item["ErrorEquals"], "next": item["Next"]}
                        comps.append(comp)
                if "Next" in jsonx["States"][state]:
                    next = jsonx["States"][state]["Next"]
                else:
                    next = jsonx["States"][state]["End"]
                saga.action(state, action, comps, next)
        return saga.build(start)
    except SagaError as e:
        print(e)  # wraps the BaseException('some error happened')
        raise HaloError("can not build saga")


def run_saga(req_context, saga, payloads, apis):
    try:
        saga.execute(req_context, payloads, apis)
    except SagaError as e:
        print(e)  # wraps the BaseException('some error happened')
        raise HaloError("can not execute saga")
