"""
原神每日自動領取腳本

首次使用請先執行設定模式：
    python genshin_daily.py --setup

之後每次領取：
    python genshin_daily.py
"""

import sys
import time
import tkinter as tk
from pathlib import Path

try:
    import pyautogui
    import pygetwindow as gw
    from PIL import Image, ImageGrab, ImageTk
except ImportError:
    print("缺少套件，請執行：pip install pyautogui pygetwindow opencv-python")
    sys.exit(1)

ASSETS_DIR = Path(__file__).parent / "assets" / "genshin"
CONFIDENCE = 0.8

# 各按鈕的參考圖片路徑，optional=True 表示缺少時不阻止腳本執行
TARGETS = {
    "battle_pass_icon":  (ASSETS_DIR / "battle_pass_icon.png",  "紀行（任務日誌）圖示",        False),
    "battle_pass_claim": (ASSETS_DIR / "battle_pass_claim.png", "紀行頁面的「一鍵領取」按鈕",  False),
    "mail_icon":         (ASSETS_DIR / "mail_icon.png",         "信件圖示",                    False),
    "mail_claim_all":    (ASSETS_DIR / "mail_claim_all.png",    "信件頁面的「全部領取」按鈕",  True),
    "mail_confirm":      (ASSETS_DIR / "mail_confirm.png",      "領取後的「確定」按鈕",        True),
}


# ── 設定模式 ──────────────────────────────────────────────────

def select_region_on_screenshot(screenshot: Image.Image, prompt: str) -> Image.Image | None:
    """顯示全螢幕截圖，讓使用者拖曳框選區域，回傳裁切後的圖片。"""
    result = []

    root = tk.Tk()
    root.title(prompt)
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)

    # 縮放截圖以符合螢幕（多螢幕環境下可能需要）
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


def run_setup():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    print("=== 設定模式 ===")
    print("請先開啟原神並進入主畫面，設定過程中請切換回遊戲視窗。")
    print("每個步驟會截取當前螢幕，讓你用滑鼠拖曳框選對應按鈕。\n")

    for key, (path, description, optional) in TARGETS.items():
        tag = "（可選）" if optional else "（必要）"
        if path.exists():
            ans = input(f"  [{description}]{tag} 已有參考圖，重新擷取？(y/N) ").strip().lower()
            if ans != "y":
                continue

        if optional:
            ans = input(f"\n{tag} 「{description}」—— 現在畫面上看得到嗎？(y/N) ").strip().lower()
            if ans != "y":
                print(f"  已跳過，之後有信件時可重新執行 --setup 補上。")
                continue

        input(f"\n步驟：請在遊戲中找到「{description}」，讓它顯示在畫面上，\n然後回到這裡按 Enter 開始截圖...")
        time.sleep(0.5)

        screenshot = pyautogui.screenshot()
        cropped = select_region_on_screenshot(screenshot, description)

        if cropped:
            cropped.save(str(path))
            print(f"  已儲存：{path.name}  ({cropped.width}x{cropped.height})")
        else:
            print(f"  已跳過：{description}")

    print("\n設定完成！執行 python genshin_daily.py 開始自動領取。")


# ── 領取邏輯 ──────────────────────────────────────────────────

def get_window_region(window) -> tuple:
    """回傳視窗所在螢幕區域 (left, top, width, height)，支援多螢幕。"""
    return (window.left, window.top, window.width, window.height)


def find_and_click(image_path: Path, region: tuple, timeout: int = 8, clicks: int = 3) -> bool:
    """截取全部螢幕後在視窗區域內搜尋圖片並點擊，支援多螢幕。
    原神需要按住 ALT 才能釋放游標，點擊前後自動處理。
    """
    needle = Image.open(str(image_path))
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            pyautogui.keyDown("alt")
            screenshot = ImageGrab.grab(all_screens=True)
            loc = pyautogui.locate(needle, screenshot, confidence=CONFIDENCE, region=region)
            if loc:
                center = pyautogui.center(loc)
                for _ in range(clicks):
                    pyautogui.click(center)
                    time.sleep(0.3)
                pyautogui.keyUp("alt")
                return True
        except Exception:
            pass
        finally:
            pyautogui.keyUp("alt")
        time.sleep(0.5)
    return False


def claim_battle_pass(region: tuple):
    print("\n[紀行] 開啟紀行頁面...")
    if not find_and_click(TARGETS["battle_pass_icon"][0], region):
        print("  [失敗] 找不到紀行圖示，請確認主畫面可見")
        return
    time.sleep(2)

    print("[紀行] 一鍵領取每日任務...")
    if find_and_click(TARGETS["battle_pass_claim"][0], region):
        print("  領取成功")
        time.sleep(1.5)
    else:
        print("  [跳過] 找不到一鍵領取按鈕（可能今日已領取或尚未完成任務）")

    pyautogui.keyUp("alt")
    pyautogui.press("escape")
    time.sleep(1)


def claim_mail(region: tuple):
    print("\n[信件] 開啟信件...")
    if not find_and_click(TARGETS["mail_icon"][0], region):
        print("  [失敗] 找不到信件圖示，請確認主畫面可見")
        return
    time.sleep(2)

    print("[信件] 全部領取...")
    claim_path = TARGETS["mail_claim_all"][0]
    if not claim_path.exists():
        print("  [跳過] 尚未設定「全部領取」參考圖，請有信件時執行 --setup 補上")
    elif find_and_click(claim_path, region):
        print("  領取成功")
        time.sleep(1.5)
        find_and_click(TARGETS["mail_confirm"][0], region, timeout=3)
        time.sleep(1)
    else:
        print("  [跳過] 找不到全部領取按鈕（可能無未讀信件）")

    pyautogui.keyUp("alt")
    pyautogui.press("escape")
    time.sleep(1)


def run_daily():
    missing = [desc for key, (path, desc, optional) in TARGETS.items()
               if not optional and not path.exists()]
    if missing:
        print("缺少以下參考圖片，請先執行：python genshin_daily.py --setup")
        for m in missing:
            print(f"  - {m}")
        return

    windows = gw.getWindowsWithTitle("原神") or gw.getWindowsWithTitle("Genshin Impact")
    if not windows:
        print("[錯誤] 找不到原神視窗，請先開啟遊戲並登入到主畫面")
        return

    window = windows[0]
    print("聚焦原神視窗...")
    window.activate()
    time.sleep(1.5)
    region = get_window_region(window)

    pyautogui.FAILSAFE = True
    print("提示：滑鼠移到左上角可緊急停止\n")

    claim_battle_pass(region)
    claim_mail(region)

    print("\n每日領取完成！")


# ── 入口 ─────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--setup" in sys.argv:
        run_setup()
    else:
        run_daily()
