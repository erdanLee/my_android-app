import flet as ft
import os

# 优先使用 YAML（更易编辑），回退到 JSON（兼容旧版）
TASKS_FILE = "tasks.yaml"  # ← 改为 .yaml

try:
    import yaml
    HAS_YAML = True
except ImportError:
    print("⚠️ PyYAML 未安装，将使用 JSON 格式（建议运行: pip install pyyaml）")
    HAS_YAML = False
    TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        # 创建易编辑的模板文件
        template_data = {
            "场地与仪式": [
                {
                    "title": "预订婚礼场地",
                    "desc": "联系3家场地并确认档期",
                    "done": False,
                    "subtasks": [
                        {"title": "查找场地A", "desc": "查看官网和评价", "done": False},
                        {"title": "对比价格", "desc": "制作Excel表格比较", "done": True}
                    ]
                }
            ],
            "婚纱与造型": [
                {
                    "title": "试婚纱",
                    "desc": "预约3家婚纱店试穿",
                    "done": False,
                    "subtasks": [
                        {"title": "查找婚纱店", "desc": "小红书推荐清单", "done": False},
                        {"title": "预约时间", "desc": "避开周末高峰", "done": False}
                    ]
                }
            ]
        }

        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            if HAS_YAML:
                # 写入带注释的 YAML 模板（更友好！）
                f.write("""# 💍 婚礼筹备任务清单（YAML 格式，支持中文，无需引号）
# 编辑说明：
# - 用缩进表示层级（2或4空格）
# - 列表项以 "- " 开头
# - done: true/false 表示完成状态
# - 可随时增删类别、任务、子任务

场地与仪式:
  - title: 预订婚礼场地
    desc: 联系3家场地并确认档期
    done: false
    subtasks:
      - title: 查找场地A
        desc: 查看官网和评价
        done: false
      - title: 对比价格
        desc: 制作Excel表格比较
        done: true

婚纱与造型:
  - title: 试婚纱
    desc: 预约3家婚纱店试穿
    done: false
    subtasks:
      - title: 查找婚纱店
        desc: 小红书推荐清单
        done: false
""")
            else:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已创建模板文件: {TASKS_FILE}")
        return template_data

    # 读取文件
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        if HAS_YAML:
            return yaml.safe_load(f) or {}
        else:
            return json.load(f)


WEDDING_PLAN = load_tasks()

# ----------------------------
# 其余代码保持不变（create_subtask_control, create_task_card 等）
# （此处省略，与上一版完全相同）
# ----------------------------

# 注意：为了完整性，我把关键函数也带上（但逻辑未变）

def create_subtask_control(subtask, on_toggle):
    checkbox = ft.Checkbox(
        value=subtask.get("done", False),
        label=subtask["title"],
        label_position="right",
        scale=0.95,
    )

    def toggle_sub(e):
        subtask["done"] = checkbox.value
        if on_toggle:
            on_toggle()

    checkbox.on_change = toggle_sub

    desc_text = None
    desc = subtask.get("desc", "").strip()
    if desc:
        desc_text = ft.Text(desc, size=11, color=ft.Colors.GREY_700, italic=True)

    content = ft.Column([checkbox], spacing=2)
    if desc_text:
        content.controls.append(
            ft.Container(desc_text, padding=ft.padding.only(left=24))
        )

    return ft.Container(content, padding=ft.padding.only(left=16, top=4, bottom=4))


expanded_state = {}

