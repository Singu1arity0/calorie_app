import json
import os
from datetime import date


class DayRecord:
    """Один день в истории пользователя."""

    def __init__(self, date, consumed, goal):
        self.date = date  # объект date (дата начала дня)
        self.consumed = consumed  # сколько съедено (число)
        self.goal = goal  # дневная норма на этот день

    def to_dict(self):
        """Превращает объект в словарь для JSON (дата -> строка)."""
        return {
            "date": self.date.isoformat(),
            "consumed": self.consumed,
            "goal": self.goal,
        }

    @staticmethod
    def from_dict(data):
        """Создаёт объект DayRecord из словаря (строка -> date)."""
        return DayRecord(
            date.fromisoformat(data["date"]), data["consumed"], data["goal"]
        )


class User:
    lifestyles = [
        "Сидячий",
        "Легкая активность",
        "Средняя активность",
        "Высокая активность",
    ]

    def __init__(self):
        self.id = 0
        self.name = "Имя"
        self.sex = "Муж"
        self.age = 0
        self.height = 0
        self.weight = 0
        self.lifestyle = "Средняя активность"
        self.recomended_calorie = 0
        self.days = []  # список объектов DayRecord

    # Геттеры (оставим как есть)
    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_sex(self):
        return self.sex

    def get_age(self):
        return self.age

    def get_weight(self):
        return self.weight

    def get_lifestyle(self):
        return self.lifestyle

    def get_recomended_calorie(self):
        return self.recomended_calorie

    # Сеттеры (без изменений)
    def set_name(self, new_name):
        if len(new_name) > 0:
            self.name = new_name
        else:
            print("Имя не может быть пустым!")

    def set_sex(self, new_sex):
        if new_sex == "Муж" or new_sex == "Жен":
            self.sex = new_sex
        else:
            print("Такого пола нет!")

    def set_age(self, new_age):
        if new_age > 0:
            self.age = new_age
        else:
            print("Возраст не может быть меньше!!")

    def set_height(self, new_height):
        if new_height >= 100 and new_height <= 250:
            self.height = new_height
        else:
            print("Рост не может быть таким!")

    def set_weight(self, new_weight):
        if new_weight >= 20:
            self.weight = new_weight
        else:
            print("Вес не может быть таким маленьким!")

    def set_lifestyle(self, new_lifestyle):
        if new_lifestyle in User.lifestyles:
            self.lifestyle = new_lifestyle
        else:
            print("Такого образа жизни нет!")

    def calculate_recomended_calorie(self):
        """Пересчитывает рекомендованную норму на основе текущих параметров."""
        # Здесь можно сократить код, вынеся общую часть, но оставим как есть для наглядности
        if self.sex == "Муж":
            base = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
        else:
            base = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161

        if self.lifestyle == User.lifestyles[0]:
            self.recomended_calorie = base * 1.2
        elif self.lifestyle == User.lifestyles[1]:
            self.recomended_calorie = base * 1.375
        elif self.lifestyle == User.lifestyles[2]:
            self.recomended_calorie = base * 1.55
        elif self.lifestyle == User.lifestyles[3]:
            self.recomended_calorie = base * 1.725

    # --- Новые методы для работы с днями ---
    def start_new_day(self):
        """Начинает новый день: всегда создаёт новую запись с сегодняшней датой."""
        today = date.today()
        new_day = DayRecord(today, 0, self.recomended_calorie)
        self.days.append(new_day)

    def add_calories(self, amount):
        """Добавляет калории к последнему (текущему) дню."""
        if not self.days:
            print("Сначала начните новый день.")
            return
        self.days[-1].consumed += amount

    def get_today_consumed(self):
        """Возвращает количество съеденных калорий за сегодня (или 0, если дня нет)."""
        if not self.days:
            return 0
        return self.days[-1].consumed

    def get_today_remaining(self):
        """Возвращает остаток калорий на сегодня (норма - съедено)."""
        if not self.days:
            return self.recomended_calorie  # если дня нет, возвращаем полную норму
        return self.days[-1].goal - self.days[-1].consumed

    def get_history(self):
        """Возвращает список дней в обратном порядке (сначала новые)."""
        return self.days[::-1]

    # --- Сериализация ---
    def to_dict(self):
        """Превращает пользователя в словарь для JSON, включая дни."""
        return {
            "id": self.id,
            "name": self.name,
            "sex": self.sex,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "lifestyle": self.lifestyle,
            "days": [day.to_dict() for day in self.days],  # сохраняем дни
        }

    @staticmethod
    def from_dict(data):
        """Создаёт пользователя из словаря, восстанавливая дни."""
        user = User()
        user.id = data["id"]
        user.set_name(data["name"])
        user.set_sex(data["sex"])
        user.set_age(data["age"])
        user.set_height(data["height"])
        user.set_weight(data["weight"])
        user.set_lifestyle(data["lifestyle"])
        user.calculate_recomended_calorie()
        # Восстанавливаем дни, если они есть
        if "days" in data:
            user.days = [DayRecord.from_dict(d) for d in data["days"]]
        return user


