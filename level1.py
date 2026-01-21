import arcade
import random
from database import db


# Параметры экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Puzzle Slider - Level 1"

GRID_ROWS = 3
GRID_COLS = 3
TILE_SIZE = 130
GRID_X = (SCREEN_WIDTH - GRID_COLS * TILE_SIZE) // 2
GRID_Y = (SCREEN_HEIGHT - GRID_ROWS * TILE_SIZE) // 2
START_MOVES = 10

TILE_TYPES = ["red", "blue", "green", "yellow", "purple"]


class Tile(arcade.Sprite):
    def __init__(self, tile_type, row, col):
        self.tile_type = tile_type
        self.row = row
        self.col = col
        image_name = TILE_TYPES[tile_type]
        image_path = f"resources/sprites/tiles/{image_name}.png"
        super().__init__(image_path)
        self.scale = TILE_SIZE // 55
        self.update_position()

    def update_position(self):
        self.center_x = GRID_X + self.col * TILE_SIZE + TILE_SIZE // 2
        self.center_y = GRID_Y + (GRID_ROWS - 1 - self.row) * TILE_SIZE + TILE_SIZE // 2


class Arrow(arcade.Sprite):
    def __init__(self, direction, x, y):
        self.direction = direction
        image_path = f"resources/sprites/arrows/{direction}.png"
        super().__init__(image_path)
        self.scale = 0.6
        self.center_x = x
        self.center_y = y


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.window = None
        self.player_name = "Player"
        
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.selected_tile = None
        self.moves_left = START_MOVES
        self.moves_used = 0
        self.score = 0
        self.game_over = False
        self.showing_stats = False
        self.showing_high_scores = False
        self.result_saved = False

        self.tile_list = arcade.SpriteList()
        self.arrow_list = arcade.SpriteList()
        
        self.score_text = None
        self.moves_text = None
        self.level_text = None
        
        self.setup()

    def setup(self):
        self.tile_list.clear()
        self.arrow_list.clear()
        self.selected_tile = None
        self.moves_left = START_MOVES
        self.moves_used = 0
        self.score = 0
        self.game_over = False
        self.showing_stats = False
        self.showing_high_scores = False
        self.result_saved = False

        self.score_text = arcade.Text(
            f"Очки: {self.score}",
            20, SCREEN_HEIGHT - 40,
            arcade.color.WHITE, 22,
            font_name="Arial"
        )
        self.moves_text = arcade.Text(
            f"Ходы: {self.moves_left}",
            20, SCREEN_HEIGHT - 75,
            arcade.color.PALE_GREEN, 22,
            font_name="Arial"
        )
        self.level_text = arcade.Text(
            "Уровень 1",
            SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40,
            arcade.color.LIGHT_GRAY, 22,
            font_name="Arial"
        )

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                tile_type = random.randint(0, len(TILE_TYPES) - 1)
                tile = Tile(tile_type, row, col)
                self.grid[row][col] = tile
                self.tile_list.append(tile)

        self.check_matches()

    def save_game_result(self):
        if self.result_saved:
            return
        
        victory = self.score > 0
        total_moves = START_MOVES
        moves_used = total_moves - self.moves_left
        
        try:
            game_id = db.save_game_result(
                player_name=self.player_name,
                score=self.score,
                moves_used=moves_used,
                total_moves=total_moves,
                level=self.level,
                victory=victory
            )
            self.result_saved = True
            print(f"Результат сохранен (ID: {game_id})")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def show_game_over(self):
        if self.result_saved:
            return
        
        total_moves = START_MOVES
        moves_used = total_moves - self.moves_left
        
        try:
            from game_over_view import GameOverView
            final_view = GameOverView(
                score=self.score,
                moves_used=moves_used,
                total_moves=total_moves,
                level=self.level,
                player_name=self.player_name
            )
            final_view.window = self.window
            self.window.show_view(final_view)
        except ImportError as e:
            print(f"Ошибка импорта GameOverView: {e}")
            self.save_game_result()

    def return_to_menu(self):
        try:
            from start_view import StartView
            start_view = StartView()
            start_view.window = self.window
            self.window.show_view(start_view)
        except ImportError:
            arcade.close_window()

    def on_draw(self):
        self.clear(arcade.color.GRAY)

        left = GRID_X - 5
        right = GRID_X + GRID_COLS * TILE_SIZE + 5
        bottom = GRID_Y - 5
        top = GRID_Y + GRID_ROWS * TILE_SIZE + 5
        arcade.draw_line(left, bottom, right, bottom, arcade.color.WHITE_SMOKE, 3)
        arcade.draw_line(left, top, right, top, arcade.color.WHITE_SMOKE, 3)
        arcade.draw_line(left, bottom, left, top, arcade.color.WHITE_SMOKE, 3)
        arcade.draw_line(right, bottom, right, top, arcade.color.WHITE_SMOKE, 3)

        self.tile_list.draw()
        self.arrow_list.draw()
        self.draw_ui()

        if self.game_over:
            self.draw_game_over_screen()

    def draw_ui(self):
        self.score_text.value = f"Очки: {self.score}"
        if self.moves_left > 3:
            self.moves_text.color = arcade.color.PALE_GREEN
        else:
            self.moves_text.color = arcade.color.RED
        self.moves_text.value = f"Ходы: {self.moves_left}"
        
        self.score_text.draw()
        self.moves_text.draw()
        self.level_text.draw()

    def draw_game_over_screen(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 180)
        )
        
        if not self.showing_stats and not self.showing_high_scores:
            if not self.result_saved:
                self.save_game_result()
            
            loading_text = arcade.Text(
                "Загрузка результатов...",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                arcade.color.WHITE, 28,
                anchor_x="center", font_name="Arial"
            )
            loading_text.draw()
        
        elif self.showing_high_scores:
            self.show_high_scores_screen()
        
        elif self.showing_stats:
            self.show_statistics_screen()

    def _show_arrows(self):
        self.arrow_list.clear()
        cx, cy = self.selected_tile.center_x, self.selected_tile.center_y
        arrow_offset = TILE_SIZE // 2 + 10
        offsets = {
            "up": (0, arrow_offset),
            "down": (0, -arrow_offset),
            "left": (-arrow_offset, 0),
            "right": (arrow_offset, 0)
        }
        for direction, (dx, dy) in offsets.items():
            self.arrow_list.append(Arrow(direction, cx + dx, cy + dy))

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            return

        for arrow in self.arrow_list:
            if arrow.collides_with_point((x, y)):
                self.shift_tile(arrow.direction)
                self.selected_tile = None
                self.arrow_list.clear()
                return

        for tile in self.tile_list:
            if tile.collides_with_point((x, y)):
                self.selected_tile = tile
                self._show_arrows()
                return

        if self.selected_tile:
            self.selected_tile = None
            self.arrow_list.clear()

    def shift_tile(self, direction):
        if not self.selected_tile or self.moves_left <= 0:
            return

        self.moves_left -= 1
        self.moves_used += 1
        old_row, old_col = self.selected_tile.row, self.selected_tile.col

        if direction == "up":
            new_row, new_col = (old_row - 1) % GRID_ROWS, old_col
        elif direction == "down":
            new_row, new_col = (old_row + 1) % GRID_ROWS, old_col
        elif direction == "left":
            new_row, new_col = old_row, (old_col - 1) % GRID_COLS
        elif direction == "right":
            new_row, new_col = old_row, (old_col + 1) % GRID_COLS

        other_tile = self.grid[new_row][new_col]
        self.grid[old_row][old_col] = other_tile
        self.grid[new_row][new_col] = self.selected_tile

        if other_tile:
            other_tile.row, other_tile.col = old_row, old_col
            other_tile.update_position()

        self.selected_tile.row, self.selected_tile.col = new_row, new_col
        self.selected_tile.update_position()

        self.check_matches()

        if self.moves_left <= 0 and not self.game_over:
            self.game_over = True
            self.show_game_over()

    def check_matches(self):
        matches = set()
        points_to_add = 0

        # Проверяем тройки по горизонтали (30 очков)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 2):
                tiles = [self.grid[row][col + i] for i in range(3)]
                
                if all(tile is not None for tile in tiles):
                    first_type = tiles[0].tile_type
                    if all(tile.tile_type == first_type for tile in tiles):
                        triple_positions = [(row, col + i) for i in range(3)]
                        # Проверяем, что эти плитки не входят в четверки или пятерки
                        if not any(pos in matches for pos in triple_positions):
                            for pos in triple_positions:
                                matches.add(pos)
                            points_to_add += 30
                            print(f"Найдена тройка в строке {row}, столбец {col}-{col+2}")
        
        # Проверяем тройки по вертикали (30 очков)
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 2):
                tiles = [self.grid[row + i][col] for i in range(3)]
                
                if all(tile is not None for tile in tiles):
                    first_type = tiles[0].tile_type
                    if all(tile.tile_type == first_type for tile in tiles):
                        triple_positions = [(row + i, col) for i in range(3)]
                        if not any(pos in matches for pos in triple_positions):
                            for pos in triple_positions:
                                matches.add(pos)
                            points_to_add += 30
                            print(f"Найдена тройка в столбце {col}, строка {row}-{row+2}")
        
        if matches:
            self.score += points_to_add
            print(f"Всего найдено {len(matches)} плиток в совпадениях")
            print(f"Добавлено очков: {points_to_add}")
            self.remove_matches(list(matches))
        else:
            print("Совпадений не найдено")

    def remove_matches(self, positions):
        for row, col in positions:
            tile = self.grid[row][col]
            if tile:
                self.tile_list.remove(tile)
                self.grid[row][col] = None
        self.fill_empty_spaces()
        self.check_matches()  # Проверяем новые совпадения после заполнения

    def fill_empty_spaces(self):
        for col in range(GRID_COLS):
            column_tiles = [self.grid[row][col] for row in range(GRID_ROWS - 1, -1, -1) if self.grid[row][col]]
            for i, tile in enumerate(column_tiles):
                row = GRID_ROWS - 1 - i
                tile.row, tile.col = row, col
                tile.update_position()
                self.grid[row][col] = tile
            for i in range(len(column_tiles), GRID_ROWS):
                row = GRID_ROWS - 1 - i
                new_type = random.randint(0, len(TILE_TYPES) - 1)
                new_tile = Tile(new_type, row, col)
                self.grid[row][col] = new_tile
                self.tile_list.append(new_tile)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if not self.game_over:
                self.return_to_menu()
            return
        
        if self.game_over and not self.result_saved:
            if key == arcade.key.R:
                self.setup()
            
            elif key == arcade.key.TAB:
                self.showing_high_scores = not self.showing_high_scores
                self.showing_stats = False if self.showing_high_scores else self.showing_stats
            
            elif key == arcade.key.S:
                self.showing_stats = not self.showing_stats
                self.showing_high_scores = False if self.showing_stats else self.showing_high_scores


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView()
    game_view.window = window
    game_view.player_name = "Player"
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
