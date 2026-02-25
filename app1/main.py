# main.py - Pocket Tools for Fly.io (Flet 0.27.6)
import os
import time
import threading
import flet as ft

def main(page: ft.Page):
    page.title = "🧰 Pocket Tools"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.GREY_100

    current_tool = "home"
    countdown_active = False

    def show_home(e=None):
        nonlocal current_tool, countdown_active
        current_tool = "home"
        countdown_active = False
        render_home()

    # ========== 手电筒 ==========
    def show_flashlight(e=None):
        nonlocal current_tool
        current_tool = "flashlight"
        page.clean()
        page.bgcolor = ft.colors.WHITE
        page.add(
            ft.Container(
                expand=True,
                content=ft.Column([
                    ft.Icon(ft.icons.WB_SUNNY_OUTLINED, size=100, color=ft.colors.AMBER_700),
                    ft.Text("🔦 手电筒", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("关闭", on_click=show_home, width=200)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )
        page.update()

    # ========== 倒计时 ==========
    def show_timer(e=None):
        nonlocal current_tool
        current_tool = "timer"
        page.clean()
        page.bgcolor = ft.colors.PURPLE_50

        timer_display = ft.Text("00:00", size=60, weight=ft.FontWeight.BOLD)
        minutes_input = ft.TextField(label="分钟", value="5", keyboard_type=ft.KeyboardType.NUMBER, width=100)
        seconds_input = ft.TextField(label="秒", value="0", keyboard_type=ft.KeyboardType.NUMBER, width=100)
        start_btn = ft.ElevatedButton("开始", on_click=start_countdown, width=200)

        def start_countdown(e):
            nonlocal countdown_active
            try:
                mins = int(minutes_input.value or 0)
                secs = int(seconds_input.value or 0)
                total = mins * 60 + secs
                if total <= 0:
                    return

                countdown_active = True
                start_btn.disabled = True
                minutes_input.disabled = True
                seconds_input.disabled = True
                page.update()

                def countdown_worker():
                    nonlocal countdown_active
                    for remaining in range(total, -1, -1):
                        if not countdown_active or current_tool != "timer":
                            break
                        mins, secs = divmod(remaining, 60)
                        timer_display.value = f"{mins:02d}:{secs:02d}"
                        page.update()
                        if remaining > 0:
                            time.sleep(1)

                    if countdown_active and current_tool == "timer":
                        page.snack_bar = ft.SnackBar(ft.Text("⏰ 时间到！"), open=True)
                        page.bgcolor = ft.colors.RED_100
                        page.update()

                    countdown_active = False
                    start_btn.disabled = False
                    minutes_input.disabled = False
                    seconds_input.disabled = False
                    page.update()

                threading.Thread(target=countdown_worker, daemon=True).start()

            except Exception as ex:
                print("Timer error:", ex)

        page.add(
            ft.AppBar(title=ft.Text("⏱️ 倒计时"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                content=ft.Column([
                    timer_display,
                    ft.Row([minutes_input, seconds_input], alignment=ft.MainAxisAlignment.CENTER),
                    start_btn,
                    ft.ElevatedButton("返回", on_click=show_home, width=200)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                alignment=ft.alignment.center,
                padding=20
            )
        )
        page.update()

    # ========== 主页 ==========
    def render_home():
        page.clean()
        page.bgcolor = ft.colors.GREY_100
        tools = [
            ("🔦 手电筒", show_flashlight),
            ("⏱️ 倒计时", show_timer),
        ]
        buttons = [
            ft.ElevatedButton(
                name,
                on_click=handler,
                height=80,
                width=300,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15))
            )
            for name, handler in tools
        ]
        page.add(
            ft.AppBar(title=ft.Text("🧰 Pocket Tools"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Column(buttons, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        )
        page.update()

    render_home()

if __name__ == "__main__":
    # Fly.io 会设置 PORT 环境变量
    port = int(os.environ.get("PORT", 8080))
    # 绑定 0.0.0.0 以接受外部连接
    ft.app(target=main, host="0.0.0.0", port=port)