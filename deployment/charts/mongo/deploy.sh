#!/bin/bash
helm upgrade --install mongo oci://registry-1.docker.io/cloudpirates/mongodb --version "0.17.1" -f ./values.yaml
