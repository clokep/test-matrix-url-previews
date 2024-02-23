set -xe

CONTAINER=synapse-url-preview-test

VERSION=${1:-latest}
echo "Testing Synapse $VERSION"

# Clean-up.
if [ -d "$VERSION" ]; then
  rm -r $VERSION
fi
mkdir -p $VERSION/data

echo "Generating the config"
# Note that the SYNAPSE_CONFIG_DIR and SYNAPSE_CONFIG_PATH environment variables
# aren't needed in newer Synapses, but v1.0.0 is strict.
docker run -it --rm \
    --mount type=bind,src=$(pwd)/data,dst=/data \
    -e SYNAPSE_SERVER_NAME=localhost:8888 \
    -e SYNAPSE_REPORT_STATS=no \
    -e SYNAPSE_CONFIG_DIR=/data \
    -e SYNAPSE_CONFIG_PATH=/data/homeserver.yaml \
    matrixdotorg/synapse:v1.80.0 generate

# Dump some info.
docker inspect -f '{{ .Created }}' matrixdotorg/synapse:$VERSION > $VERSION/created

# Enable URL previews.
echo "Updating the config"
echo "
# Old versions use a broken path for the database.
database:
  name: sqlite3
  args:
    database: /data/homeserver.db

# Old versions have broke IPv6 support.
listeners:
  - port: 8488
    tls: false
    bind_addresses: ['0.0.0.0']
    type: http
    x_forwarded: true

    resources:
      - names: [client, federation]
        compress: false

# Configure the media to be stored in data.
media_store_path: /data/media_store
uploads_path: /data/uploads

# Enable dynamic thumbnails.
dynamic_thumbnails: true

# Enable URL previews & dynamic thumbnails.
url_preview_enabled: true

url_preview_ip_range_blacklist:
  - '127.0.0.0/8'
  - '10.0.0.0/8'
  - '172.16.0.0/12'
  - '192.168.0.0/16'
  - '100.64.0.0/10'
  - '192.0.0.0/24'
  - '169.254.0.0/16'
  - '192.88.99.0/24'
  - '198.18.0.0/15'
  - '192.0.2.0/24'
  - '198.51.100.0/24'
  - '203.0.113.0/24'
  - '224.0.0.0/4'
  - '::1/128'
  - 'fe80::/10'
  - 'fc00::/7'
  - '2001:db8::/32'
  - 'ff00::/8'
  - 'fec0::/10'
" >> $VERSION/data/homeserver.yaml

sed -i "" -e "s_/homeserver.log_/data/homeserver.log_" $VERSION/data/localhost:8888.log.config

# Run the Docker container.
echo "Starting Synapse"
# Note that the environment variables aren't needed in newer Synapses, but
# v1.0.0 is strict.
docker run -d --name $CONTAINER \
    --mount type=bind,src=$(pwd)/$VERSION/data,dst=/data \
    -e SYNAPSE_SERVER_NAME=localhost:8888 \
    -e SYNAPSE_REPORT_STATS=no \
    -e SYNAPSE_CONFIG_DIR=/data \
    -e SYNAPSE_CONFIG_PATH=/data/homeserver.yaml \
    -p 8888:8488 \
    matrixdotorg/synapse:$VERSION

# Let the container come up (old versions need a bit...)
sleep 10

# Generate a user.
echo "Creating a local user"
docker exec -it $CONTAINER register_new_matrix_user \
  http://localhost:8488 -c /data/homeserver.yaml \
  --user alice \
  --password password \
  --no-admin

# Log into the server.
echo "Logging in"
# Use r0 to be compatible with old versions.
ACCESS_TOKEN=$(curl http://localhost:8888/_matrix/client/r0/login -X POST \
  --data '{"identifier": { "type": "m.id.user", "user": "alice"}, "type": "m.login.password", "password": "password"}' | jq -r .access_token)

# Request the URL previews.
echo "Getting URL previews"
python run-tests.py http://localhost:8888 $ACCESS_TOKEN

# Kill the Docker container.
echo "Cleaning up"
docker stop $CONTAINER
docker rm $CONTAINER
