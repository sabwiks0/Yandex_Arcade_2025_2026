import arcade
from start_view import StartView

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Puzzle Slider"


def main():
    # Основная функция запуска игры
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    start_view.window = window
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
