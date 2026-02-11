# main.py
import os
import flet as ft

def main(page: ft.Page):
    page.title = "My Flet App on Fly.io"
    page.add(
        ft.Text("Hello from Flet! 🌐", size=30),
        ft.Text("Deployed on Fly.io with a short URL!", color="blue")
    )

# 关键：监听 0.0.0.0 和 $PORT（Fly.io 动态分配端口）
if __name__ == "__main__":
    ft.app(target=main, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))