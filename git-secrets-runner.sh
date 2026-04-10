#!/usr/bin/env bash
set -euo pipefail

git secrets --register-aws
git secrets --scan-history
