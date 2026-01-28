import arcade
from database import db


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class GameOverView(arcade.View):
    def __init__(self, score: int, moves_used: int, total_moves: int, level: int = 1, player_name: str = "Player"):
        super().__init__()
        self.window = None
        self.score = score
        self.moves_used = moves_used
        self.total_moves = total_moves
        self.level = level
        self.player_name = player_name
        
        # Рассчитываем процент выполнения
        max_possible_score = 200  # Примерный максимальный счет
        self.completion_percent = min(100, (score / max_possible_score) * 100) if max_possible_score > 0 else 0
        self.is_win = score > 0
        
        # Сохраняем результат в базу данных
        self.save_to_database()
        
        # Определяем кнопки в зависимости от результата
        if self.is_win:
            self.button_texts = ["ПОВТОРИТЬ УРОВЕНЬ", "СЛЕДУЮЩИЙ УРОВЕНЬ", "ГЛАВНОЕ МЕНЮ", "ВЫЙТИ"]
            self.button_y_positions = [250, 175, 100, 25]
        else:
            self.button_texts = ["ПОВТОРИТЬ УРОВЕНЬ", "ГЛАВНОЕ МЕНЮ", "ВЫЙТИ"]
            self.button_y_positions = [225, 150, 75]
    
    def save_to_database(self):
        # Сохранение результата игры в базу данных 
        try:
            db.save_game_result(
                player_name=self.player_name,
                score=self.score,
                moves_used=self.moves_used,
                total_moves=self.total_moves,
                level=self.level,
                victory=self.is_win
            )
        except Exception as e:
            # Внутренняя ошибка
            print(f"Ошибка при сохранении в БД: {e}")
    
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)
        
    def on_draw(self):
        self.clear()
        
        # Фон
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            arcade.color.GRAY
        )
        
        # Заголовок в зависимости от результата
        status_text = "ПОБЕДА!" if self.is_win else "ПОРАЖЕНИЕ"
        status_color = arcade.color.PALE_PINK if self.is_win else arcade.color.RED
        
        title = arcade.Text(
            status_text,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            status_color, 48,
            anchor_x="center", font_name="Arial", bold=True
        )
        title.draw()
        
        # Подзаголовок с уровнем
        subtitle = arcade.Text(
            f"Уровень {self.level}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
            arcade.color.LIGHT_GRAY, 24,
            anchor_x="center", font_name="Arial"
        )
        subtitle.draw()
        
        # Статистика игры
        y = SCREEN_HEIGHT - 220
        stats_items = [
            (f"ОЧКИ: {self.score}", arcade.color.WHITE),
            (f"ХОДЫ: {self.moves_used}/{self.total_moves}", arcade.color.LIGHT_BLUE),
            (f"РЕЗУЛЬТАТ: {'Успешно' if self.is_win else 'Неудачно'}", 
             arcade.color.GREEN if self.is_win else arcade.color.RED),
        ]
        
        for text, color in stats_items:
            stat_text = arcade.Text(
                text,
                SCREEN_WIDTH // 2, y,
                color, 22,
                anchor_x="center", font_name="Arial"
            )
            stat_text.draw()
            y -= 50
        
        # Кнопки
        self.draw_buttons()
    
    def draw_buttons(self):
        """Отрисовка кнопок"""
        colors = {
            "ПОВТОРИТЬ УРОВЕНЬ": arcade.color.LIGHT_BLUE,
            "СЛЕДУЮЩИЙ УРОВЕНЬ": arcade.color.LIGHT_BLUE,
            "ГЛАВНОЕ МЕНЮ": arcade.color.LIGHT_BLUE,
            "ВЫЙТИ": arcade.color.LIGHT_BLUE
        }
        
        for y_pos, text in zip(self.button_y_positions, self.button_texts):
            color = colors.get(text, arcade.color.GRAY)
            
            # Фон кнопки
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - 200,
                right=SCREEN_WIDTH // 2 + 200,
                bottom=y_pos - 19,
                top=y_pos + 25,
                color=color
            )
            
            # Рамка кнопки
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH // 2 - 200,
                right=SCREEN_WIDTH // 2 + 200,
                bottom=y_pos - 19,
                top=y_pos + 25,
                color=arcade.color.WHITE,
                border_width=2
            )
            
            # Текст кнопки
            arcade.draw_text(
                text,
                SCREEN_WIDTH // 2,
                y_pos,
                arcade.color.WHITE,
                font_size=20,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                font_name="Arial"
            )
    
    def on_mouse_press(self, x, y, button, modifiers):
        for y_pos, text in zip(self.button_y_positions, self.button_texts):
            left = SCREEN_WIDTH // 2 - 160
            right = SCREEN_WIDTH // 2 + 160
            top = y_pos + 25
            bottom = y_pos - 25
            
            if left <= x <= right and bottom <= y <= top:
                self.handle_button_click(text)
                break
    
    def handle_button_click(self, button_text):
        # Обработка кликов по кнопкам
        if button_text == "ПОВТОРИТЬ УРОВЕНЬ":
            self.restart_level()
            
        elif button_text == "СЛЕДУЮЩИЙ УРОВЕНЬ" and self.is_win:
            self.next_level()
            
        elif button_text == "ГЛАВНОЕ МЕНЮ":
            self.return_to_menu()
            
        elif button_text == "ВЫЙТИ":
            arcade.close_window()
    
    def restart_level(self):
        # Перезапуск текущего уровня
        if self.level == 1:
            from level1 import GameView as LevelView
        elif self.level == 2:
            from level2 import GameView as LevelView
        elif self.level == 3:
            from level3 import GameView as LevelView
        else:
            return
        
        level_view = LevelView()
        level_view.window = self.window
        level_view.player_name = self.player_name
        self.window.show_view(level_view)
    
    def next_level(self):
        # Переход к следующему уровню
        next_level = self.level + 1
        if next_level > 3:
            # Если это последний уровень, возвращаемся в меню
            self.return_to_menu()
            return
            
        if next_level == 2:
            from level2 import GameView as LevelView
        elif next_level == 3:
            from level3 import GameView as LevelView
        else:
            return
        
        level_view = LevelView()
        level_view.window = self.window
        level_view.player_name = self.player_name
        self.window.show_view(level_view)
    
    def return_to_menu(self):
        # Возврат в главное меню 
        from start_view import StartView
        start_view = StartView()
        start_view.window = self.window
        self.window.show_view(start_view)
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.return_to_menu()
        elif key == arcade.key.R:
            self.restart_level()
        elif key == arcade.key.N and self.is_win:
            self.next_level()
        elif key == arcade.key.M:
            self.return_to_menu()


# Функция для тестирования окна
def main():
    # Отдельный запуск GameOverView для тестирования
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Game Over Test")
    
    # Тестовые данные
    final_view = GameOverView(
        score=150,
        moves_used=8,
        total_moves=10,
        level=2,
        player_name="Player"
    )
    final_view.window = window
    window.show_view(final_view)
    arcade.run()


if __name__ == "__main__":
    main()
