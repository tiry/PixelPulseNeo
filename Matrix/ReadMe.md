
## API Module

Contains a Flask (`flask_restx`) based REST Enpoint exposing an OpenAPI API used by the Web FrontEnd.

## Driver

Contains the `CommandExector` code and all related features:

 - command system
 - playlist / schedule logic
 - IPC related code

## Tests

The test folder contains the Unit tests.

To run the tests:

From the root folder

    python -m unittest

Or to run a specific test suite

    python -m unittest Matrix.tests.test_cmdexec

## End 2 End testing

To run end to end test with IPC enabled:

    python -m  Matrix.tests.test_end2end --ipc

## Models

Store Models objects (Pydantic and RestX).

NB: this is a mess for now 

