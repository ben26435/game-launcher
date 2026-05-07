"""
遊戲自動啟動腳本

首次使用請先執行設定模式，分別截圖兩款遊戲的啟動畫面按鈕：
    python launch_games.py --setup

之後每次啟動：
    python launch_games.py
"""

import subprocess
import sys
import time
import tkinter as tk
from pathlib import Path

try:
    import pyautogui
    import pygetwindow as gw
    from PIL import Image, ImageGrab, ImageTk
except ImportError:
    print("缺少必要套件，請先執行：pip install pyautogui pygetwindow opencv-python Pillow")
    sys.exit(1)

# ===== 設定遊戲路徑（請修改為你的實際路徑）=====
GENSHIN_EXE  = r"D:\Genshin Impact\Genshin Impact game\GenshinImpact.exe"
STARRAIL_EXE = r"D:\Star Rail\Games\StarRail.exe"

# 遊戲視窗標題（中英文皆可識別）
GENSHIN_WINDOW_TITLES  = ["原神", "Genshin Impact"]
STARRAIL_WINDOW_TITLES = ["崩壞：星穹鐵道", "Honkai: Star Rail"]

# 等待遊戲視窗出現的最長秒數
LAUNCH_WAIT = 60
# 每個啟動畫面按鈕的最長等待秒數
SCREEN_TIMEOUT = 30
# 圖像辨識信心值
ASSETS_DIR = Path(__file__).parent / "assets"

# 各遊戲的啟動畫面按鈕，依序點擊直到進入主選單
# 每個 tuple：(圖片路徑, 說明, optional, 信心值)
GENSHIN_SCREENS = [
    (ASSETS_DIR / "genshin" / "start_enter.png",   "第一次點擊進入（標題畫面）", False, 0.8),
    (ASSETS_DIR / "genshin" / "start_enter_2.png", "第二次點擊進入",            False, 0.7),
]
STARRAIL_SCREENS = [
    (ASSETS_DIR / "starrail" / "start_enter.png",   "第一次點擊進入（標題畫面）", False, 0.8),
    (ASSETS_DIR / "starrail" / "start_enter_2.png", "第二次點擊進入",            False, 0.8),
]


# ── 設定模式 ──────────────────────────────────────────────────