class CalorieCalculator:
    """Калькулятор для одной порции (не хранит состояние между вызовами)."""

    def __init__(self):
        self.food_weight = 0
        self.calorie_food = 0
        self.calories_per_100g = 0

    def get_food_weight(self):
        return self.food_weight

    def get_calories_per_100g(self):
        return self.calories_per_100g

    def set_food_weight(self, new_food_weight):
        if new_food_weight >= 0:
            self.food_weight = new_food_weight
        else:
            print("Вес не может быть отрицательным!")

    def set_calories_per_100g(self, new_calories_per_100g):
        if new_calories_per_100g >= 0:
            self.calories_per_100g = new_calories_per_100g
        else:
            print("Калорийность не может быть отрицательной!")

    def calculate_calorie(self):
        self.calorie_food = round(self.food_weight * (self.calories_per_100g / 100))
        return self.calorie_food


class AppData:
    title_message = """Калории обновляются после полноценного сна. Во время отдыха организм восстанавливается и запускает метаболические процессы. Новая норма появляется после пробуждения.
Ваша персональная норма рассчитывается на основе указанных вами данных — пол, возраст, вес, рост и уровень активности. 
Калькулятор в приложении работает максимально прозрачно: вы вводите вес порции и калорийность блюда на 100 грамм, а калькулятор автоматически вычисляет итоговую калорийность вашей порции."""

    def __init__(self, storage_path=None):
        self.users = []
        self.user_id = 0
        self.current_user_index = -1  # -1 означает, что пользователь не выбран
        self.storage_path = storage_path or "."  # если путь не указан, используем текущую папку
        self.load()

    # --- Управление пользователями ---
    def add_user(self):
        """Создаёт нового пользователя (с консольным вводом, потом заменится на интерфейс)."""
        user = User()
        user.set_name(input("Как вас зовут? \n"))
        user.set_sex(input("Выберите пол (Муж/Жен) \n"))
        user.set_age(int(input("Укажите возраст \n")))
        user.set_height(int(input("Укажите свой рост (в см) \n")))
        user.set_weight(int(input("Укажите свой вес (в кг) \n")))
        user.set_lifestyle(
            input(
                "Выберите образ жизни (Сидячий/Легкая активность/Средняя активность/Высокая активность) \n"
            )
        )
        user.calculate_recomended_calorie()
        self.user_id += 1
        user.id = self.user_id
        self.users.append(user)
        self.save()
        # Автоматически делаем нового пользователя текущим
        self.current_user_index = len(self.users) - 1

    def set_current_user_by_index(self, index):
        """Выбирает пользователя по индексу в списке."""
        if 0 <= index < len(self.users):
            self.current_user_index = index
        else:
            print("Неверный индекс")

    def get_current_user(self):
        """Возвращает объект текущего пользователя или None."""
        if self.current_user_index >= 0:
            return self.users[self.current_user_index]
        return None

    # --- Методы для работы с днями (делегируют текущему пользователю) ---
    def start_new_day(self):
        user = self.get_current_user()
        if user:
            user.start_new_day()
            self.save()
        else:
            print("Нет выбранного пользователя")

    def add_calories(self, amount):
        user = self.get_current_user()
        if user:
            user.add_calories(amount)
            self.save()
        else:
            print("Нет выбранного пользователя")

    def get_today_consumed(self):
        user = self.get_current_user()
        return user.get_today_consumed() if user else 0

    def get_today_remaining(self):
        user = self.get_current_user()
        return user.get_today_remaining() if user else 0

    def get_history(self):
        user = self.get_current_user()
        return user.get_history() if user else []

    # --- Сохранение и загрузка ---
    def _get_filepath(self, filename="data.json"):
        """Возвращает полный путь к файлу с учётом storage_path."""
        return os.path.join(self.storage_path, filename)

    def save(self, filename="data.json"):
        data = {
            "last_user_id": self.user_id,
            "current_user_index": self.current_user_index,
            "users": [user.to_dict() for user in self.users],
        }
        filepath = self._get_filepath(filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def load(self, filename="data.json"):
        filepath = self._get_filepath(filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return

        self.user_id = data["last_user_id"]
        self.current_user_index = data.get("current_user_index", -1)
        self.users = [User.from_dict(user_dict) for user_dict in data["users"]]