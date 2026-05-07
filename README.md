# Game Launcher

自動啟動原神與崩壞：星穹鐵道，使用圖像辨識點擊通過啟動畫面進入遊戲主選單。
另提供原神每日自動領取功能（紀行一鍵領取、信件全部領取）。

## 需求

- Python 3.10+
- 原神 / 崩壞：星穹鐵道（已安裝於本機）
- 遊戲內帳號已記住登入狀態

## 安裝依賴套件

```bash
python -m pip install pyautogui pygetwindow opencv-python Pillow
```

## 腳本說明

| 檔案 | 功能 |
|------|------|
| `launch_games.py` | 自動啟動兩款遊戲並點擊通過啟動畫面 |
| `genshin_daily.py` | 原神每日自動領取（紀行 + 信件） |

> 緊急停止：執行中將滑鼠移到螢幕**左上角**即可中斷腳本。

---

## launch_games.py — 遊戲啟動器

### 設定遊戲路徑

開啟 `launch_games.py`，修改頂部的遊戲路徑：

```python
GENSHIN_EXE  = r"D:\Genshin Impact\Genshin Impact game\GenshinImpact.exe"
STARRAIL_EXE = r"D:\Star Rail\Games\StarRail.exe"
```

### 首次設定（只需執行一次）

腳本會自動啟動遊戲，引導你截圖框選各啟動畫面的按鈕：

```bash
python launch_games.py --setup
```

需要對每款遊戲各截圖 2 張（第一次與第二次點擊進入的畫面）。
截圖存放於 `assets/` 資料夾（已加入 `.gitignore`，不會上傳至 GitHub）。

### 每次啟動

```bash
python launch_games.py
```

腳本會依序：
1. 啟動原神 → 圖像辨識啟動畫面 → 按住 ALT 點擊通過 → 釋放滑鼠
2. 啟動崩壞：星穹鐵道 → 同上

### 技術說明

- 使用 `ImageGrab.grab(all_screens=True)` 截取全部螢幕，支援雙螢幕
- 點擊時按住 ALT 釋放遊戲對滑鼠的鎖定
- 找到按鈕後連點 3 次確保觸發

---

## genshin_daily.py — 原神每日領取

### 首次設定（只需執行一次）

確保原神已在主畫面，然後執行：

```bash
python genshin_daily.py --setup
```

程式會逐步引導你截圖框選以下按鈕：

| 目標 | 說明 | 必要 |
|------|------|------|
| 紀行圖示 | 主畫面左側的紀行 icon | 必要 |
| 一鍵領取 | 進入紀行後的領取按鈕 | 必要 |
| 信件圖示 | 主畫面的信封 icon | 必要 |
| 全部領取 | 信件頁面的領取按鈕 | 可選（無信件時可跳過，之後補截） |

截圖存放於 `assets/genshin/` 資料夾。遊戲 UI 更新後重新執行 `--setup` 即可。

### 每日使用

```bash
python genshin_daily.py
```

腳本會自動：
1. 開啟紀行 → 一鍵領取每日任務 → 關閉
2. 開啟信件 → 全部領取 → 關閉
