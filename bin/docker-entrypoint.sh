#!/bin/bash


cd /app
export EDGEDB_CLIENT_TLS_SECURITY=insecure
edgedb instance link edgedb --non-interactive --trust-tls-cert --overwrite
edgedb  -I edgedb 
edgedb migrate 
edgedb-py --file /app/wishlist/query/__init__.py --tls-securit insecure
hypercorn --reload --access-log - main:app