import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Puzzle Slider"


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        

    def on_draw(self):
        self.clear()

        arcade.set_background_color(arcade.color.GRAY)
        
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
        
        # Кнопки (просто текст пока)
        button_y_pos = [300, 225, 150, 75]
        button_texts = ["НАЧАТЬ ИГРУ", "ВЫБОР УРОВНЯ", "НАСТРОЙКИ", "ВЫЙТИ"]
        
        for y_pos, text in zip(button_y_pos, button_texts):
            # Рисуем фон кнопки
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - 150,
                right=SCREEN_WIDTH // 2 + 150,
                bottom=y_pos - 25,
                top=y_pos + 25,
                color=arcade.color.PALE_BLUE
            )
            
            
            # Рисуем текст кнопки
            arcade.draw_text(text,
                            SCREEN_WIDTH // 2,
                            y_pos,
                            arcade.color.WHITE,
                            font_size=22,
                            anchor_x="center",
                            anchor_y="center",
                            bold=True)
        
        

    def on_mouse_press(self, x, y, button, modifiers):
        # Проверяем, попал ли клик в какую-либо кнопку
        button_y_pos = [300, 225, 150, 75]
        button_texts = ["НАЧАТЬ ИГРУ", "ВЫБОР УРОВНЯ", "НАСТРОЙКИ", "ВЫЙТИ"]
        
        for y_pos, text in zip(button_y_pos, button_texts):
            left = SCREEN_WIDTH // 2 - 150
            right = SCREEN_WIDTH // 2 + 150
            top = y_pos + 25
            bottom = y_pos - 25
            
            if left <= x <= right and bottom <= y <= top:
                print(f"Нажата кнопка: {text}")
                break



def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
