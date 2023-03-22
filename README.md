# EDG Microservices API Template

## Description

_Example Application Interface using FastAPI framework in Python 3_

This example showcases Repository Pattern in Hexagonal Architecture _(also known as Clean Architecture)_. Here we have two Entities - Books and Authors, whose relationships have been exploited to create CRUD endpoint in REST under OpenAPI standard.

## Installation

- Install all the project dependency using [Pipenv](https://pipenv.pypa.io):

  ```sh
  $ pipenv install --dev
  ```

- Run the application from command prompt:

  ```sh
  $ pipenv run uvicorn api.main:app --reload
  ```

- You can also open a shell inside virtual environment:

  ```sh
  $ pipenv shell
  ```

- Open `localhost:8000/docs` for API Documentation

- Open `localhost:8000/graphql` for GraphQL Documentation

_*Note:* In case you are not able to access `pipenv` from you `PATH` locations, replace all instances of `pipenv` with `python3 -m pipenv`._

## Testing

For Testing, `unittest` module is used for Test Suite and Assertion, whereas `pytest` is being used for Test Runner and Coverage Reporter.

- Run the following command to initiate test:
  ```sh
  $ pipenv run pytest
  ```