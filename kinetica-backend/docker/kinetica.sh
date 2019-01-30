#!/usr/bin/env bash
sed -i "s#license_key.*#license_key = ${LICENSE_KEY}#" /opt/gpudb/core/etc/gpudb.conf
ldconfig
/opt/gpudb-docker-start.sh
