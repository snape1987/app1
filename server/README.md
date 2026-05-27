# Gobston Leaderboard — Backend

FastAPI + SQLite. Lưu điểm người chơi, trả bảng xếp hạng cho game client.

## Chạy local (test)

```bash
cd server
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Mở http://localhost:8000/health → `{"ok": true}`.

## API

| Method | Path | Mô tả |
|--------|------|-------|
| GET  | `/health` | healthcheck |
| POST | `/score` | upsert điểm 1 device (best_round/wins chỉ tăng, không tụt) |
| GET  | `/leaderboard?scope=world&limit=100` | top toàn cầu |
| GET  | `/leaderboard?scope=region&region=VN&limit=10` | top khu vực |

Body `POST /score`:
```json
{ "device_id":"abc123", "name":"Bạn", "status_full":"Tomorrow never die",
  "status_rev":3, "wins":5, "best_round":4, "plays":12, "region":"VN" }
```

## Deploy lên VPS (systemd)

```bash
# 1) copy thư mục server/ lên VPS, ví dụ /opt/gobston/server
# 2) cài deps
cd /opt/gobston/server && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 3) tạo service
sudo tee /etc/systemd/system/gobston.service >/dev/null <<'UNIT'
[Unit]
Description=Gobston Leaderboard API
After=network.target

[Service]
WorkingDirectory=/opt/gobston/server
ExecStart=/opt/gobston/server/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload && sudo systemctl enable --now gobston
sudo ufw allow 8000/tcp   # nếu dùng UFW

# 4) client: set API_BASE trong www/index.html = "http://<VPS_IP>:8000"
```

> Bản test dùng HTTP trực tiếp qua port 8000 (game bật `allowMixedContent`).
> Khi public thật nên đặt sau Nginx + HTTPS (Let's Encrypt) và đổi API_BASE sang `https://...`.
