#!/bin/bash
set -e

for dir in "iam" "orchestration"; do
  echo "Checking infra/$dir"
  cd infra/$dir

  terraform fmt -check -recursive
  terraform init -backend=false
  terraform validate

  cd ../..
done