def select_region_on_screenshot(screenshot: Image.Image, prompt: str) -> Image.Image | None:
    """顯示全螢幕截圖，讓使用者拖曳框選區域，回傳裁切後的圖片。"""
    result = []

    root = tk.Tk()
    root.title(prompt)
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    img_resized = screenshot.resize((screen_w, screen_h), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(img_resized)

    scale_x = screenshot.width / screen_w
    scale_y = screenshot.height / screen_h

    canvas = tk.Canvas(root, cursor="cross", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

    label = tk.Label(root, text=f"拖曳框選：{prompt}　（Esc 跳過）",
                     bg="black", fg="yellow", font=("Arial", 14, "bold"))
    label.place(x=10, y=10)

    state = {}

    def on_press(e):
        state["x0"], state["y0"] = e.x, e.y
        state["rect"] = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="red", width=2)

    def on_drag(e):
        canvas.coords(state["rect"], state["x0"], state["y0"], e.x, e.y)

    def on_release(e):
        x1 = int(min(state["x0"], e.x) * scale_x)
        y1 = int(min(state["y0"], e.y) * scale_y)
        x2 = int(max(state["x0"], e.x) * scale_x)
        y2 = int(max(state["y0"], e.y) * scale_y)
        if x2 - x1 > 5 and y2 - y1 > 5:
            result.append(screenshot.crop((x1, y1, x2, y2)))
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", lambda _: root.destroy())
    root.mainloop()

    return result[0] if result else None


def setup_game(game_name: str, exe_path: str, window_titles: list[str], screens: list):
    print(f"\n{'='*40}")
    print(f"設定：{game_name}")

    print(f"  啟動遊戲中...")
    subprocess.Popen([exe_path])

    window = wait_for_window(window_titles, timeout=LAUNCH_WAIT)
    if window is None:
        print(f"  [警告] 找不到 {game_name} 視窗，請手動開啟後重試。")
        return
    print(f"  遊戲已開啟，請等待畫面載入後依提示操作。")

    for path, description, optional, _ in screens:
        path.parent.mkdir(parents=True, exist_ok=True)
        tag = "（可選）" if optional else "（必要）"

        if path.exists():
            ans = input(f"\n  [{description}]{tag} 已有參考圖，重新擷取？(y/N) ").strip().lower()
            if ans != "y":
                continue

        if optional:
            ans = input(f"\n{tag} 「{description}」—— 現在畫面上看得到嗎？(y/N) ").strip().lower()
            if ans != "y":
                print("  已跳過。")
                continue

        input(f"\n步驟：讓「{description}」出現在遊戲畫面上，\n然後回到這裡按 Enter 開始截圖...")
        time.sleep(0.5)

        screenshot = pyautogui.screenshot()
        cropped = select_region_on_screenshot(screenshot, description)

        if cropped:
            cropped.save(str(path))
            print(f"  已儲存：{path}  ({cropped.width}x{cropped.height})")
        else:
            print(f"  已跳過：{description}")


def run_setup():
    print("=== 設定模式 ===")
    print("將逐一引導你截圖各遊戲的啟動畫面按鈕。\n")
    setup_game("原神 Genshin Impact",              GENSHIN_EXE,  GENSHIN_WINDOW_TITLES,  GENSHIN_SCREENS)
    setup_game("崩壞：星穹鐵道 Honkai: Star Rail", STARRAIL_EXE, STARRAIL_WINDOW_TITLES, STARRAIL_SCREENS)
    print("\n設定完成！執行 python launch_games.py 開始自動啟動。")


# ── 啟動邏輯 ──────────────────────────────────────────────────

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


def get_window_region(window) -> tuple:
    """回傳視窗所在螢幕區域 (left, top, width, height)，供 locateCenterOnScreen 使用。"""
    return (window.left, window.top, window.width, window.height)


def find_and_click(image_path: Path, confidence: float, region: tuple, timeout: int = SCREEN_TIMEOUT, clicks: int = 3) -> bool:
    """截取全部螢幕後在視窗區域內搜尋圖片並點擊，支援多螢幕。"""
    needle = Image.open(str(image_path))
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            screenshot = ImageGrab.grab(all_screens=True)
            loc = pyautogui.locate(needle, screenshot, confidence=confidence, region=region)
            if loc:
                center = pyautogui.center(loc)
                for _ in range(clicks):
                    pyautogui.click(center)
                    time.sleep(0.3)
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def click_through_screens(window, screens: list):
    """依序等待並點擊各啟動畫面的按鈕。"""
    for path, description, optional, confidence in screens:
        if not path.exists():
            if not optional:
                print(f"  [警告] 缺少參考圖「{description}」，請執行 --setup 設定")
            continue

        try:
            window.activate()
            time.sleep(0.5)
        except Exception:
            pass

        region = get_window_region(window)
        print(f"  等待畫面：{description}...")
        if find_and_click(path, confidence, region):
            print(f"  已點擊：{description}")
            time.sleep(2)
        else:
            if not optional:
                print(f"  [逾時] 找不到「{description}」，可能已通過或畫面不同")


def launch_game(name: str, exe_path: str, window_titles: list[str], screens: list):
    print(f"\n{'='*40}")
    print(f"啟動：{name}")

    subprocess.Popen([exe_path])
    print(f"  已送出啟動指令...")

    window = wait_for_window(window_titles, timeout=LAUNCH_WAIT)
    if window is None:
        print(f"  [警告] 找不到 {name} 的視窗，跳過自動點擊。")
        return

    print(f"  找到視窗，開始辨識啟動畫面...")
    click_through_screens(window, screens)
    print(f"  {name} 完成！")


def check_missing_required(screens: list, game_name: str) -> bool:
    missing = [desc for path, desc, optional, _ in screens if not optional and not path.exists()]
    if missing:
        print(f"[{game_name}] 缺少以下參考圖，請執行 --setup：")
        for m in missing:
            print(f"  - {m}")
        return True
    return False


def main():
    pyautogui.FAILSAFE = True
    print("遊戲自動啟動腳本")
    print("提示：將滑鼠移到螢幕左上角可緊急停止腳本\n")

    has_missing = False
    has_missing |= check_missing_required(GENSHIN_SCREENS,  "原神")
    has_missing |= check_missing_required(STARRAIL_SCREENS, "崩壞：星穹鐵道")
    if has_missing:
        print("\n請先執行：python launch_games.py --setup")
        return

    launch_game("原神 Genshin Impact",              GENSHIN_EXE,  GENSHIN_WINDOW_TITLES,  GENSHIN_SCREENS)
    launch_game("崩壞：星穹鐵道 Honkai: Star Rail", STARRAIL_EXE, STARRAIL_WINDOW_TITLES, STARRAIL_SCREENS)

    print("\n全部完成！")


# ── 入口 ─────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--setup" in sys.argv:
        run_setup()
    else:
        main()
