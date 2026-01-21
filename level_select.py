import arcade


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class LevelSelectView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window = None
        self.selected_level = 1
        
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)
        
    def on_draw(self):
        self.clear()
        
        # Заголовок
        arcade.draw_text("ВЫБЕРИТЕ УРОВЕНЬ",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT - 100,
                         arcade.color.GOLD,
                         font_size=40,
                         anchor_x="center",
                         bold=True)
        
        # Описание уровней
        level_descriptions = [
            "Уровень 1: 3x3 поле, тройки",
            "Уровень 2: 4x4 поле, тройки и четверки", 
            "Уровень 3: 5x5 поле, тройки, четверки и пятерки"
        ]
        
        # Кнопки выбора уровня
        self.draw_level_buttons(level_descriptions)
        
        # Кнопка запуска
        self.draw_start_button()
        
        # Кнопка возврата
        self.draw_back_button()
        
    def draw_level_buttons(self, descriptions):
        # Отрисовка кнопок уровней
        button_y_pos = [400, 300, 200]
        
        for i, (y_pos, desc) in enumerate(zip(button_y_pos, descriptions), 1):
            # Определяем цвет кнопки
            if i == self.selected_level:
                button_color = arcade.color.GREEN
                text_color = arcade.color.WHITE
            else:
                button_color = arcade.color.LIGHT_GRAY
                text_color = arcade.color.BLACK
            
            # Рисуем фон кнопки
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - 200,
                right=SCREEN_WIDTH // 2 + 200,
                bottom=y_pos - 40,
                top=y_pos + 40,
                color=button_color
            )
            
            # Рисуем рамку
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH // 2 - 200,
                right=SCREEN_WIDTH // 2 + 200,
                bottom=y_pos - 40,
                top=y_pos + 40,
                color=arcade.color.DARK_GREEN,
                border_width=3
            )
            
            # Номер уровня
            arcade.draw_text(f"УРОВЕНЬ {i}",
                            SCREEN_WIDTH // 2,
                            y_pos + 10,
                            text_color,
                            font_size=24,
                            anchor_x="center",
                            anchor_y="center",
                            bold=True)
            
            # Описание
            arcade.draw_text(desc,
                            SCREEN_WIDTH // 2,
                            y_pos - 15,
                            text_color,
                            font_size=16,
                            anchor_x="center",
                            anchor_y="center")
    
    def draw_start_button(self):
        # Отрисовка кнопки запуска уровня
        # Рисуем фон кнопки
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH // 2 - 150,
            right=SCREEN_WIDTH // 2 + 150,
            bottom=100,
            top=150,
            color=arcade.color.BLUE
        )
        
        # Рисуем рамку
        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - 150,
            right=SCREEN_WIDTH // 2 + 150,
            bottom=100,
            top=150,
            color=arcade.color.DARK_BLUE,
            border_width=2
        )
        
        # Текст кнопки
        arcade.draw_text("ЗАПУСТИТЬ УРОВЕНЬ",
                        SCREEN_WIDTH // 2,
                        125,
                        arcade.color.WHITE,
                        font_size=22,
                        anchor_x="center",
                        anchor_y="center",
                        bold=True)
    
    def draw_back_button(self):
        # Отрисовка кнопки возврата
        # Рисуем фон кнопки
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH // 2 - 100,
            right=SCREEN_WIDTH // 2 + 100,
            bottom=50,
            top=100,
            color=arcade.color.RED
        )
        
        # Рисуем рамку
        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - 100,
            right=SCREEN_WIDTH // 2 + 100,
            bottom=50,
            top=100,
            color=arcade.color.DARK_RED,
            border_width=2
        )
        
        # Текст кнопки
        arcade.draw_text("НАЗАД",
                        SCREEN_WIDTH // 2,
                        75,
                        arcade.color.WHITE,
                        font_size=22,
                        anchor_x="center",
                        anchor_y="center",
                        bold=True)
    
    def on_mouse_press(self, x, y, button, modifiers):
        # Проверка кнопок уровней
        button_y_pos = [400, 300, 200]
        
        for i, y_pos in enumerate(button_y_pos, 1):
            left = SCREEN_WIDTH // 2 - 200
            right = SCREEN_WIDTH // 2 + 200
            top = y_pos + 40
            bottom = y_pos - 40
            
            if left <= x <= right and bottom <= y <= top:
                self.selected_level = i
                return
        
        # Проверка кнопки запуска уровня
        start_left = SCREEN_WIDTH // 2 - 150
        start_right = SCREEN_WIDTH // 2 + 150
        start_top = 150
        start_bottom = 100
        
        if start_left <= x <= start_right and start_bottom <= y <= start_top:
            self.start_selected_level()
            return
        
        # Проверка кнопки возврата
        back_left = SCREEN_WIDTH // 2 - 100
        back_right = SCREEN_WIDTH // 2 + 100
        back_top = 100
        back_bottom = 50
        
        if back_left <= x <= back_right and back_bottom <= y <= back_top:
            self.go_back_to_menu()
            return
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.go_back_to_menu()
            
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            self.start_selected_level()
            
        elif key in [arcade.key.UP, arcade.key.W]:
            self.selected_level = max(1, self.selected_level - 1)
            
        elif key in [arcade.key.DOWN, arcade.key.S]:
            self.selected_level = min(3, self.selected_level + 1)
            
        elif key in [arcade.key.KEY_1, arcade.key.NUM_1]:
            self.selected_level = 1
            self.start_selected_level()
            
        elif key in [arcade.key.KEY_2, arcade.key.NUM_2]:
            self.selected_level = 2
            self.start_selected_level()
            
        elif key in [arcade.key.KEY_3, arcade.key.NUM_3]:
            self.selected_level = 3
            self.start_selected_level()
    
    def start_selected_level(self):
        # Запуск выбранного уровня
        if self.selected_level == 1:
            from level1 import GameView as Level1View
            level_view = Level1View()  
        elif self.selected_level == 2:
            from level2 import GameView as Level2View
            level_view = Level2View()  
        elif self.selected_level == 3:
            from level3 import GameView as Level3View
            level_view = Level3View()  
        else:
            return
    
        level_view.window = self.window  
        level_view.player_name = "Player"
        self.window.show_view(level_view)

    def go_back_to_menu(self):
        # Возврат в главное меню
        from start_view import StartView
        start_view = StartView()  
        start_view.window = self.window  
        self.window.show_view(start_view)
