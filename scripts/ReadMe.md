
# Command Server

## Execute a command as root

    sudo -E scripts/run_cmd_as_root.sh <command_name> <duration>

## Start the Command Server as root is listen mode

    sudo -E scripts/start_cmd_server.sh

# Command CLI

    python -m Matrix.driver.ipc.client --remotecli

# API and FrontEnd

## Be sure to build the front end

    cd pixel-pulse-neo-client

    npm install

    npm run build

## Start REST API Server

    python -m Matrix.api.server 

    python -m Matrix.api.server  &> "api_server.log" & echo $! > "api_server.pid"

