# Tempus Data Engineer Challenge
For this challenge,
 you will develop a simple
 [Apache Airflow](https://airflow.apache.org) data pipeline.

## Candidate Details

### Necessary Set Up
In order to interact with newsapi.org and AWS, several configuration options must be passed into the Airflow docker container. I've opted to use a environment file in the `/docker` directory named `variables.env`. This file expects three lines
1. `NEWS_API=<NEWSAPI_API_KEY>`
2. `AWS_ACCESS_KEY=<USERS_AWS_ACCESS_KEY>`
3. `AWS_SECRET_ACCESS_KEY=<USERS_AWS_SECRET_ACCESS_KEY>`

The `docker/variables.env` file has been added to the `.gitignore` to ensure that keys aren't accidentally saved into source control.

Within the appropriate users AWS account, there needs to be a bucket named `dfenko-tempus`. The user whose AWS credentials are being used needs to have the IAM permission of `AmazonS3FullAccess`.

### Testing
Since `make test` doesn't include the `variables.env` file that `make run` will,  you need to pass in three environment variables to the command in order to have the tests succeed.
```
make test -e NEWS_API=<NEWSAPI_API_KEY> AWS_ACCESS_KEY=<USERS_AWS_ACCESS_KEY> AWS_SECRET_ACCESS_KEY=<USERS_AWS_SECRET_ACCESS_KEY>
```

### Notes
With more time, it would be necessary to create Terraform to create the S3 bucket and to create an IAM role that can be used by the container to absolve the need for a user's API credentials.

Being new to Airflow, I owe myself the time to learn how to better utilize [Xcom](https://airflow.apache.org/concepts.html?highlight=xcom) in Airflow to pass context between operators instead of creating a class for my functions to pass context between them.

There are two strong candidates for integration testing:
1. Utilizing the `NewsAPIException` feature of the newsapi python package to better handle API errors. In retrospect, I would have used that at start of the process, as I had to wait 24 hours to test my DAG.
2. There is numerous documentation around for testing use cases in boto3 and the AWS API. I would like to build up testing to ensure that content is being written.

The `json_normalize` function in `pandas.io.json` simplifies much of the processing needed to move from raw JSON to a DataFrame. In several cases, I opted to call out the specific JSON nests (e.g. `sources`, `totalResults`, and `headlines`) thanks to testing my work in Jupyter prior to committing code to this repository, which allowed me to skip a lot of the setup of the DataFrames that were CSV exported. That influenced my choice of test for the `headline_transform` function, as I opted to ensure that the columns returned from a popular content source matched my expectation. This testing premise is faulty in the long run, since they may change their API output.

I'm including a Jupyter notebook named `Tempus.ipynb` that I used to validate my work. In the same directory as that notebook, there needs to be a file named `tempus.json` with a simple JSON entry in it with the News API key. AWS credentials for boto3 should be in the `~/.aws/config` file, per boto3 documentation.
```
{
    "news_api": "<NEWSAPI_API_KEY>",
}
```

### Specific Environment Notes
In order to avoid rebuilding the Python environment on my home laptop, Anaconda was used to handle the creation and use of a Python 3.6.9 environment.
```
conda create -n py36 python=3.6.9 anaconda
conda activate py36
make init
make run
```

Docker Version: 19.03.5, build 633a0ea
VirtualBox Version: 6.0.12 r133076

## Challenge Summary
Our data pipeline must fetch data from [News API](https://newsapi.org),
 transform the data into a tabular structure,
 and store the transformed data on [Amazon S3](https://aws.amazon.com/s3/).

## Quickstart
1. We recommend starting with a fresh virtualenv using Python 3.6 on a *nix system.
    * Our docker versions are docker 17.12.0-ce and docker-compose 1.18.0.
2. Run `make init` to download project dependencies.
3. Run `make test` to make sure basic smoke tests are passing.
4. Run `make run` with docker running to bring up airflow.
    * The Airflow UI/Admin Console should now be visible on [http://localhost:8080](http://localhost:8080).
    * There will be a DAG named `sample_dag`. You should be able to view logs from the [Task Instance Context Menu](https://airflow.readthedocs.io/en/latest/ui.html#task-instance-context-menu).
5. Follow the requirements + rules of engagement below.

## Requirements
- [ ] Use Airflow to construct a new data pipeline (DAG) named 'tempus_challenge_dag'.
- [ ] Data pipeline must be scheduled to run once a day.
- [ ] Data pipeline will:
  - [ ] Retrieve all English news sources.
  - [ ] For each news source, retrieve the top headlines.
    - [ ] Top headlines must be flattened into a CSV file. CSV Filename: `<pipeline_execution_date>_top_headlines.csv`
    - [ ] Result CSV must be uploaded to the following s3 location `<s3_bucket>/<source_name>`
- [ ] The solution must contain at least one test for your headline transformation.
- [ ] The solution must be start-able via `make run`.
- [ ] The solution must be pep-8 compliant.
- [ ] Bonus: Build a separate pipeline that uses the following keywords instead of English news sources: Tempus Labs, Eric Lefkofsky, Cancer, Immunotherapy
- [ ] Bonus: Write an integration test for any of the external services your solution connects to.


## Rules of engagement
* We suggest that you establish a four hour timebox to complete the challenge.
* The solution must perform a Python transformation of the data;
 feel free to add any open-source libraries you wish and add additional output files.
* Please document changes required to make the solution resilient to
 failure by taking the following actions:
  * add developer-friendly requirements to functions
  * add comments in the main function that list failures that the solution should
  be designed to handle
* Please run `make clean` and deliver your Python code via repo or zip ahead of the meeting.

## Grading
We will grade your solution with the following guidelines.
 This list is ordered with highest-weighted factors at the top:
1. **Functional correctness**: The solution meets all functional requirements,
 including bonuses.
2. **Code composition and style**: Code follows appropriate coding standards and pep-8 guidelines.
3. **Communication**: The project includes a README and the code is well-commented.


## [Apache Airflow](https://airflow.apache.org)
From the Apache Airflow documentation:

>Airflow is a platform to programmatically author, schedule and monitor workflows.

>Use airflow to author workflows as directed acyclic graphs (DAGs) of tasks. The airflow scheduler executes your tasks on an array of workers while following the specified dependencies. Rich command line utilities make performing complex surgeries on DAGs a snap. The rich user interface makes it easy to visualize pipelines running in production, monitor progress, and troubleshoot issues when needed.

>When workflows are defined as code, they become more maintainable, versionable, testable, and collaborative.

In order to facilitate the use of Airflow, we have included a Dockerfile and a docker-compose.yml that can be used to set up a local airflow development environment. **Make sure to have [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.**

From the root folder, you can execute the following command to run airflow:
```
docker-compose up --build
```
The Airflow UI/Admin Console should now be visible on [http://localhost:8080](http://localhost:8080).

### DAGs
In order to build the data pipeline, it will be necessary to create a DAG. We have provided an example DAG, `dags/sample_dag.py`, that can be used as a reference. Further documentation can be found in the [airflow tutorial](https://airflow.apache.org/tutorial.html) and the [airflow concepts](https://airflow.apache.org/concepts.html) pages.

To load a new DAG into airflow, simply create a new Python file in the `dags` folder that contains an airflow DAG object.

### Python Packages
To install additional Python packages (boto3, pandas, requests, etc.), add them to `requirements.txt`.

### Related Articles/Tutorials
* https://airflow.apache.org/index.html
* https://medium.com/@dustinstansbury/understanding-apache-airflows-key-concepts-a96efed52b1a
* https://speakerdeck.com/artwr/apache-airflow-dataengconf-sf-2017-workshop
* https://github.com/hgrif/airflow-tutorial

## [News API](https://newsapi.org)
A simple REST API that can be used to retrieve breaking headlines and search for articles. **A free News API account is required to obtain an API key.**

| Route             | Description                                                                                                                |
|-------------------|----------------------------------------------------------------------------------------------------------------------------|
| [/v2/top-headlines](https://newsapi.org/docs/endpoints/top-headlines) | Returns live top and breaking headlines for a country, specific category in a country, single source, or multiple sources. |
| [/v2/sources](https://newsapi.org/docs/endpoints/sources) | Returns the subset of news publishers that top headlines are available from. |


## [Amazon S3](https://aws.amazon.com/s3/)
A simple cloud storage service run by Amazon Web Services (AWS). **An AWS account is needed to use AWS S3. Furthermore, AWS has a [free tier](https://aws.amazon.com/free/) that can be used for this challenge.**

Amazon provides a Python SDK (**[boto](http://boto3.readthedocs.io/en/latest/guide/resources.html)**), that provides an easy to use API for interacting with AWS S3.