def create_task_card(task, category, task_index, on_toggle):
    key = f"{category}||{task_index}"
    if key not in expanded_state:
        expanded_state[key] = False

    main_checkbox = ft.Checkbox(
        value=task.get("done", False),
        label=task["title"],
        label_position="right",
    )

    def toggle_main(e):
        task["done"] = main_checkbox.value
        if on_toggle:
            on_toggle()

    main_checkbox.on_change = toggle_main

    def toggle_expand(e):
        expanded_state[key] = not expanded_state[key]
        subtasks_container.visible = expanded_state[key]
        expand_icon.name = ft.Icons.KEYBOARD_ARROW_DOWN if not expanded_state[key] else ft.Icons.KEYBOARD_ARROW_UP
        e.page.update()

    expand_icon = ft.Icon(
        ft.Icons.KEYBOARD_ARROW_DOWN if not expanded_state[key] else ft.Icons.KEYBOARD_ARROW_UP,
        size=18,
        color=ft.Colors.GREY_600
    )
    expand_button = ft.IconButton(
        icon=expand_icon.name,
        on_click=toggle_expand,
        width=30,
        height=30,
        style=ft.ButtonStyle(padding=0)
    )

    desc_text = None
    desc = task.get("desc", "").strip()
    if desc:
        desc_text = ft.Text(desc, size=13, color=ft.Colors.GREY_800)

    subtask_controls = []
    for sub in task.get("subtasks", []):
        subtask_controls.append(create_subtask_control(sub, on_toggle))

    subtasks_container = ft.Column(
        subtask_controls,
        spacing=4,
        visible=expanded_state[key]
    )

    header_row = ft.Row(
        [
            main_checkbox,
            ft.Container(expand_button, padding=ft.padding.only(left=4))
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    card_content_items = [header_row]
    if desc_text:
        card_content_items.append(desc_text)
    if subtask_controls:
        card_content_items.append(subtasks_container)

    card = ft.Card(
        content=ft.Container(
            content=ft.Column(card_content_items, spacing=6),
            padding=12,
        ),
        elevation=1 if not task.get("done", False) else 0,
        color=ft.Colors.GREEN_50 if task.get("done", False) else ft.Colors.WHITE,
    )
    return card


def get_all_tasks():
    all_t = []
    for tasks in WEDDING_PLAN.values():
        for t in tasks:
            all_t.append(t)
            for st in t.get("subtasks", []):
                all_t.append(st)
    return all_t


def wedding_planner(page: ft.Page):
    def refresh_ui():
        all_tasks = get_all_tasks()
        total = len(all_tasks)
        done = sum(1 for t in all_tasks if t.get("done", False))
        progress = int(done / total * 100) if total > 0 else 0

        progress_bar.value = progress / 100
        progress_text.value = f"整体进度: {done}/{total} ({progress}%)"

        if content_area.controls:
            title = content_area.controls[0]
            if isinstance(title, ft.Text) and title.value.startswith("📌 "):
                cat = title.value[2:]
                if cat in WEDDING_PLAN:
                    show_category(cat)
        page.update()

    content_area = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def show_category(category_name):
        tasks = WEDDING_PLAN[category_name]
        cards = [
            create_task_card(task, category_name, i, refresh_ui)
            for i, task in enumerate(tasks)
        ]
        content_area.controls = [
            ft.Text(f"📌 {category_name}", size=20, weight="bold"),
            ft.Divider(),
            *cards
        ]
        page.update()

    menu_items = []
    for cat in WEDDING_PLAN.keys():
        btn = ft.ElevatedButton(
            text=cat,
            on_click=lambda e, c=cat: show_category(c),
            width=180,
            height=40,
        )
        menu_items.append(btn)

    menu_column = ft.Column(menu_items, spacing=8)

    if WEDDING_PLAN:
        first_cat = next(iter(WEDDING_PLAN))
        show_category(first_cat)

    all_init = get_all_tasks()
    total_init = len(all_init)
    done_init = sum(1 for t in all_init if t.get("done", False))
    progress_init = int(done_init / total_init * 100) if total_init > 0 else 0

    progress_bar = ft.ProgressBar(value=progress_init / 100, width=300)
    progress_text = ft.Text(f"整体进度: {done_init}/{total_init} ({progress_init}%)", weight="bold")

    if page.width and page.width < 600:
        layout = ft.Column([
            ft.Container(content=menu_column, padding=10),
            ft.Divider(),
            content_area
        ], expand=True)
    else:
        layout = ft.Row([
            ft.Container(content=menu_column, width=220, padding=10),
            ft.VerticalDivider(),
            ft.Container(content=content_area, expand=True, padding=10)
        ], expand=True)

    return ft.Column([
        ft.Container(
            content=ft.Column([
                progress_text,
                progress_bar,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            bgcolor=ft.Colors.PINK_50,
        ),
        layout
    ], expand=True)


def main(page: ft.Page):
    page.title = "婚礼筹备助手"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    page.appbar = ft.AppBar(
        title=ft.Text("💍 婚礼筹备助手"),
        bgcolor="#F8BBD0"
    )

    app = wedding_planner(page)
    page.add(app)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, host="0.0.0.0", port=port)