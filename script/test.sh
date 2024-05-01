#!/bin/sh
export PATHONPATH=`pwd`
# python -m pytest -s --ignore=fe/data
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v --ignore=fe/data
coverage combine
coverage report
coverage html
