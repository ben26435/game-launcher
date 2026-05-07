# Game Launcher

自動啟動原神與崩壞：星穹鐵道，並自動點擊通過開頭畫面進入遊戲主選單。

## 需求

- Python 3.10+
- 原神 / 崩壞：星穹鐵道（已安裝於本機）
- 遊戲內帳號已記住登入狀態

## 安裝依賴套件

```bash
python -m pip install pyautogui pygetwindow
```

## 設定

開啟 `launch_games.py`，修改頂部的遊戲路徑：

```python
GENSHIN_EXE  = r"D:\Genshin Impact\Genshin Impact game\GenshinImpact.exe"
STARRAIL_EXE = r"D:\Star Rail\Games\StarRail.exe"
```

## 使用方式

```bash
python launch_games.py
```

腳本會依序：
1. 啟動原神，等待視窗出現後自動點擊通過啟動畫面
2. 啟動崩壞：星穹鐵道，同上

> 緊急停止：將滑鼠移到螢幕**左上角**即可中斷腳本。

## 可調整參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `LAUNCH_WAIT` | 等待遊戲啟動的秒數 | 15 秒 |
| `CLICK_INTERVAL` | 每次點擊的間隔秒數 | 5 秒 |
| `CLICK_COUNT` | 點擊次數 | 5 次 |

若遊戲載入較慢，可適當增加 `LAUNCH_WAIT`；若啟動動畫較長，可增加 `CLICK_COUNT`。
