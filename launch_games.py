import subprocess
import time
import sys

try:
    import pyautogui
    import pygetwindow as gw
except ImportError:
    print("缺少必要套件，請先執行：pip install pyautogui pygetwindow")
    sys.exit(1)

# ===== 設定遊戲路徑（請修改為你的實際路徑）=====
GENSHIN_EXE = r"D:\Genshin Impact\Genshin Impact game\GenshinImpact.exe"
STARRAIL_EXE = r"D:\Star Rail\Games\StarRail.exe"

# 遊戲視窗標題關鍵字（用來識別視窗）
GENSHIN_WINDOW_TITLES = ["原神", "Genshin Impact"]
STARRAIL_WINDOW_TITLES = ["崩壞：星穹鐵道", "Honkai: Star Rail"]

# 等待遊戲啟動的秒數（視電腦速度調整）
LAUNCH_WAIT = 15
# 啟動後點擊間隔（通過各啟動畫面）
CLICK_INTERVAL = 5
# 點擊次數（通過開頭動畫和進入遊戲的按鈕）
CLICK_COUNT = 5


def wait_for_window(titles: list[str], timeout: int = 60) -> object | None:
    """等待任一指定標題的視窗出現，回傳視窗物件或 None。"""
    print(f"  等待視窗出現：{' / '.join(titles)}（最多 {timeout} 秒）")
    for _ in range(timeout):
        for title in titles:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                return windows[0]
        time.sleep(1)
    return None


def click_through_startup(window, click_count: int, interval: float):
    """聚焦視窗後，連續點擊中央以通過啟動畫面。"""
    try:
        window.activate()
        time.sleep(1)
    except Exception:
        pass

    center_x = window.left + window.width // 2
    center_y = window.top + window.height // 2

    for i in range(1, click_count + 1):
        print(f"  點擊第 {i}/{click_count} 次...")
        pyautogui.click(center_x, center_y)
        time.sleep(interval)


def launch_game(name: str, exe_path: str, window_titles: list[str]):
    print(f"\n{'='*40}")
    print(f"啟動：{name}")
    print(f"路徑：{exe_path}")

    subprocess.Popen([exe_path])
    print(f"  已送出啟動指令，等待 {LAUNCH_WAIT} 秒...")
    time.sleep(LAUNCH_WAIT)

    window = wait_for_window(window_titles)
    if window is None:
        print(f"  [警告] 找不到 {name} 的視窗，跳過自動點擊。")
        return

    print(f"  找到視窗，開始自動點擊通過啟動畫面...")
    click_through_startup(window, CLICK_COUNT, CLICK_INTERVAL)
    print(f"  {name} 完成！")


def main():
    pyautogui.FAILSAFE = True  # 滑鼠移到左上角可緊急停止

    print("遊戲自動啟動腳本")
    print("提示：將滑鼠移到螢幕左上角可緊急停止腳本\n")

    launch_game("原神 Genshin Impact", GENSHIN_EXE, GENSHIN_WINDOW_TITLES)
    launch_game("崩壞：星穹鐵道 Honkai: Star Rail", STARRAIL_EXE, STARRAIL_WINDOW_TITLES)

    print("\n全部完成！")


if __name__ == "__main__":
    main()
