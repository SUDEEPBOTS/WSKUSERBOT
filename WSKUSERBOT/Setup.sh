#!/usr/bin/env bash
set -e

if [ ! -f .env ]; then
    if [ -f sample.env ]; then
        cp sample.env .env
        echo "Created .env from sample.env — edit it with your values!"
    else
        cat > .env << 'EOF'
API_ID=
API_HASH=
BOT_TOKEN=
MONGO_URI=
OWNER_ID=
WORDSEEK_BOT=@WordSeekBot
EOF
        echo "Created empty .env — fill it in before running."
    fi
    exit 0
fi

echo "[Setup] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[Setup] Installing dependencies..."
pip install --upgrade pip
pip install pyrogram tgcrypto aiohttp pymongo

echo "[Setup] Done! Run with: python -m WSKUSERBOT"
