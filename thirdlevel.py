import arcade
import random


# Параметры экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Puzzle Slider - Level 3"

GRID_ROWS = 5  
GRID_COLS = 5  
TILE_SIZE = 80  
GRID_X = (SCREEN_WIDTH - GRID_COLS * TILE_SIZE) // 2
GRID_Y = (SCREEN_HEIGHT - GRID_ROWS * TILE_SIZE) // 2
START_MOVES = 10

# Цвета плиток должны совпадать с именами файлов в папке tiles
TILE_TYPES = ["red", "blue", "green", "yellow", "purple"]


class Tile(arcade.Sprite):
    def __init__(self, tile_type, row, col):
        self.tile_type = tile_type # номер цвета от 0-4
        self.row = row
        self.col = col

        image_name = TILE_TYPES[tile_type]
        image_path = f"resources/sprites/tiles/{image_name}.png"

        super().__init__(image_path)
        self.scale = TILE_SIZE / 100  
        self.update_position() # Располагаем плитку на экране

    def update_position(self):
        # Вычисляем координаты центра плитки
        self.center_x = GRID_X + self.col * TILE_SIZE + TILE_SIZE // 2
        self.center_y = GRID_Y + (GRID_ROWS - 1 - self.row) * TILE_SIZE + TILE_SIZE // 2

