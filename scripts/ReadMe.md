
# Command Server

## Execute a command as root

    sudo -E scripts/run_cmd_as_root.sh <command_name> <duration>

## Start the Command Server as root is listen mode

    sudo -E scripts/start_cmd_server.sh

# Command CLI

    python -m Matrix.driver.ipc.client --remotecli

# API and FrontEnd

## Start REST API Server

    python -m Matrix.api.server 

    python -m Matrix.api.server  &> "api_server.log" & echo $! > "api_server.pid"


## Start UI


    apt-get install npm

    npm install

    cd pixel-pulse-neo-client ; npm start &> "${CURRENT_DIR}/ui.log" & echo $! > "${CURRENT_DIR}/ui.pid"

