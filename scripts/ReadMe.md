
# Command Server

## Execute a command as root

    sudo -E scripts/run_cmd.sh <command_name> <duration>

## Start the Command Server as root is listen mode

    sudo -E scripts/start_cmd_server.sh

# Command CLI

    python -m Matrix.driver.ipc.client --remotecli

# API and FrontEnd

## Start REST API Server

    scripts/api_server.sh

## Build the webapp if needed

To build the web app

    npm install

    npm run build

The resulting static files are located in [pixel-pulse-neo-client/build](pixel-pulse-neo-client/build).

These files are served via the API Server on

    http://localhost:5000/web/

Alternatively, you can also run the web app in debug:

    npm start

# Starting everything as one command

    scripts/serve.sh