class Arrow(arcade.Sprite):
    def __init__(self, direction, x, y):
        self.direction = direction # Направление (up, down, left, right)
        image_path = f"resources/sprites/arrows/{direction}.png"

        super().__init__(image_path)
        self.scale = 0.5 
        self.center_x = x
        self.center_y = y


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        # Создаем пустую сетку 5*5
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.selected_tile = None
        self.moves_left = START_MOVES
        self.score = 0
        self.game_over = False

        self.tile_list = arcade.SpriteList()
        self.arrow_list = arcade.SpriteList()
        
        self.score_text = None
        self.moves_text = None
        self.level_text = None
        
        self.setup()

    def setup(self):
        # Начало уровня, сбрасываем все перед новой игрой
        self.tile_list.clear()
        self.arrow_list.clear()
        self.selected_tile = None
        self.moves_left = START_MOVES
        self.score = 0 
        self.game_over = False
        
        # Создаем текстовые объекты
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
            "Уровень 3",
            SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40,
            arcade.color.LIGHT_GRAY, 22,
            font_name="Arial"
        )

        # Генерируем начальное поле без готовых совпадений
        self.generate_initial_grid()
        

    def generate_initial_grid(self):
        # Генерирует начальное поле без готовых совпадений (троек, четверок, пятерок)
        max_attempts = 150  
        
        for attempt in range(max_attempts):
            # Заполняем поле случайными плитками
            for row in range(GRID_ROWS):
                for col in range(GRID_COLS):
                    # Выбираем случайный тип плитки
                    tile_type = random.randint(0, len(TILE_TYPES) - 1)
                    tile = Tile(tile_type, row, col)
                    self.grid[row][col] = tile
                    self.tile_list.append(tile)
            
            # Проверяем, есть ли готовые совпадения в начальном поле
            if not self.has_matches_in_grid():
                return  # Поле подходит, выходим из функции
            
            # Если есть совпадения, очищаем поле и пробуем снова
            self.tile_list.clear()
            self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        
        # Если не удалось сгенерировать поле без совпадений
        print(f"Предупреждение: не удалось сгенерировать поле без совпадений за {max_attempts} попыток")
        # Используем последнее сгенерированное поле и удалим готовые совпадения
        self.remove_initial_matches()

    def remove_initial_matches(self):
        # Удаляет готовые совпадения из начального поля
        # Проверяем и удаляем все совпадения до тех пор, пока они есть
        while self.has_matches_in_grid():
            # Находим все совпадения
            matches = self.find_all_matches()
            if matches:
                # Заменяем одну плитку из каждого совпадения
                for match in matches:
                    if match:
                        row, col = match[0]
                        # Меняем цвет плитки на случайный
                        new_type = random.randint(0, len(TILE_TYPES) - 1)
                        while new_type == self.grid[row][col].tile_type:
                            new_type = random.randint(0, len(TILE_TYPES) - 1)
                        
                        # Создаем новую плитку
                        self.tile_list.remove(self.grid[row][col])
                        new_tile = Tile(new_type, row, col)
                        self.grid[row][col] = new_tile
                        self.tile_list.append(new_tile)

    def find_all_matches(self):
        # Находит все совпадения в текущем поле
        matches = []
        
        # Проверяем пятерки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 4):
                tiles = [self.grid[row][col + i] for i in range(5)]
                if all(tiles) and all(t.tile_type == tiles[0].tile_type for t in tiles):
                    matches.append([(row, col + i) for i in range(5)])
        
        # Проверяем пятерки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 4):
                tiles = [self.grid[row + i][col] for i in range(5)]
                if all(tiles) and all(t.tile_type == tiles[0].tile_type for t in tiles):
                    matches.append([(row + i, col) for i in range(5)])
        
        # Проверяем четверки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 3):
                tiles = [self.grid[row][col + i] for i in range(4)]
                if all(tiles) and all(t.tile_type == tiles[0].tile_type for t in tiles):
                    matches.append([(row, col + i) for i in range(4)])
        
        # Проверяем четверки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 3):
                tiles = [self.grid[row + i][col] for i in range(4)]
                if all(tiles) and all(t.tile_type == tiles[0].tile_type for t in tiles):
                    matches.append([(row + i, col) for i in range(4)])
        
        # Проверяем тройки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 2):
                tiles = [self.grid[row][col + i] for i in range(3)]
                if all(tiles) and all(t.tile_type == tiles[0].tile_type for t in tiles):
                    matches.append([(row, col + i) for i in range(3)])
        
        # Проверяем тройки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 2):
                tiles = [self.grid[row + i][col] for i in range(3)]
                if all(tiles) and all(t.tile_type == tiles[0].tile_type for t in tiles):
                    matches.append([(row + i, col) for i in range(3)])
        
        return matches

    def has_matches_in_grid(self):
        #Проверяет, есть ли готовые совпадения в текущем состоянии поля
        # Проверяем пятерки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 4):
                t0, t1, t2, t3, t4 = (self.grid[row][col], self.grid[row][col + 1], 
                                     self.grid[row][col + 2], self.grid[row][col + 3], 
                                     self.grid[row][col + 4])
                if t0 and t1 and t2 and t3 and t4 and t0.tile_type == t1.tile_type == t2.tile_type == t3.tile_type == t4.tile_type:
                    return True

        # Проверяем пятерки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 4):
                t0, t1, t2, t3, t4 = (self.grid[row][col], self.grid[row + 1][col], 
                                     self.grid[row + 2][col], self.grid[row + 3][col], 
                                     self.grid[row + 4][col])
                if t0 and t1 and t2 and t3 and t4 and t0.tile_type == t1.tile_type == t2.tile_type == t3.tile_type == t4.tile_type:
                    return True

        # Проверяем четверки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 3):
                t0, t1, t2, t3 = (self.grid[row][col], self.grid[row][col + 1], 
                                  self.grid[row][col + 2], self.grid[row][col + 3])
                if t0 and t1 and t2 and t3 and t0.tile_type == t1.tile_type == t2.tile_type == t3.tile_type:
                    return True

        # Проверяем четверки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 3):
                t0, t1, t2, t3 = (self.grid[row][col], self.grid[row + 1][col], 
                                  self.grid[row + 2][col], self.grid[row + 3][col])
                if t0 and t1 and t2 and t3 and t0.tile_type == t1.tile_type == t2.tile_type == t3.tile_type:
                    return True

        # Проверяем тройки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 2):
                t0, t1, t2 = self.grid[row][col], self.grid[row][col + 1], self.grid[row][col + 2]
                if t0 and t1 and t2 and t0.tile_type == t1.tile_type == t2.tile_type:
                    return True

        # Проверяем тройки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 2):
                t0, t1, t2 = self.grid[row][col], self.grid[row + 1][col], self.grid[row + 2][col]
                if t0 and t1 and t2 and t0.tile_type == t1.tile_type == t2.tile_type:
                    return True

        return False

    def on_draw(self):
        self.clear(arcade.color.GRAY)

        # Рисуем границу сетки
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
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                (0, 0, 0, 180)
            )
            if self.score > 0:
                status = "ПОБЕДА!"
                color = arcade.color.PALE_GREEN
            else:
                status = "ПОРАЖЕНИЕ"
                color = arcade.color.RED
            
            status_text = arcade.Text(
                status,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                color, 48,
                anchor_x="center", font_name="Arial"
            )
            score_text = arcade.Text(
                f"Очки: {self.score}",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
                arcade.color.WHITE, 28,
                anchor_x="center", font_name="Arial"
            )
            status_text.draw()
            score_text.draw()

    def draw_ui(self):
        # Текстовые объекты
        self.score_text.value = f"Очки: {self.score}"
        if self.moves_left > 4:
            self.moves_text.color = arcade.color.PALE_GREEN
        elif self.moves_left > 2:
            self.moves_text.color = arcade.color.YELLOW
        else:
            self.moves_text.color = arcade.color.RED
        self.moves_text.value = f"Ходы: {self.moves_left}"
        
        # Рисуем текстовые объекты
        self.score_text.draw()
        self.moves_text.draw()
        self.level_text.draw()

    def _show_arrows(self):
        # Рисуем стрелки вокруг выбранной плитки
        self.arrow_list.clear() # Удаляем все стрелки, нарисованные раньше
        cx, cy = self.selected_tile.center_x, self.selected_tile.center_y
        # Поясняем, куда сдвинуть в соответствии с направлением
        arrow_offset = TILE_SIZE // 2 + 10 # Расстояние от плитки до стрелки
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

        # Проверяем, что нажали именно на стрелку и двигаем плитку
        for arrow in self.arrow_list:
            if arrow.collides_with_point((x, y)):
                self.shift_tile(arrow.direction)
                self.selected_tile = None
                self.arrow_list.clear()
                return

        # Проверяем, если кликнули по плитке, то выбираем ее и показываем стрелки
        for tile in self.tile_list:
            if tile.collides_with_point((x, y)):
                self.selected_tile = tile
                self._show_arrows()
                return

        # Если кликнули в пустое место поля, то отменяем выбор
        if self.selected_tile:
            self.selected_tile = None
            self.arrow_list.clear()

    def shift_tile(self, direction):
        if not self.selected_tile or self.moves_left <= 0:
            return

        self.moves_left -= 1
        old_row, old_col = self.selected_tile.row, self.selected_tile.col

        # С помощью циклического сдвига определяем новую позицию
        if direction == "up":
            new_row, new_col = (old_row - 1) % GRID_ROWS, old_col
        elif direction == "down":
            new_row, new_col = (old_row + 1) % GRID_ROWS, old_col
        elif direction == "left":
            new_row, new_col = old_row, (old_col - 1) % GRID_COLS
        elif direction == "right":
            new_row, new_col = old_row, (old_col + 1) % GRID_COLS

        # Меняем местами
        other_tile = self.grid[new_row][new_col]
        self.grid[old_row][old_col] = other_tile
        self.grid[new_row][new_col] = self.selected_tile

        if other_tile:
            other_tile.row, other_tile.col = old_row, old_col
            other_tile.update_position()

        self.selected_tile.row, self.selected_tile.col = new_row, new_col
        self.selected_tile.update_position()

        # Ищем совпадения
        self.check_matches()

        if self.moves_left <= 0:
            self.game_over = True

    # Функция для поиска совпадений (троек, четверок и пятерок)
    def check_matches(self):
        matches = set()
        points_to_add = 0  # Счетчик очков для добавления

        # Проверяем пятерки по горизонтали (50 баллов)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 4):
                t0, t1, t2, t3, t4 = (self.grid[row][col], self.grid[row][col + 1], 
                                     self.grid[row][col + 2], self.grid[row][col + 3], 
                                     self.grid[row][col + 4])
                if t0 and t1 and t2 and t3 and t4 and t0.tile_type == t1.tile_type == t2.tile_type == t3.tile_type == t4.tile_type:
                    matches.update([(row, col), (row, col + 1), (row, col + 2), 
                                   (row, col + 3), (row, col + 4)])
                    points_to_add += 50  

        # Проверяем пятерки по вертикали (50 баллов)
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 4):
                t0, t1, t2, t3, t4 = (self.grid[row][col], self.grid[row + 1][col], 
                                     self.grid[row + 2][col], self.grid[row + 3][col], 
                                     self.grid[row + 4][col])
                if t0 and t1 and t2 and t3 and t4 and t0.tile_type == t1.tile_type == t2.tile_type == t3.tile_type == t4.tile_type:
                    matches.update([(row, col), (row + 1, col), (row + 2, col), 
                                   (row + 3, col), (row + 4, col)])
                    points_to_add += 50  

        # Проверяем четверки по горизонтали (40 баллов)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 3):
                t0, t1, t2, t3 = (self.grid[row][col], self.grid[row][col + 1], 
                                  self.grid[row][col + 2], self.grid[row][col + 3])
                if t0 and t1 and t2 and t3 and t0.tile_type == t1.tile_type == t2.tile_type == t3.tile_type:
                    # Проверяем, что эти плитки еще не входят в пятерки
                    quad_positions = [(row, col), (row, col + 1), (row, col + 2), (row, col + 3)]
                    if not any(pos in matches for pos in quad_positions):
                        matches.update(quad_positions)
                        points_to_add += 40  

        # Проверяем четверки по вертикали (40 баллов)
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 3):
                t0, t1, t2, t3 = (self.grid[row][col], self.grid[row + 1][col], 
                                  self.grid[row + 2][col], self.grid[row + 3][col])
                if t0 and t1 and t2 and t3 and t0.tile_type == t1.tile_type == t2.tile_type == t3.tile_type:
                    # Проверяем, что эти плитки еще не входят в пятерки
                    quad_positions = [(row, col), (row + 1, col), (row + 2, col), (row + 3, col)]
                    if not any(pos in matches for pos in quad_positions):
                        matches.update(quad_positions)
                        points_to_add += 40  

        # Проверяем тройки по горизонтали (30 баллов)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 2):
                t0, t1, t2 = self.grid[row][col], self.grid[row][col + 1], self.grid[row][col + 2]
                if t0 and t1 and t2 and t0.tile_type == t1.tile_type == t2.tile_type:
                    # Проверяем, что эти плитки еще не входят в пятерки или четверки
                    triple_positions = [(row, col), (row, col + 1), (row, col + 2)]
                    if not any(pos in matches for pos in triple_positions):
                        matches.update(triple_positions)
                        points_to_add += 30  

        # Проверяем тройки по вертикали (30 баллов)
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 2):
                t0, t1, t2 = self.grid[row][col], self.grid[row + 1][col], self.grid[row + 2][col]
                if t0 and t1 and t2 and t0.tile_type == t1.tile_type == t2.tile_type:
                    # Проверяем, что эти плитки еще не входят в пятерки или четверки
                    triple_positions = [(row, col), (row + 1, col), (row + 2, col)]
                    if not any(pos in matches for pos in triple_positions):
                        matches.update(triple_positions)
                        points_to_add += 30  

        if matches:
            # Добавляем очки один раз за все совпадения
            self.score += points_to_add
            # Удаляем совпавшие плитки
            self.remove_matches(list(matches))

    # Удаляем совпавшие плитки
    def remove_matches(self, positions):
        for row, col in positions:
            tile = self.grid[row][col]
            if tile:
                self.tile_list.remove(tile)
                self.grid[row][col] = None
        
        # Заполняем пустоты и проверяем снова
        self.fill_empty_spaces()
        self.check_matches()

    # Заполняем пустоты плитками
    def fill_empty_spaces(self):
        for col in range(GRID_COLS):
            column_tiles = [self.grid[row][col] for row in range(GRID_ROWS - 1, -1, -1) if self.grid[row][col]]
            # Заполняем столбец
            for i, tile in enumerate(column_tiles):
                row = GRID_ROWS - 1 - i
                tile.row, tile.col = row, col
                tile.update_position()
                self.grid[row][col] = tile
            # Добавляем новые
            for i in range(len(column_tiles), GRID_ROWS):
                row = GRID_ROWS - 1 - i
                new_type = random.randint(0, len(TILE_TYPES) - 1)
                new_tile = Tile(new_type, row, col)
                self.grid[row][col] = new_tile
                self.tile_list.append(new_tile)

    def on_key_press(self, key, modifiers):
        # Только ESC для выхода — без перезапуска
        if key == arcade.key.ESCAPE:
            arcade.close_window()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
