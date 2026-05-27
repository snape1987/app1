#!/usr/bin/env python3
"""
Bi Vương — mobile tester (screen-walk + screenshot).
Cài/khởi động app, đi qua các màn, CHỤP screenshot từng bước vào tester/shots/.
Điều khiển theo TEXT (uiautomator) + fallback toạ độ. Màn thiếu -> log 'SKIP', không treo.

Dùng:
  python tester/walk.py              # walk + chụp (giả định app đã cài)
  python tester/walk.py --install    # tải APK mới nhất từ Releases, cài, rồi walk
"""
import argparse
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

APP_ID = "com.app1.app"
REPO = "snape1987/app1"
SHOTS = Path(__file__).parent / "shots"


def adb(*args):
    return subprocess.run(["adb", *args], capture_output=True, text=True)


def adb_bytes(*args):
    return subprocess.run(["adb", *args], capture_output=True).stdout


def devices():
    out = adb("devices").stdout
    return [ln.split("\t")[0] for ln in out.splitlines()[1:] if ln.strip().endswith("\tdevice")]


def wm_size():
    m = re.search(r"(\d+)x(\d+)", adb("shell", "wm", "size").stdout)
    return (int(m.group(1)), int(m.group(2))) if m else (1080, 2400)


def screenshot(name):
    SHOTS.mkdir(parents=True, exist_ok=True)
    data = adb_bytes("exec-out", "screencap", "-p")
    (SHOTS / name).write_bytes(data)
    print(f"  [shot] {name} ({len(data)} bytes)")


def find_text_center(needle):
    """Tìm node có text/content-desc chứa needle (case-insensitive) -> (x,y) tâm, hoặc None."""
    try:
        adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
        xml = adb_bytes("shell", "cat", "/sdcard/ui.xml").decode("utf-8", "replace")
        root = ET.fromstring(xml)
    except Exception:
        return None
    nl = needle.lower()
    for node in root.iter("node"):
        txt = (node.get("text") or "") + " " + (node.get("content-desc") or "")
        if nl in txt.lower():
            nums = re.findall(r"\d+", node.get("bounds") or "")
            if len(nums) == 4:
                return ((int(nums[0]) + int(nums[2])) // 2, (int(nums[1]) + int(nums[3])) // 2)
    return None


def tap(x, y):
    adb("shell", "input", "tap", str(x), str(y))


def step(name, needle=None, frac=None, wait=2.0, size=(1080, 2400)):
    """Tap (theo text hoặc theo frac toạ độ) rồi chụp. Trả True nếu tap thành công."""
    ok = True
    if needle is not None:
        c = find_text_center(needle)
        if c:
            tap(*c)
            print(f"-> tap text '{needle}' @ {c}")
        else:
            ok = False
            print(f"-> tap text '{needle}': SKIP (khong thay)")
            if frac is not None:
                W, H = size
                xy = (int(W * frac[0]), int(H * frac[1]))
                tap(*xy)
                print(f"   fallback tap frac {frac} @ {xy}")
    elif frac is not None:
        W, H = size
        xy = (int(W * frac[0]), int(H * frac[1]))
        tap(*xy)
        print(f"-> tap frac {frac} @ {xy}")
    time.sleep(wait)
    screenshot(name)
    return ok


def install_latest():
    d = tempfile.mkdtemp()
    print("Tai APK moi nhat...")
    subprocess.run(["gh", "release", "download", "--repo", REPO, "--pattern", "*.apk",
                    "--dir", d, "--clobber"], check=True)
    apk = next(Path(d).glob("*.apk"))
    # CI sinh debug keystore mới mỗi build -> chữ ký khác -> phải uninstall truoc
    print(f"adb uninstall {APP_ID} (bo qua neu chua cai)")
    subprocess.run(["adb", "uninstall", APP_ID], capture_output=True, text=True)
    print(f"adb install {apk.name}")
    r = subprocess.run(["adb", "install", str(apk)], capture_output=True, text=True)
    if r.returncode != 0:
        print("INSTALL LOI:", (r.stdout + r.stderr).strip())
        raise SystemExit(1)
    print("install OK")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true", help="tải + cài APK mới nhất trước khi walk")
    args = ap.parse_args()

    devs = devices()
    if not devs:
        print("Khong thay dien thoai (adb devices rong). Cam USB + bat USB debugging.")
        sys.exit(1)
    print(f"Thiet bi: {devs}")

    if args.install:
        install_latest()

    size = wm_size()
    print(f"Man hinh: {size[0]}x{size[1]}")

    def cold():
        """Cold start -> SPA luôn về Trang chủ (tránh resume nhầm màn)."""
        adb("shell", "am", "force-stop", APP_ID)
        time.sleep(0.8)
        adb("shell", "am", "start", "-n", f"{APP_ID}/.MainActivity")
        time.sleep(3.5)

    # Toạ độ frac canh từ ảnh thật 1200x2640 (WebView -> uiautomator không thấy text):
    # nút home: CHƠI~0.56, KHẮC DANH HIỆU~0.63, BẢNG XẾP HẠNG~0.72, ĐỔI TÊN~0.80
    cold(); screenshot("01_home.png")
    step("02_round.png",       frac=(0.5, 0.56),  wait=2.0, size=size)   # CHƠI -> Chọn Round
    step("03_game.png",        frac=(0.5, 0.28),  wait=4.5, size=size)   # Round 1 -> vào trận
    step("04_game_play.png",   frac=None,         wait=3.0, size=size)   # đang chơi
    cold(); step("05_status.png",      frac=(0.5, 0.63), wait=2.0, size=size)  # KHẮC DANH HIỆU
    cold(); step("06_leaderboard.png", frac=(0.5, 0.72), wait=3.5, size=size)  # BẢNG XẾP HẠNG (BXH online)

    print(f"\nXong. Anh o: {SHOTS}")
    print("Gui lai cho Claude review, hoac Claude tu Read neu chay tren may build.")


if __name__ == "__main__":
    main()
