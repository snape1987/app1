#!/usr/bin/env bash
# Deploy agent hermes-bivuong lên VPS Hermes (ADDITIVE — không đụng service đang chạy).
# Chạy as root trên droplet:
#   curl -fsSL https://raw.githubusercontent.com/snape1987/app1/main/ops/deploy_hermes_agent.sh | bash
set -euo pipefail

KEY=bivuong
PORT=8006
ROOT=/opt/hermes-$KEY
MASTER_ENV=/opt/hermes-master/.env

# Nguồn code agent generic: tái dùng từ một agent đã deploy (config qua .env)
SRC_AGENT=""
for c in /opt/hermes-stone/agent.py /opt/hermes-tctg/agent.py /opt/hermes-gold/agent.py /opt/hermes-downsub/agent.py; do
  [ -f "$c" ] && SRC_AGENT="$c" && break
done
[ -n "$SRC_AGENT" ] || { echo "Khong tim thay agent.py mau trong /opt/hermes-*"; exit 1; }
echo "==> Dung agent.py mau: $SRC_AGENT"

mkdir -p "$ROOT"
cp "$SRC_AGENT" "$ROOT/agent.py"
SRC_DIR="$(dirname "$SRC_AGENT")"
[ -d "$SRC_DIR/workflow" ] && cp -r "$SRC_DIR/workflow" "$ROOT/" || true

echo "==> Tao .env (BOT_TOKEN/CHAT_ID lay tu master, KHONG in ra)"
BOT_TOKEN=$(grep -E '^BOT_TOKEN=' "$MASTER_ENV" | head -1 | cut -d= -f2-)
CHAT_ID=$(grep -E '^CHAT_ID='   "$MASTER_ENV" | head -1 | cut -d= -f2-)
[ -n "$BOT_TOKEN" ] && [ -n "$CHAT_ID" ] || { echo "Khong doc duoc BOT_TOKEN/CHAT_ID tu $MASTER_ENV"; exit 1; }
cat > "$ROOT/.env" <<ENV
AGENT_PROJECT_NAME=Bi Vương
AGENT_PROJECT_PATH=/opt/bi-vuong
AGENT_SERVICE_NAME=bi-vuong
AGENT_KEY=$KEY
BOT_TOKEN=$BOT_TOKEN
CHAT_ID=$CHAT_ID
ENV
chmod 600 "$ROOT/.env"

echo "==> venv + deps"
python3 -m venv "$ROOT/venv"
"$ROOT/venv/bin/pip" install -q --upgrade pip
"$ROOT/venv/bin/pip" install -q fastapi "uvicorn[standard]" httpx pydantic

echo "==> systemd hermes-$KEY (127.0.0.1:$PORT)"
cat > /etc/systemd/system/hermes-$KEY.service <<UNIT
[Unit]
Description=hermes-$KEY agent
After=network.target

[Service]
WorkingDirectory=$ROOT
EnvironmentFile=$ROOT/.env
ExecStart=$ROOT/venv/bin/uvicorn agent:app --host 127.0.0.1 --port $PORT
Restart=always

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now hermes-$KEY
sleep 2
echo "==> health:"
curl -s "http://127.0.0.1:$PORT/health"; echo
echo "DONE agent hermes-$KEY. Buoc tiep: dang ky key vao master (xem huong dan)."
