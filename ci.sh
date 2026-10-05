#!/bin/bash
# CI script for Linux and macOS
# Викликається з GitHub Actions workflow
set -e

echo "=== Installing dependencies ==="
npm install

echo "=== Running tests ==="
npm test

echo "=== CI script completed successfully ==="
