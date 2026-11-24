#!/bin/bash
# CI script for Linux and macOS
# Викликається з GitHub Actions workflow: встановлення → складання → запуск → тести
set -e

echo "=== Installing dependencies ==="
npm ci

echo "=== Building executable ==="
npm run build

echo "=== Smoke test: running build/hello/hello ==="
OUTPUT="$(./build/hello/hello)"
echo "$OUTPUT"
if [ "$OUTPUT" != "Hello, World!" ]; then
  echo "ERROR: unexpected output from hello executable"
  exit 1
fi

echo "=== Running unit tests (with coverage) ==="
npm run test:coverage

echo "=== CI script completed successfully ==="
