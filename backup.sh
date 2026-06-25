#!/bin/bash
set -e
cd /opt/meshtasturk-bot-pro
mkdir -p backups
TS=$(date +%F-%H%M%S)
tar -czf backups/backup-$TS.tar.gz data .env
echo "✅ Yedek alındı: backups/backup-$TS.tar.gz"
