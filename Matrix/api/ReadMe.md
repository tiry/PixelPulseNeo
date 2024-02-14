
# API Server

The API Server exposes a REST API using Flask.

The APIServer use the driver, either directly or via IPC.

## Starting the API Server

To start the server:

    scripts/api_server.sh

or run from python (from root directory)

    python -m Matrix.api.server

Server by default will run on localhost:5000

## Debug model

To run with debug mode

    python -m Matrix.api.server --debug

In debug mode, because Flask uses `WERKZEUG` to run 2 python interpreter there are technically 2 instances of the command executor running. This will created duplicate display with the `RGBMatrixEmulator` and will produce funky results with a real matrix.

## REST API

The API endpoint is exposed via RESTX on `http://localhost:5000/api/`

<img src="../../pictures/openapi.png" width="500px"/>

Get Swagger-UI from : http://localhost:5000/

Get OpenAPI definition from: http://localhost:5000/api/swagger.json


The Web interface is exposed on `http://localhost:5000/web/`

