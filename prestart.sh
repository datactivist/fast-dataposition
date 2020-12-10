#! /usr/bin/env bash

# Let the DB start
sleep 10;
# Run migrations
export PYTHONPATH=$PYTHONPATH:.  # dirty
alembic upgrade head