# main.py - Flet 0.27.6 Web 模式兼容版（同步）
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

    # ========== 主页 ==========
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

    # ========== 水平仪 ==========
    def show_level(e=None):
        nonlocal current_tool
        current_tool = "level"
        page.clean()
        page.bgcolor = ft.colors.BLUE_50

        tilt_x = ft.Text("X: 0°", size=24, weight=ft.FontWeight.BOLD)
        tilt_y = ft.Text("Y: 0°", size=24, weight=ft.FontWeight.BOLD)
        bubble = ft.Container(width=40, height=40, bgcolor=ft.colors.RED, border_radius=20)

        level_area = ft.Stack(
            [
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
                    content=ft.Stack([bubble], width=360, height=540)
                )
            ],
            width=360,
            height=540
        )

        def on_device_tilt(e):
            if current_tool != "level":
                return
            data = e.data
            try:
                x = float(data.get("x", 0))
                y = float(data.get("y", 0))
                tilt_x.value = f"X: {x:.1f}°"
                tilt_y.value = f"Y: {y:.1f}°"
                bubble.left = max(0, min(300, 150 + x * 3))
                bubble.top = max(0, min(500, 250 - y * 3))
                page.update()
            except Exception as ex:
                print("Tilt error:", ex)

        page.on_event("device_tilt", on_device_tilt)

        # 注入 JS 监听陀螺仪
        page.run_js("""
        const sendTilt = (e) => {
            window.flet_app.send('device_tilt', {x: e.gamma, y: e.beta});
        };
        if (typeof DeviceOrientationEvent !== 'undefined' && 
            typeof DeviceOrientationEvent.requestPermission === 'function') {
            DeviceOrientationEvent.requestPermission().then(permission => {
                if (permission === 'granted') {
                    window.addEventListener('deviceorientation', sendTilt);
                }
            }).catch(console.error);
        } else {
            window.addEventListener('deviceorientation', sendTilt);
        }
        """)

        page.add(
            ft.AppBar(title=ft.Text("📏 水平仪"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(content=level_area, alignment=ft.alignment.center, padding=20),
            ft.ElevatedButton("返回", on_click=show_home, width=200)
        )
        page.update()

    # ========== 倒计时（非阻塞版）==========
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

                # 启动后台线程（避免阻塞 UI）
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

                    if countdown_active:
                        page.snack_bar = ft.SnackBar(ft.Text("⏰ 时间到！"), open=True)
                        page.bgcolor = ft.colors.RED_100
                        page.update()

                    # 重置按钮
                    countdown_active = False
                    start_btn.disabled = False
                    minutes_input.disabled = False
                    seconds_input.disabled = False
                    page.update()

                threading.Thread(target=countdown_worker, daemon=True).start()

            except Exception as ex:
                print("Timer error:", ex)

        def stop_countdown(e):
            nonlocal countdown_active
            countdown_active = False

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

    # ========== 渲染主页 ==========
    def render_home():
        page.clean()
        page.bgcolor = ft.colors.GREY_100
        tools = [
            ("🔦 手电筒", show_flashlight),
            ("📏 水平仪", show_level),
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

# ========== 启动 ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.app(target=main, host="0.0.0.0", port=port)