import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Puzzle Slider"


class GameOverView(arcade.View):
    def __init__(self, score: int, time_used: float, moves_used: int, completion_percent: float, level: int = 1):
        super().__init__()
        self.score = score # количество очков
        self.time_used = time_used  # время в секундах
        self.moves_used = moves_used # количество использованных ходов
        self.completion_percent = completion_percent # процент выполнения
        self.level = level # номер уровня

        # Определяем статус: победа или поражение
        self.is_win = completion_percent >= 100

        # Форматируем время для отображения
        self.time_str = self._format_time(time_used)

        # Определяем кнопки в зависимости от результата
        if self.is_win:
            self.button_texts = ["ПОВТОРИТЬ УРОВЕНЬ", "СЛЕДУЮЩИЙ УРОВЕНЬ", "ГЛАВНОЕ МЕНЮ", "ВЫЙТИ"]
            self.button_y_positions = [300, 225, 150, 75]
        else:
            self.button_texts = ["ПОВТОРИТЬ УРОВЕНЬ", "ГЛАВНОЕ МЕНЮ", "ВЫЙТИ"]
            self.button_y_positions = [275, 200, 125]

    def _format_time(self, seconds: float) -> str:
        # Форматируем время в формат ММ:СС
        minutes = int(seconds) // 60
        secnds = int(seconds) % 60
        return f"{minutes:02d}:{secnds:02d}"

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.GRAY)

        # Заголовок в зависимости от результата
        status_text = "ПОБЕДА!" if self.is_win else "ПОРАЖЕНИЕ"
        status_color = arcade.color.PALE_GREEN if self.is_win else arcade.color.PALE_PINK

        arcade.draw_text(status_text,
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT - 100,
                         status_color,
                         font_size=50,
                         anchor_x="center",
                         bold=True)

        # Подзаголовок с уровнем
        arcade.draw_text(f"Уровень {self.level}",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT - 140,
                         arcade.color.LIGHT_GRAY,
                         font_size=20,
                         anchor_x="center")

        # Статистика
        stats_y_start = SCREEN_HEIGHT - 200
        stats = [
            f"Очки: {self.score}   Время: {self.time_str}",
            f"Ходы: {self.moves_used}   Выполнено: {int(self.completion_percent)}%",
        ]

        for i, stat in enumerate(stats):
            arcade.draw_text(stat,
                             SCREEN_WIDTH // 2,
                             stats_y_start - i * 40,
                             arcade.color.WHITE_SMOKE,
                             font_size=22,
                             anchor_x="center")

        # Кнопки (пока просто текст)
        for y_pos, text in zip(self.button_y_positions, self.button_texts):
            # Рисуем фон кнопки
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - 160,
                right=SCREEN_WIDTH // 2 + 160,
                bottom=y_pos - 25,
                top=y_pos + 25,
                color=arcade.color.PALE_BLUE if "ПОВТОРИТЬ" in text else
                (arcade.color.PALE_GREEN if "СЛЕДУЮЩИЙ" in text else
                 (arcade.color.LIGHT_GOLDENROD_YELLOW if "МЕНЮ" in text else arcade.color.PALE_PINK))
            )

            # Рисуем текст кнопки
            arcade.draw_text(text,
                             SCREEN_WIDTH // 2,
                             y_pos,
                             arcade.color.DARK_BLUE,
                             font_size=22,
                             anchor_x="center",
                             anchor_y="center",
                             bold=True)

    def on_mouse_press(self, x, y, button, modifiers):
        # Проверяем, попал ли клик в какую-либо кнопку
        for y_pos, text in zip(self.button_y_positions, self.button_texts):
            left = SCREEN_WIDTH // 2 - 160
            right = SCREEN_WIDTH // 2 + 160
            top = y_pos + 25
            bottom = y_pos - 25

            if left <= x <= right and bottom <= y <= top:
                print(f"Нажата кнопка: {text}")

                # Здесь будет логика переходов между экранами
                if text == "ПОВТОРИТЬ УРОВЕНЬ":
                    # Перезапуск текущего уровня
                    pass
                elif text == "СЛЕДУЮЩИЙ УРОВЕНЬ" and self.is_win:
                    # Переход к следующему уровню
                    pass
                elif text == "ГЛАВНОЕ МЕНЮ":
                    # Возврат в главное меню
                    start_view = StartView()
                    self.window.show_view(start_view)
                elif text == "ВЫЙТИ":
                    arcade.close_window()
                break



def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    final_view = GameOverView(score=150, time_used=125.5, moves_used=23, completion_percent=100.0, level=3) #с примерными даными
    window.show_view(final_view)
    arcade.run()


if __name__ == "__main__":
    main()