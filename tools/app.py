import flet as ft
import random
import string
import time
import os
import re
# ----------------------------
# 密码生成器（带复制功能）
# ----------------------------
def password_generator(page: ft.Page):
    length_field = ft.TextField(value="10", width=80, text_align=ft.TextAlign.CENTER, read_only=True)
    password_output = ft.TextField(
        label="生成的密码", read_only=True, width=320,
        multiline=False, password=True, can_reveal_password=True
    )

    include_upper = ft.Checkbox(label="包含大写字母 (A-Z)", value=True)
    include_lower = ft.Checkbox(label="包含小写字母 (a-z)", value=True)
    include_digits = ft.Checkbox(label="包含数字 (0-9)", value=True)          # ✅ 新增
    include_special = ft.Checkbox(label="包含特殊字符 (!@#$%^&*)", value=False)

    mode_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="random", label="随机"),
            ft.Radio(value="word", label="词语"),
        ]),
        value="random"
    )

    WORDS = [
        # 原有保留
        "jiangsuyinghang", "beijing", "shanghai", "apple", "coffee",
        "sunshine", "password", "welcome", "fletapp", "secure",

        # 新增 40 个（共 50）
        "dragon", "forest", "ocean", "mountain", "river",
        "tiger", "eagle", "phoenix", "galaxy", "nebula",
        "quantum", "cipher", "vault", "shield", "anchor",
        "horizon", "zenith", "mirage", "echo", "pulse",
        "nova", "orbit", "comet", "aurora", "tempest",
        "crystal", "ember", "frost", "thunder", "lightning",
        "harmony", "serenity", "valor", "legacy", "momentum",
        "apex", "vertex", "nexus", "prism", "vortex"
    ]

    def adjust_length(delta):
        try:
            val = int(length_field.value) + delta
            val = max(4, min(32, val))
            length_field.value = str(val)
        except:
            length_field.value = "10"
        length_field.page.update()

    def generate_password(e):
        length = int(length_field.value)
        mode = mode_radio.value

        if mode == "word":
            base = random.choice(WORDS)
            extra_len = length - len(base)
            if extra_len <= 0:
                pwd = base[:length]
            else:
                extras = ""
                if include_upper.value:
                    extras += string.ascii_uppercase
                if include_lower.value:
                    extras += string.ascii_lowercase
                if include_digits.value:              # ✅ 使用新选项
                    extras += string.digits
                if include_special.value:
                    extras += "!@#$%^&*"
                if not extras:
                    extras = string.ascii_lowercase  # fallback
                suffix = ''.join(random.choices(extras, k=extra_len))
                pwd = base + suffix
        else:
            chars = ""
            if include_lower.value:
                chars += string.ascii_lowercase
            if include_upper.value:
                chars += string.ascii_uppercase
            if include_digits.value:                  # ✅ 使用新选项
                chars += string.digits
            if include_special.value:
                chars += "!@#$%^&*"
            if not chars:
                chars = string.ascii_lowercase + string.digits  # 默认至少有小写+数字
            pwd = ''.join(random.choices(chars, k=length))

        password_output.value = pwd
        password_output.page.update()

    def copy_password(e):
        pwd = password_output.value
        if pwd and pwd.strip():
            page.set_clipboard(pwd)
            page.show_snack_bar(
                ft.SnackBar(ft.Text("✅ 密码已复制到剪贴板！"), open=True)
            )
        else:
            page.show_snack_bar(
                ft.SnackBar(ft.Text("⚠️ 请先生成有效密码！"), open=True)
            )

    return ft.Column([
        ft.Text("🔐 密码生成器", size=24, weight="bold"),
        ft.Row([
            ft.IconButton(ft.Icons.REMOVE, on_click=lambda _: adjust_length(-1)),
            length_field,
            ft.IconButton(ft.Icons.ADD, on_click=lambda _: adjust_length(+1)),
            ft.Text("位"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        include_upper,
        include_lower,
        include_digits,  # ✅ 添加到 UI
        include_special,
        ft.Text("生成模式：", size=14),
        mode_radio,
        ft.ElevatedButton("生成密码", on_click=generate_password, width=200),
        password_output,
        ft.ElevatedButton("复制密码", icon=ft.Icons.CONTENT_COPY, on_click=copy_password, width=200),
    ], spacing=1, scroll=ft.ScrollMode.ADAPTIVE)

# ----------------------------
# 全自由拖拽 24点游戏
# ----------------------------
def twenty_four_game(page: ft.Page):
    numbers = []
    number_drags = []
    used_numbers = set()
    status_text = ft.Text("", size=18)
    next_auto = False

    # 表达式构建区的内容（纯布局）
    result_area = ft.Row(
        wrap=True,
        spacing=5,
        run_spacing=5,
    )

    # 用 Container 包裹以添加样式（padding, border 等）
    result_container = ft.Container(
        content=result_area,
        width=540,
        height=80,
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=8,
    )

    def create_number_draggables():
        nonlocal number_drags, used_numbers
        number_drags = []
        used_numbers.clear()
        for i, num in enumerate(numbers):
            container = ft.Container(
                content=ft.Text(str(num), size=18, weight="bold"),
                width=45, height=45,
                bgcolor=ft.Colors.BLUE_200,
                border_radius=8,
                alignment=ft.alignment.center,
                data={"type": "number", "value": num, "index": i}
            )
            draggable = ft.Draggable(
                group="tokens",
                content=container,
                content_when_dragging=ft.Container(
                    width=45, height=45, bgcolor=ft.Colors.GREY_300, opacity=0.5
                ),
                data={"type": "number", "value": num, "index": i}
            )
            number_drags.append(draggable)
        numbers_row.controls = number_drags
        page.update()

    def create_operator_draggables():
        operators = ['+', '-', '*', '/', '(', ')']
        op_draggables = []
        for op in operators:
            container = ft.Container(
                content=ft.Text(op, size=18),
                width=40, height=40,
                bgcolor=ft.Colors.AMBER_100,
                border_radius=6,
                alignment=ft.alignment.center,
                data={"type": "operator", "value": op}
            )
            draggable = ft.Draggable(
                group="tokens",
                content=container,
                content_feedback=ft.Container(
                    content=ft.Text(op, size=18, color=ft.Colors.WHITE),
                    width=40, height=40,
                    bgcolor=ft.Colors.AMBER,
                    border_radius=6,
                    alignment=ft.alignment.center,
                ),
                data={"type": "operator", "value": op}
            )
            op_draggables.append(draggable)
        operators_row.controls = op_draggables
        page.update()

    def on_will_accept(e):
        e.control.bgcolor = ft.Colors.GREEN_100 if e.data == "true" else ft.Colors.RED_100
        e.control.page.update()

    def on_leave(e):
        e.control.bgcolor = None
        e.control.page.update()

    def on_accept(e):
        src_control = e.page.get_control(e.src_id)
        if not src_control or not getattr(src_control, 'data', None):
            return

        token_data = src_control.data
        token_type = token_data["type"]

        if token_type == "number":
            idx = token_data["index"]
            if idx in used_numbers:
                return
            used_numbers.add(idx)
            orig_container = src_control.content
            orig_container.bgcolor = ft.Colors.GREY_300
            orig_container.opacity = 0.5
            src_control.content = orig_container

        new_content = ft.Text(str(token_data["value"]), size=18)
        bg = ft.Colors.BLUE_100 if token_type == "number" else ft.Colors.GREEN_50
        size = 45 if token_type == "number" else 40

        new_box = ft.Container(
            content=new_content,
            width=size, height=size,
            bgcolor=bg,
            border_radius=6,
            alignment=ft.alignment.center,
            data=token_data["value"],
        )
        result_area.controls.append(new_box)
        e.control.bgcolor = None
        e.control.page.update()

    result_drag_target = ft.DragTarget(
        group="tokens",
        content=result_container,
        on_will_accept=on_will_accept,
        on_accept=on_accept,
        on_leave=on_leave,
    )

    def clear_game():
        nonlocal used_numbers
        used_numbers.clear()
        result_area.controls.clear()
        status_text.value = ""
        page.update()

    def new_game():
        nonlocal numbers
        numbers = [random.randint(1, 13) for _ in range(4)]
        create_number_draggables()
        create_operator_draggables()
        clear_game()

    def evaluate_expression(tokens):
        expr = ''.join(str(t) for t in tokens)
        if not re.match(r'^[\d\+\-\*/\(\)\.]+$', expr):
            return False
        try:
            res = eval(expr)
            return abs(res - 24) < 1e-6
        except:
            return False

    def submit_answer(e):
        nonlocal next_auto
        tokens = [ctrl.data for ctrl in result_area.controls]
        num_tokens = [t for t in tokens if str(t).isdigit()]
        if len(num_tokens) != 4:
            status_text.value = "❌ 必须使用全部4个数字！"
            status_text.color = ft.Colors.RED
            page.update()
            return

        try:
            used_nums = sorted(int(x) for x in num_tokens)
            original_nums = sorted(numbers)
            if used_nums != original_nums:
                status_text.value = "❌ 使用的数字与题目不符！"
                status_text.color = ft.Colors.RED
                page.update()
                return
        except:
            status_text.value = "❌ 表达式无效！"
            status_text.color = ft.Colors.RED
            page.update()
            return

        if evaluate_expression(tokens):
            status_text.value = "🎉 正确！2秒后进入下一题..."
            status_text.color = ft.Colors.GREEN
            page.update()
            next_auto = True
            page.run_thread(lambda: auto_next())
        else:
            status_text.value = "❌ 计算结果不是24，请重试。"
            status_text.color = ft.Colors.RED
            page.update()

    def auto_next():
        time.sleep(2)
        if next_auto:
            page.call_after(new_game)

    def reset_game(e):
        nonlocal next_auto
        next_auto = False
        new_game()

    numbers_row = ft.Row(spacing=8, alignment=ft.MainAxisAlignment.CENTER)
    operators_row = ft.Row(spacing=6, wrap=True, run_spacing=6, alignment=ft.MainAxisAlignment.CENTER)

    new_game()

    return ft.Column([
        ft.Text("🔢 24点游戏", size=22, weight="bold"),
        ft.Text("拖动数字和符号到下方区域构建表达式", size=14, italic=True),
        ft.Divider(),
        ft.Text("题目数字（每个只能用一次）：", size=16),
        numbers_row,
        ft.Divider(),
        ft.Text("操作符（可重复使用）：", size=16),
        operators_row,
        ft.Divider(),
        ft.Text("表达式构建区：", size=16),
        result_drag_target,
        ft.Row([
            ft.ElevatedButton("提交", on_click=submit_answer),
            ft.OutlinedButton("重置", on_click=reset_game),
        ], alignment=ft.MainAxisAlignment.CENTER),
        status_text,
    ], spacing=12, scroll=ft.ScrollMode.ADAPTIVE)

# ----------------------------
# 主应用入口
# ----------------------------
def main(page: ft.Page):
    page.title = "24点 & 密码生成器"
    page.window_width = 440
    page.window_height = 780
    page.theme_mode = ft.ThemeMode.LIGHT

    pwd_tab = password_generator(page)
    game_tab = twenty_four_game(page)

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="密码生成器", content=pwd_tab),
            ft.Tab(text="24点游戏", content=game_tab),
        ],
        expand=True,
    )

    page.add(
        ft.AppBar(title=ft.Text("🔐 & 🔢 工具箱"), bgcolor="#E7E0EC"),
        tabs
    )

# ----------------------------
# 启动应用（兼容 Fly.io）
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, host="0.0.0.0", port=port)