#!/bin/bash
helm upgrade --install redis oci://registry-1.docker.io/cloudpirates/redis --version "0.27.4" -f ./values.yaml
