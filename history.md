# App1 — Lịch sử session (handoff cho Claude trên desktop)

> Mục đích: File này tóm tắt lại toàn bộ những gì phiên **Claude Code trên web**
> (chạy trong repo Hermes) đã làm với dự án **App1**, để **Claude trên desktop**
> (làm việc tại `G:\My Drive\Claude Code\App1`) đọc và nắm được đầy đủ ngữ cảnh.
>
> Lưu ý: đây là bản **tóm tắt trung thực có cấu trúc**, không phải transcript
> nguyên văn từng câu — phần đầu phiên đã được nén lại nên không còn lời thoại
> gốc. Nội dung dưới đây bám theo sự thật trong repo và các quyết định đã chốt.

## 1. App1 là gì

- Mô tả: *"App1 — big project (web + Android via Capacitor)"* (theo
  `app1/package.json`).
- Định danh (tạm, dễ đổi sau): appName `App1`, appId `com.app1.app`, npm name
  `app1`.
- Công nghệ: **Capacitor 6** (`@capacitor/core`, `@capacitor/android`,
  `@capacitor/cli` `^6.1.2`), `webDir: "www"`, `android.allowMixedContent: true`.
- Ý tưởng sản phẩm chi tiết: **chưa có** trong file này — sẽ được ghi riêng vào
  `app1/CONTEXT.md` khi người dùng cung cấp (xem mục 7).

## 2. Bối cảnh xuất phát

Trong repo Hermes đã có sẵn một dự án mobile hoạt động tốt: `gobston/` — một app
Capacitor (web + Android) mà APK được build **tự động** bằng GitHub Actions.
Người dùng muốn mở một "dự án lớn" mới tên **App1** và **tái sử dụng nguyên bộ
pipeline build → APK → GitHub Release** đã được kiểm chứng đó ngay từ đầu.

## 3. Dòng thời gian — phiên web này đã làm gì

1. **Nhân bản setup gobston sang `app1/`.** Chỉ có **5 file được Git theo dõi**
   (thư mục `android/` bị gitignore và được **CI tự sinh lại** bằng
   `npx cap add android`):
   - `app1/package.json` (name `app1`, deps Capacitor 6)
   - `app1/package-lock.json`
   - `app1/capacitor.config.json` (appId `com.app1.app`, appName `App1`)
   - `app1/.gitignore` (`node_modules/`, `android/`, `ios/`, `*.apk`, …)
   - `app1/www/index.html` (copy game của gobston làm điểm khởi đầu)
   - Kèm workflow CI mới: `.github/workflows/android-app1.yml` ("Build App1 APK").
   - Commit: `fdeb2dc` — *"Add app1 project: duplicate Gobston Capacitor + APK CI
     setup"*. Đã push lên nhánh `claude/evaluate-open-design-DQd2j`.
   - `gobston/` **giữ nguyên**, không đụng tới; hai workflow chạy độc lập theo
     path filter riêng.

2. **Hướng dẫn dựng App1 trên máy local của người dùng.** Song song, người dùng
   tạo App1 ở `G:\My Drive\Claude Code\App1` và push lên một **repo GitHub riêng
   tên `app1`** (khác repo Hermes). Các bước đã đi qua: tạo 5 file qua brief →
   `dir` kiểm tra → tạo repo trống trên GitHub → `git init/add/commit/push` →
   xem tab **Actions** → tải APK ở **Releases/Artifacts**. Có lúc `git commit`
   báo *"nothing to commit, working tree clean"* (chẩn đoán: file đã commit từ
   trước hoặc thư mục trống). Người dùng xác nhận **"đã chuyển xong rồi, done"**.

3. **Bàn về lưu brainstorm thành file context.** Yêu cầu ban đầu là
   `context-files/app1-CONTEXT.md`, nhưng phát hiện `context-files/` nằm trong
   `.gitignore` (dòng 18) → file ở đó **không push lên GitHub**. Đã chốt dùng
   `app1/CONTEXT.md` cho khớp quy ước sẵn có `open-design/CONTEXT.md` và được Git
   theo dõi. File `CONTEXT.md` **chưa viết** — đang chờ người dùng dán ý tưởng.

4. **Xuất lịch sử phiên** → chính là file `app1/history.md` này.

## 4. Hai vị trí "App1" (quan trọng — tránh nhầm)

Có **hai** chỗ tên App1, dùng chung cách tiếp cận Capacitor/CI nhưng là hai nơi
khác nhau:

- **(a) `app1/` trong repo Hermes** (`snape1987/hermes`, nhánh
  `claude/evaluate-open-design-DQd2j`) — nơi phiên web này thao tác.
- **(b) `G:\My Drive\Claude Code\App1` trên máy local** → push lên repo GitHub
  **riêng** tên `app1` — nơi Claude desktop thao tác.

Khi đọc file này, Claude desktop cần ý thức mình đang ở (b); còn các commit/CI
mô tả ở mục 3.1 thuộc về (a).

## 5. Build & cài đặt (tóm tắt pipeline trong repo Hermes)

Mỗi lần push có thay đổi trong `app1/**` (hoặc chỉnh workflow) sẽ kích hoạt
`.github/workflows/android-app1.yml`:

1. Checkout → setup Node 20 → setup Java 21 (temurin) → setup Android SDK
   (`platform-tools`, `platforms;android-34`, `build-tools;34.0.0`).
2. `npm install` (trong `app1/`).
3. `npx cap add android` → `npx cap sync android` (sinh lại `app1/android/`).
4. Build: `app1/android` → `./gradlew assembleDebug`.
5. Đổi tên: `app-debug.apk` → `app1-debug.apk`.
6. Upload artifact `app1-debug-apk` + tạo **GitHub Release**: tag
   `app1-apk-build-<số run>`, tên `App1 APK · build <số run>`, đính kèm
   `app1-debug.apk`.

Tải file `.apk` ở **Releases** (hoặc **Artifacts** của lần chạy) → cài trên
Android (bật *"cài từ nguồn không xác định"*).

## 6. Quyết định & quy ước

- Nhánh phát triển: `claude/evaluate-open-design-DQd2j`.
- Tag release của App1 được **đặt namespace riêng** (`app1-apk-build-*`) để
  không đụng tag của gobston (`apk-build-*`).
- Định danh `App1` / `com.app1.app` / `app1` là **placeholder**, đổi tên sau dễ.
- File context "công khai" theo chuẩn Hermes: `CONTEXT.md` nằm trong thư mục
  domain (ví dụ mẫu `open-design/CONTEXT.md`).

## 7. Việc còn dang dở / cần làm tiếp

- **`app1/CONTEXT.md`**: chưa viết — đang chờ người dùng dán **ý tưởng/tính năng
  sản phẩm** App1. Khi có, viết theo khung: intro → `## Idea / Vision` →
  `## Platform & Build` → `## Identity & Conventions` → `## Open questions`.
- **Tên app cuối cùng**: chưa chốt (hiện để `App1`).
- **Branding trong game**: `app1/www/index.html` vẫn còn chữ "Gobston" do copy
  nguyên — cần rebrand lại khi xác định nội dung thật của App1.

## 8. Ghi chú môi trường

- Phiên web chạy trong **container đám mây tạm thời**: mọi thay đổi **phải được
  commit + push** mới được giữ lại; container bị thu hồi sau khi nhàn rỗi.
- Tương tác GitHub ở phiên web đi qua **GitHub MCP tools** (không có `gh` CLI).
- Repo Hermes là monorepo lớn (có submodule `open-design`); App1 chỉ là một thư
  mục con `app1/` bên trong, độc lập với phần còn lại.
