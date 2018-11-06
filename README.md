<p align="center">
  <img src="http://i.imgur.com/oePnHJn.jpg" alt="Halo Biz Serverless!"/>
</p>

# Halo

The **Halo** Lib is a python based library utilizing [**Serverless**](https://logz.io/blog/serverless-vs-containers/) technology and [**microservices architecture**](http://blog.binaris.com/your-guide-to-migrating-existing-microservices-to-serverless/) 
<p/>Halo provides the following features:

-  Django and/or Flask development for AWS Lambda & Dynamodb
-  [correlation id across microservices](https://theburningmonk.com/2017/09/capture-and-forward-correlation-ids-through-different-lambda-event-sources/)
-  [structured json based logging](https://theburningmonk.com/2018/01/you-need-to-use-structured-logging-with-aws-lambda/)
-  [sample debug log in production](https://theburningmonk.com/2018/04/you-need-to-sample-debug-logs-in-production/)
-  [support for microservice transactions with the saga pattern](https://read.acloud.guru/how-the-saga-pattern-manages-failures-with-aws-lambda-and-step-functions-bc8f7129f900)
-  [using SSM Parameter Store over Lambda env variables](https://hackernoon.com/you-should-use-ssm-parameter-store-over-lambda-env-variables-5197fc6ea45b)
-  [Serverless Error Handling & trace id for end users](https://aws.amazon.com/blogs/compute/error-handling-patterns-in-amazon-api-gateway-and-aws-lambda/)
-  [Lambda timeout](https://blog.epsagon.com/best-practices-for-aws-lambda-timeouts) management for [slow HTTP responses](https://theburningmonk.com/2018/01/aws-lambda-use-the-invocation-context-to-better-handle-slow-http-responses/)
-  [ootb support for Idempotent service invocations (md5)](https://cloudonaut.io/your-lambda-function-might-execute-twice-deal-with-it/)


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
