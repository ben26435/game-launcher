# Game Launcher

自動啟動原神與崩壞：星穹鐵道，並自動點擊通過開頭畫面進入遊戲主選單。
另提供原神每日自動領取功能（紀行一鍵領取、信件全部領取）。

## 需求

- Python 3.10+
- 原神 / 崩壞：星穹鐵道（已安裝於本機）
- 遊戲內帳號已記住登入狀態

## 安裝依賴套件

```bash
python -m pip install pyautogui pygetwindow opencv-python
```

## 腳本說明

| 檔案 | 功能 |
|------|------|
| `launch_games.py` | 自動啟動兩款遊戲並點擊通過啟動畫面 |
| `genshin_daily.py` | 原神每日自動領取（紀行 + 信件） |

---

## launch_games.py — 遊戲啟動器

### 設定

開啟 `launch_games.py`，修改頂部的遊戲路徑：

```python
GENSHIN_EXE  = r"D:\Genshin Impact\Genshin Impact game\GenshinImpact.exe"
STARRAIL_EXE = r"D:\Star Rail\Games\StarRail.exe"
```

### 使用方式

```bash
python launch_games.py
```

腳本會依序：
1. 啟動原神，等待視窗出現後自動點擊通過啟動畫面
2. 啟動崩壞：星穹鐵道，同上

> 緊急停止：將滑鼠移到螢幕**左上角**即可中斷腳本。

### 可調整參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `LAUNCH_WAIT` | 等待遊戲啟動的秒數 | 15 秒 |
| `CLICK_INTERVAL` | 每次點擊的間隔秒數 | 5 秒 |
| `CLICK_COUNT` | 點擊次數 | 5 次 |

若遊戲載入較慢，可適當增加 `LAUNCH_WAIT`；若啟動動畫較長，可增加 `CLICK_COUNT`。

---

## genshin_daily.py — 原神每日領取

### 首次設定（只需執行一次）

確保原神已開啟並在主畫面，然後執行：

```bash
python genshin_daily.py --setup
```

程式會逐步引導你截圖並框選以下 4 個按鈕：

| 目標 | 位置 |
|------|------|
| 紀行圖示 | 主畫面左側的紀行 icon |
| 一鍵領取 | 進入紀行後的領取按鈕 |
| 信件圖示 | 主畫面的信封 icon |
| 全部領取 | 信件頁面的領取按鈕 |

框選的圖片會儲存在 `assets/genshin/` 資料夾，遊戲 UI 更新後重新執行 `--setup` 即可。

### 每日使用

```bash
python genshin_daily.py
```

腳本會自動：
1. 開啟紀行 → 一鍵領取每日任務 → 關閉
2. 開啟信件 → 全部領取 → 關閉
