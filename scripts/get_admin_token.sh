export ADMIN_TOKEN=$(docker logs $SLURK_SERVER_ID 2> /dev/null | sed -n '/admin token:/{n;p;}')
