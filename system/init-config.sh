#!/bin/bash

# Define the configuration directory and file paths
config_dir="/etc/PixelPulseNeo"
config_file="${config_dir}/secrets.conf"

# Check if the configuration directory exists, create it if not
if [ ! -d "$config_dir" ]; then
    echo "Creating configuration directory: $config_dir"
    mkdir -p "$config_dir"
fi

# Initialize the configuration file with variable assignments
echo "Initializing environment configuration file: $config_file"
cat > "$config_file" <<EOF

MTA_API_KEY=
MTA_SIRI_API_KEY=

SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
SPOTIPY_REDIRECT_URI=http://127.0.0.1:3099

EOF

echo "Configuration file initialized"
