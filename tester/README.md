# Tester pipeline — tự cài APK vào điện thoại

Tự tải APK mới nhất từ GitHub Releases và `adb install` vào điện thoại Android cắm USB, rồi mở app. Dành cho vòng test nhanh trên máy thật.

## Chuẩn bị (1 lần)
1. Điện thoại: bật **Developer options** → **USB debugging**.
2. Cắm USB vào máy này, chọn **Allow** khi điện thoại hỏi "cho phép gỡ lỗi USB".
3. Kiểm tra: `adb devices` → thấy thiết bị ở trạng thái `device`.
4. `gh auth status` phải đã login (đã có sẵn).

## Cài tay (1 lần, khi cần)
```powershell
powershell -ExecutionPolicy Bypass -File tester\install_latest.ps1
```
→ tải APK mới nhất → `adb install -r` → mở **Bi Vương** trên điện thoại.

## Tự động (cắm máy để đó, có build mới là tự cài)
```powershell
powershell -ExecutionPolicy Bypass -File tester\watch.ps1
```
→ cứ ~60 giây kiểm tra Releases; có tag mới (sau khi push code → CI build xong) là tự cài + mở. Ctrl+C để dừng.

## Quy trình tổng
```
sửa code → git push → GitHub Actions build APK → release mới
        → watch.ps1 phát hiện → adb install vào điện thoại → mở app test
```

## Tham số
- `-Repo`  : repo GitHub (mặc định `snape1987/app1`)
- `-AppId` : package id để mở app (mặc định `com.app1.app`)
- `-IntervalSec` (watch): chu kỳ kiểm tra, mặc định 60s
