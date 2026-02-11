# main.py - Pocket Tools: 多功能手机工具箱
import os
import time
from datetime import datetime
import flet as ft

def main(page: ft.Page):
    page.title = "🧰 Pocket Tools"
    page.padding = 0
    page.theme_mode = "light"
    page.window_width = 400
    page.window_height = 800

    # ========== 全局状态 ==========
    current_tool = "home"
    flashlight_on = False
    countdown_active = False
    countdown_seconds = 0
    countdown_start_time = None

    # ========== 工具页面 ==========
    def show_home(e=None):
        nonlocal current_tool
        current_tool = "home"
        update_ui()

    def show_flashlight(e=None):
        nonlocal current_tool, flashlight_on
        current_tool = "flashlight"
        flashlight_on = True
        page.bgcolor = "#ffffff"
        page.overlay.clear()
        page.add(
            ft.Container(
                expand=True,
                content=ft.Column([
                    ft.IconButton(ft.icons.FLASH_ON, icon_size=100, disabled=True),
                    ft.Text("🔦 手电筒", size=24),
                    ft.ElevatedButton("关闭", on_click=show_home, width=200)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )
        page.update()

    def show_level(e=None):
        nonlocal current_tool
        current_tool = "level"
        page.bgcolor = ft.colors.BLUE_50
        page.overlay.clear()
        page.clean()

        tilt_x = ft.Text("X: 0°", size=24, weight="bold")
        tilt_y = ft.Text("Y: 0°", size=24, weight="bold")
        bubble = ft.Container(width=40, height=40, bgcolor=ft.colors.RED, border_radius=20)

        def on_device_tilt(data):
            if current_tool != "level":
                return
            try:
                x = float(data.get("x", 0))
                y = float(data.get("y", 0))
                tilt_x.value = f"X: {x:.1f}°"
                tilt_y.value = f"Y: {y:.1f}°"
                # 移动气泡（简化版）
                bubble.left = max(0, min(300, 150 + x * 3))
                bubble.top = max(0, min(500, 250 - y * 3))
                page.update()
            except:
                pass

        # 注册 JS 回调
        page.on_event("device_tilt", on_device_tilt)

        # 注入 JS 监听陀螺仪
        page.run_js("""
        if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
            DeviceOrientationEvent.requestPermission().then(permission => {
                if (permission === 'granted') {
                    window.addEventListener('deviceorientation', (e) => {
                        window.flet_app.send('device_tilt', {x: e.gamma, y: e.beta});
                    });
                }
            }).catch(console.error);
        } else {
            // 非 iOS 设备直接监听
            window.addEventListener('deviceorientation', (e) => {
                window.flet_app.send('device_tilt', {x: e.gamma, y: e.beta});
            });
        }
        """)

        level_view = ft.Stack([
            ft.Container(
                width=360, height=540,
                bgcolor=ft.colors.WHITE,
                border_radius=20,
                padding=20,
                content=ft.Column([tilt_x, tilt_y])
            ),
            ft.Container(
                width=360, height=540,
                border=ft.border.all(2, ft.colors.BLACK),
                border_radius=20,
                content=ft.Stack([
                    bubble
                ], width=360, height=540)
            )
        ], width=360, height=540)

        page.add(
            ft.AppBar(title=ft.Text("水平仪"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                content=level_view,
                alignment=ft.alignment.center,
                padding=20
            ),
            ft.ElevatedButton("返回", on_click=show_home, width=200)
        )
        page.update()

    def show_timer(e=None):
        nonlocal current_tool, countdown_active, countdown_seconds
        current_tool = "timer"
        page.clean()
        page.bgcolor = ft.colors.PURPLE_50

        timer_display = ft.Text("00:00", size=60, weight="bold")
        minutes_input = ft.TextField(label="分钟", value="5", keyboard_type="number", width=100)
        seconds_input = ft.TextField(label="秒", value="0", keyboard_type="number", width=100)

        def start_countdown(e):
            nonlocal countdown_active, countdown_seconds, countdown_start_time
            try:
                mins = int(minutes_input.value or 0)
                secs = int(seconds_input.value or 0)
                total = mins * 60 + secs
                if total <= 0:
                    return
                countdown_seconds = total
                countdown_active = True
                countdown_start_time = time.time()
                update_timer()
            except:
                pass

        def update_timer():
            nonlocal countdown_active, countdown_seconds
            if not countdown_active:
                return
            elapsed = time.time() - countdown_start_time
            remaining = max(0, countdown_seconds - int(elapsed))
            mins, secs = divmod(remaining, 60)
            timer_display.value = f"{mins:02d}:{secs:02d}"
            if remaining <= 0:
                countdown_active = False
                page.show_snack_bar(ft.SnackBar(ft.Text("⏰ 时间到！"), open=True))
                page.bgcolor = ft.colors.RED_100
            page.update()
            if countdown_active:
                page.run_js(f"setTimeout(() => window.flet_app.send('update_timer', {{}}), 1000)")

        page.on_event("update_timer", lambda _: update_timer())

        page.add(
            ft.AppBar(title=ft.Text("倒计时"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                content=ft.Column([
                    timer_display,
                    ft.Row([minutes_input, seconds_input], alignment=ft.MainAxisAlignment.CENTER),
                    ft.ElevatedButton("开始", on_click=start_countdown, width=200),
                    ft.ElevatedButton("返回", on_click=show_home, width=200)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                alignment=ft.alignment.center,
                padding=20
            )
        )
        page.update()

    # ========== 主页 ==========
    def update_ui():
        page.clean()
        page.bgcolor = ft.colors.GREY_100

        tools = [
            ("🔦 手电筒", show_flashlight),
            ("📏 水平仪", show_level),
            ("⏱️ 倒计时", show_timer),
            ("🌙 护眼模式", lambda e: page.go("/dark")),
        ]

        tool_buttons = []
        for name, handler in tools:
            tool_buttons.append(
                ft.ElevatedButton(name, on_click=handler, height=80, width=300, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15)))
            )

        page.add(
            ft.AppBar(title=ft.Text("🧰 Pocket Tools"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Column(tool_buttons, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        )
        page.update()

    # 初始化
    update_ui()

# ========== 启动 ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.app(target=main, host="0.0.0.0", port=port)