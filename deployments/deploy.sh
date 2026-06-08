#!/usr/bin/env bash
#
# Deploy the latest mint-ai backend to the Azure host.
#
# Pulls the CI-built image (ghcr.io/jehoi-ga-ada/mint-ai:latest), recreates the
# backend container from it, and verifies the public /privacy page is live.
#
# Run this AFTER the "Build and push Docker image" GitHub Action for your latest
# push has completed — otherwise it just re-pulls the old image.
#
# Overridable via env vars:
#   MINT_SSH_KEY    path to the SSH private key   (default: ~/Downloads/mint-ai-key.pem)
#   MINT_SSH_HOST   user@host                     (default: ubuntu@20.24.250.109)
#   MINT_REMOTE_DIR compose dir on the host       (default: mint-ai)
#
set -euo pipefail

KEY="${MINT_SSH_KEY:-$HOME/Downloads/mint-ai-key.pem}"
HOST="${MINT_SSH_HOST:-ubuntu@20.24.250.109}"
REMOTE_DIR="${MINT_REMOTE_DIR:-mint-ai}"
URL="https://mintai.eastasia.cloudapp.azure.com/privacy"

echo "→ Deploying backend to ${HOST}:${REMOTE_DIR}"
ssh -i "$KEY" -o StrictHostKeyChecking=accept-new "$HOST" \
  "set -e; cd '${REMOTE_DIR}' && docker compose pull mint-backend && docker compose up -d mint-backend && docker compose ps mint-backend"

echo "→ Verifying ${URL}"
for i in $(seq 1 12); do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$URL" || echo 000)"
  echo "  attempt ${i}: HTTP ${code}"
  if [ "$code" = "200" ]; then
    echo "✓ Privacy policy is live at ${URL}"
    exit 0
  fi
  sleep 5
done

echo "✗ ${URL} is not returning 200 yet."
echo "  The CI image may still be building. Re-run this script once the GitHub"
echo "  Action 'Build and push Docker image' has finished."
exit 1
