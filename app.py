import flet as ft
from flet import Page
from flet.web import app as flet_app  # 获取 ASGI 应用
import uvicorn
import os

def main(page: Page):
    page.title = "Flet 0.80.5 on Codespaces"
    page.vertical_alignment = "center"

    def on_click(e):
        text.value = "Hello from Flet 0.80.5! 🎉"
        page.update()

    text = ft.Text("点击按钮", size=24)
    button = ft.ElevatedButton("打招呼", on_click=on_click)

    page.add(
        ft.Column(
            [text, button],
            alignment="center",
            horizontal_alignment="center"
        )
    )

# 仅当直接运行时启动服务器（用于 Codespaces）
if __name__ == "__main__":
    # 创建 Flet ASGI 应用（传入你的 main 函数）
    flet_asgi_app = flet_app(main)

    port = int(os.environ.get("PORT", 8000))
    
    # 手动用 uvicorn 启动，并绑定 0.0.0.0
    uvicorn.run(
        flet_asgi_app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )