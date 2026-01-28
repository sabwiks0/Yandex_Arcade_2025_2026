import arcade
from statistics_view import StatisticsView
from level_select import LevelSelectView


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window = None
        
    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        
    def on_draw(self):
        self.clear()
        
        # Заголовок игры
        arcade.draw_text("PUZZLE SLIDER", 
                         SCREEN_WIDTH // 2, 
                         SCREEN_HEIGHT - 150,
                         arcade.color.PALE_PINK, 
                         font_size=50, 
                         anchor_x="center",
                         bold=True)
        
        # Подзаголовок
        arcade.draw_text("Перемещайте элементы, чтобы собрать картинку",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT - 200,
                         arcade.color.LIGHT_GRAY,
                         font_size=18,
                         anchor_x="center")
        
        # Кнопки
        self.draw_buttons()
        
    def draw_buttons(self):
        button_y_pos = [300, 225, 150, 75]
        button_texts = ["НАЧАТЬ ИГРУ", "ВЫБОР УРОВНЯ", "СТАТИСТИКА", "ВЫЙТИ"]
        
        for i, (y_pos, text) in enumerate(zip(button_y_pos, button_texts)):
            button_color = arcade.color.PALE_BLUE if i == 0 else arcade.color.LIGHT_BLUE
            
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - 150,
                right=SCREEN_WIDTH // 2 + 150,
                bottom=y_pos - 25,
                top=y_pos + 25,
                color=button_color
            )
            
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH // 2 - 150,
                right=SCREEN_WIDTH // 2 + 150,
                bottom=y_pos - 25,
                top=y_pos + 25,
                color=arcade.color.DARK_BLUE,
                border_width=2
            )
            
            arcade.draw_text(text,
                            SCREEN_WIDTH // 2,
                            y_pos,
                            arcade.color.WHITE,
                            font_size=22,
                            anchor_x="center",
                            anchor_y="center",
                            bold=True)
    
    def on_mouse_press(self, x, y, button, modifiers):
        button_y_pos = [300, 225, 150, 75]
        button_texts = ["НАЧАТЬ ИГРУ", "ВЫБОР УРОВНЯ", "СТАТИСТИКА", "ВЫЙТИ"]
        
        for y_pos, text in zip(button_y_pos, button_texts):
            left = SCREEN_WIDTH // 2 - 150
            right = SCREEN_WIDTH // 2 + 150
            top = y_pos + 25
            bottom = y_pos - 25
            
            if left <= x <= right and bottom <= y <= top:
                self.handle_button_click(text)
                break
    
    def handle_button_click(self, button_text):
        if button_text == "НАЧАТЬ ИГРУ":
            from level_first import GameView as Level1View
            level_view = Level1View()
            level_view.window = self.window
            level_view.player_name = "Player"
            self.window.show_view(level_view)
            
        elif button_text == "ВЫБОР УРОВНЯ":
            level_select_view = LevelSelectView()
            level_select_view.window = self.window
            self.window.show_view(level_select_view)
            
        elif button_text == "СТАТИСТИКА":
            # Открываем статистику из БД
            stats_view = StatisticsView()
            stats_view.window = self.window
            stats_view.player_name = "Player"
            self.window.show_view(stats_view)
            
        elif button_text == "ВЫЙТИ":
            arcade.close_window()
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            from level1 import GameView as Level1View
            level_view = Level1View()
            level_view.window = self.window
            level_view.player_name = "Player"
            self.window.show_view(level_view)
