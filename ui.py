import flet as ft
from main import AppData, User
from datetime import date
import asyncio
import os
import flet

print("=== DIAGNOSTICS START ===")
print(f"flet module location: {flet.__file__}")
print(f"flet dir: {dir(flet)}")
print(f"has __version__: {hasattr(flet, '__version__')}")
if hasattr(flet, "__version__"):
    print(f"__version__: {flet.__version__}")
print(f"has version module: {hasattr(flet, 'version')}")
if hasattr(flet, "version"):
    print(f"flet.version dir: {dir(flet.version)}")
print("=== DIAGNOSTICS END ===")


class CalorieApp:
    def __init__(self, page: ft.Page):
        self.page = page
        import flet.version

        print(f"Flet version in app: {flet.version.version}")
        self.page.title = "Калории"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.bgcolor = "#F5F5F5"
        self.colors = {
            "primary": "#007AFF",
            "green": "#4CAF50",
            "yellow": "#FFC107",
            "red": "#F44336",
            "background": "#F5F5F5",
            "card": "#FFFFFF",
            "text": "#000000",
            "secondary_text": "#8E8E93",
            "shadow": "grey",
        }
        # Получаем путь для хранения данных (на Android это внутренняя директория)
        storage_dir = (
            page.get_storage_dir() if hasattr(page, "get_storage_dir") else "."
        )
        self.app = AppData(storage_path=storage_dir)
        self.new_user = None
        self.nav_bar = None

        # Стартовый экран
        if not self.app.users:
            self.show_welcome()
        else:
            if self.app.current_user_index == -1 and self.app.users:
                self.app.set_current_user_by_index(0)
            self.show_main_interface()

    # --- Утилиты ---
    def _show_snack(self, message):
        snack = ft.SnackBar(content=ft.Text(message))
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    # --- Приветствие ---
    def show_welcome(self):
        self.page.overlay.clear()
        self.page.navigation_bar = None
        self.page.clean()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Добро пожаловать!", size=32, weight=ft.FontWeight.BOLD
                        ),
                        ft.Container(
                            content=ft.Text(
                                self.app.title_message,
                                size=16,
                                color=self.colors["secondary_text"],
                            ),
                            padding=10,
                        ),
                        ft.ElevatedButton(
                            "Начать худеть",
                            style=ft.ButtonStyle(
                                color={"": "white"},
                                bgcolor={"": self.colors["primary"]},
                                shape={"": ft.RoundedRectangleBorder(radius=12)},
                            ),
                            on_click=lambda e: self.show_create_user(0),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                border_radius=20,
                bgcolor=self.colors["card"],
                shadow=ft.BoxShadow(blur_radius=10, color=self.colors["shadow"]),
                expand=True,
            )
        )

    # --- Создание пользователя (пошаговое) ---
    def show_create_user(self, step_index=0):
        self.page.navigation_bar = None
        self.page.clean()
        if not self.new_user:
            self.new_user = User()

        # Определяем поле для текущего шага
        if step_index == 0:
            field = ft.TextField(label="Имя", width=300, autofocus=True)
            next_action = lambda e: self._next_step(step_index, {"name": field.value})
        elif step_index == 1:
            field = ft.Dropdown(
                label="Пол",
                options=[ft.dropdown.Option("Муж"), ft.dropdown.Option("Жен")],
                width=300,
            )
            next_action = lambda e: self._next_step(step_index, {"sex": field.value})
        elif step_index == 2:
            field = ft.TextField(
                label="Возраст",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=300,
            )
            next_action = lambda e: self._next_step(
                step_index,
                {
                    "age": (
                        int(field.value) if field.value and field.value.isdigit() else 0
                    )
                },
            )
        elif step_index == 3:
            field = ft.TextField(
                label="Рост (см)",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=300,
            )
            next_action = lambda e: self._next_step(
                step_index,
                {
                    "height": (
                        int(field.value) if field.value and field.value.isdigit() else 0
                    )
                },
            )
        elif step_index == 4:
            field = ft.TextField(
                label="Вес (кг)",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=300,
            )
            next_action = lambda e: self._next_step(
                step_index,
                {
                    "weight": (
                        int(field.value) if field.value and field.value.isdigit() else 0
                    )
                },
            )
        elif step_index == 5:
            field = ft.Dropdown(
                label="Образ жизни",
                options=[ft.dropdown.Option(l) for l in User.lifestyles],
                width=300,
            )
            next_action = lambda e: self._next_step(
                step_index, {"lifestyle": field.value}
            )
        else:
            self.finish_create_user()
            return

        titles = [
            "Как вас зовут?",
            "Ваш пол",
            "Сколько вам лет?",
            "Ваш рост (в см)",
            "Ваш вес (в кг)",
            "Образ жизни",
        ]

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            f"Шаг {step_index+1} из 6",
                            size=16,
                            color=self.colors["secondary_text"],
                        ),
                        ft.Text(titles[step_index], size=28, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=20, color="transparent"),
                        field,
                        ft.ElevatedButton(
                            "Продолжить" if step_index < 5 else "Завершить",
                            style=ft.ButtonStyle(
                                color={"": "white"},
                                bgcolor={"": self.colors["primary"]},
                                shape={"": ft.RoundedRectangleBorder(radius=12)},
                            ),
                            on_click=next_action,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                border_radius=20,
                bgcolor=self.colors["card"],
                shadow=ft.BoxShadow(blur_radius=10, color=self.colors["shadow"]),
                expand=True,
            )
        )

    def _next_step(self, step, data):
        # Валидация
        if "name" in data and not data["name"]:
            self._show_snack("Введите имя")
            return
        if "sex" in data and not data["sex"]:
            self._show_snack("Выберите пол")
            return
        if "age" in data and data["age"] <= 0:
            self._show_snack("Введите корректный возраст")
            return
        if "height" in data and (data["height"] < 100 or data["height"] > 250):
            self._show_snack("Рост должен быть от 100 до 250 см")
            return
        if "weight" in data and data["weight"] < 20:
            self._show_snack("Вес должен быть не менее 20 кг")
            return
        if "lifestyle" in data and not data["lifestyle"]:
            self._show_snack("Выберите образ жизни")
            return

        # Применяем данные
        if "name" in data:
            self.new_user.set_name(data["name"])
        if "sex" in data:
            self.new_user.set_sex(data["sex"])
        if "age" in data:
            self.new_user.set_age(data["age"])
        if "height" in data:
            self.new_user.set_height(data["height"])
        if "weight" in data:
            self.new_user.set_weight(data["weight"])
        if "lifestyle" in data:
            self.new_user.set_lifestyle(data["lifestyle"])

        if step < 5:
            self.show_create_user(step + 1)
        else:
            self.finish_create_user()

    def finish_create_user(self):
        self.new_user.calculate_recomended_calorie()
        self.app.user_id += 1
        self.new_user.id = self.app.user_id
        self.app.users.append(self.new_user)
        self.app.set_current_user_by_index(len(self.app.users) - 1)
        self.app.start_new_day()
        self.app.save()
        self.new_user = None
        self.show_main_interface()

    # --- Основной интерфейс с нижней навигацией ---
    def show_main_interface(self):
        if not self.nav_bar:
            self.nav_bar = ft.NavigationBar(
                destinations=[
                    ft.NavigationDestination(icon=ft.icons.HOME, label="Главная"),
                    ft.NavigationDestination(
                        icon=ft.icons.CALCULATE, label="Калькулятор"
                    ),
                    ft.NavigationDestination(icon=ft.icons.HISTORY, label="История"),
                    ft.NavigationDestination(
                        icon=ft.icons.PEOPLE, label="Пользователи"
                    ),
                ],
                on_change=self._on_nav_change,
                bgcolor=self.colors["card"],
                selected_index=0,
            )
        self.page.navigation_bar = self.nav_bar
        self._show_page(0)

    def _on_nav_change(self, e):
        self._show_page(e.control.selected_index)

    def _show_page(self, index):
        self.page.clean()
        if index == 0:
            self._show_home()
        elif index == 1:
            self._show_calculator()
        elif index == 2:
            self._show_history()
        elif index == 3:
            self._show_users()
        self.page.update()

    # --- Главная ---
    def _show_home(self):
        user = self.app.get_current_user()
        if not user:
            self._show_users()
            return

        remaining = self.app.get_today_remaining()
        consumed = self.app.get_today_consumed()
        goal = user.get_recomended_calorie()
        percent = remaining / goal if goal > 0 else 0

        if percent > 0.6:
            circle_color = self.colors["green"]
        elif percent > 0.3:
            circle_color = self.colors["yellow"]
        else:
            circle_color = self.colors["red"]

        circle = ft.Container(
            content=ft.Container(
                content=ft.Text(
                    str(max(0, int(remaining))),
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                ),
                alignment=ft.alignment.center,
                width=200,
                height=200,
                bgcolor=circle_color,
                border_radius=100,
                shadow=ft.BoxShadow(blur_radius=20, color=self.colors["shadow"]),
            ),
            alignment=ft.alignment.center,
        )

        buttons = ft.Row(
            [
                ft.ElevatedButton(
                    "Новый день",
                    icon=ft.icons.REFRESH,
                    style=ft.ButtonStyle(
                        color={"": self.colors["primary"]},
                        bgcolor={"": "white"},
                        shape={"": ft.RoundedRectangleBorder(radius=12)},
                    ),
                    on_click=lambda e: self._start_new_day(),
                ),
                ft.ElevatedButton(
                    "Сменить пользователя",
                    icon=ft.icons.PEOPLE,
                    style=ft.ButtonStyle(
                        color={"": self.colors["primary"]},
                        bgcolor={"": "white"},
                        shape={"": ft.RoundedRectangleBorder(radius=12)},
                    ),
                    on_click=lambda e: self._switch_to_users(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        )

        progress_text = ft.Text(
            f"Съедено: {consumed} / {int(goal)} ккал",
            size=16,
            color=self.colors["secondary_text"],
        )

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(user.get_name(), size=30, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=10, color="transparent"),
                        circle,
                        ft.Divider(height=10),
                        progress_text,
                        ft.Divider(height=20),
                        buttons,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                border_radius=20,
                bgcolor=self.colors["card"],
                shadow=ft.BoxShadow(blur_radius=10, color=self.colors["shadow"]),
                expand=True,
            )
        )

    def _start_new_day(self):
        self.app.start_new_day()
        self._show_snack("Новый день начат")
        self._show_page(0)

    def _switch_to_users(self):
        self.nav_bar.selected_index = 3
        self._show_page(3)

    # --- Калькулятор ---
    def _show_calculator(self):
        weight_field = ft.TextField(
            label="Вес порции (г)", keyboard_type=ft.KeyboardType.NUMBER, width=200
        )
        calorie_field = ft.TextField(
            label="Калорий на 100г", keyboard_type=ft.KeyboardType.NUMBER, width=200
        )
        result_text = ft.Text(
            "0 ккал", size=24, weight=ft.FontWeight.BOLD, color=self.colors["primary"]
        )

        calculate_btn = ft.ElevatedButton(
            "Рассчитать",
            style=ft.ButtonStyle(
                color={"": "white"},
                bgcolor={"": self.colors["primary"]},
            ),
            disabled=True,
        )
        add_btn = ft.ElevatedButton(
            "Добавить к дневному рациону",
            style=ft.ButtonStyle(
                color={"": self.colors["primary"]},
                bgcolor={"": "white"},
            ),
            disabled=True,
        )

        def validate():
            try:
                w = float(weight_field.value or "")
                c = float(calorie_field.value or "")
                valid = (w >= 0) and (c >= 0)
            except (ValueError, TypeError):
                valid = False
            calculate_btn.disabled = not valid
            add_btn.disabled = not valid
            self.page.update()

        weight_field.on_change = lambda e: validate()
        calorie_field.on_change = lambda e: validate()

        def calculate(e):
            try:
                w = float(weight_field.value or 0)
                c = float(calorie_field.value or 0)
                total = round(w * c / 100)
                result_text.value = f"{total} ккал"
                self.page.update()
            except:
                pass

        def add_food(e):
            try:
                w = float(weight_field.value or 0)
                c = float(calorie_field.value or 0)
                total = round(w * c / 100)
                self.app.add_calories(total)
                self._show_snack(f"Добавлено {total} ккал")
                self.nav_bar.selected_index = 0
                self._show_page(0)
            except:
                self._show_snack("Ошибка ввода")

        calculate_btn.on_click = calculate
        add_btn.on_click = add_food

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Калькулятор", size=28, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=20, color="transparent"),
                        weight_field,
                        calorie_field,
                        calculate_btn,
                        result_text,
                        add_btn,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                border_radius=20,
                bgcolor=self.colors["card"],
                shadow=ft.BoxShadow(blur_radius=10, color=self.colors["shadow"]),
                expand=True,
            )
        )

    # --- История ---
    def _show_history(self):
        user = self.app.get_current_user()
        if not user:
            self._show_users()
            return

        history = self.app.get_history()
        if not history:
            items = [ft.Text("История пуста", color=self.colors["secondary_text"])]
        else:
            items = []
            for day in history:
                items.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    day.date.strftime("%d.%m.%Y"),
                                    size=16,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Text(
                                    f"{day.consumed} / {int(day.goal)} ккал",
                                    size=16,
                                    color=self.colors["secondary_text"],
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=15,
                        margin=5,
                        border_radius=15,
                        bgcolor=self.colors["background"],
                    )
                )

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("История", size=28, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=20, color="transparent"),
                        *items,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                border_radius=20,
                bgcolor=self.colors["card"],
                shadow=ft.BoxShadow(blur_radius=10, color=self.colors["shadow"]),
                expand=True,
            )
        )

    # --- Пользователи ---
    def _show_users(self):
        users = self.app.users
        if not users:
            self._show_snack("Нет пользователей, создайте нового")
            self.show_welcome()
            return

        def on_user_click(u):
            idx = self.app.users.index(u)
            self.app.set_current_user_by_index(idx)
            self.nav_bar.selected_index = 0
            self._show_page(0)

        def confirm_delete(u):
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Подтверждение"),
                content=ft.Text(f"Удалить пользователя {u.get_name()}?"),
            )

            def close_dialog():
                dlg.open = False
                self.page.update()

            def delete_user(user):
                close_dialog()

                # Асинхронная задержка для завершения анимации закрытия диалога
                async def delayed_delete():
                    await asyncio.sleep(0.1)  # 100 мс
                    perform_delete(user)

                self.page.run_task(delayed_delete)

            def perform_delete(user):
                if user in self.app.users:
                    self.app.users.remove(user)
                    if self.app.current_user_index >= len(self.app.users):
                        self.app.current_user_index = (
                            len(self.app.users) - 1 if self.app.users else -1
                        )
                    self.app.save()

                if not self.app.users:
                    self.show_welcome()
                else:
                    self._show_page(3)

            dlg.actions = [
                ft.TextButton("Отмена", on_click=lambda e: close_dialog()),
                ft.TextButton(
                    "Удалить",
                    on_click=lambda e: delete_user(u),
                    style=ft.ButtonStyle(color=self.colors["red"]),
                ),
            ]
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

        user_cards = []
        for u in users:
            card = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.PERSON, color=self.colors["primary"], size=40),
                        ft.Column(
                            [
                                ft.Text(
                                    u.get_name(), size=20, weight=ft.FontWeight.W_500
                                ),
                                ft.Text(
                                    f"{u.get_age()} лет, {u.get_sex()}",
                                    size=14,
                                    color=self.colors["secondary_text"],
                                ),
                            ],
                            expand=True,
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=self.colors["red"],
                                    on_click=lambda e, u=u: confirm_delete(u),
                                ),
                                ft.Icon(
                                    ft.icons.CHEVRON_RIGHT,
                                    color=self.colors["secondary_text"],
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=15,
                margin=5,
                border_radius=15,
                bgcolor=self.colors["background"],
                ink=True,
                on_click=lambda e, u=u: on_user_click(u),
            )
            user_cards.append(card)

        new_user_btn = ft.ElevatedButton(
            "Новый пользователь",
            icon=ft.icons.ADD,
            style=ft.ButtonStyle(
                color={"": "white"},
                bgcolor={"": self.colors["primary"]},
                shape={"": ft.RoundedRectangleBorder(radius=12)},
            ),
            on_click=lambda e: self.show_create_user(0),
        )

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Пользователи", size=28, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=20, color="transparent"),
                        *user_cards,
                        ft.Divider(height=20),
                        new_user_btn,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                border_radius=20,
                bgcolor=self.colors["card"],
                shadow=ft.BoxShadow(blur_radius=10, color=self.colors["shadow"]),
                expand=True,
            )
        )


def main(page: ft.Page):
    CalorieApp(page)


if __name__ == "__main__":
    ft.app(target=main)
