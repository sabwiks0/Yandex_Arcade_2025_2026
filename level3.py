import arcade
import random
from database import db

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Puzzle Slider - Level 3"

GRID_ROWS = 5
GRID_COLS = 5
TILE_SIZE = 80
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
        self.scale = TILE_SIZE / 100

        # Анимационные параметры
        self.target_x = 0
        self.target_y = 0
        self.animating_move = False
        self.animating_fade = False
        self.alpha = 255

        self.update_position()

    def update_position(self):
        self.center_x = GRID_X + self.col * TILE_SIZE + TILE_SIZE // 2
        self.center_y = GRID_Y + (GRID_ROWS - 1 - self.row) * TILE_SIZE + TILE_SIZE // 2
        self.target_x = self.center_x
        self.target_y = self.center_y


class Arrow(arcade.Sprite):
    def __init__(self, direction, x, y):
        self.direction = direction
        image_path = f"resources/sprites/arrows/{direction}.png"
        super().__init__(image_path)
        self.scale = 0.5
        self.center_x = x
        self.center_y = y


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.level = 3
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

        # Флаги для анимаций
        self._waiting_to_fill = False
        self._check_after_fill = False

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

        self._waiting_to_fill = False
        self._check_after_fill = False

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

        self.generate_initial_grid()



    def on_update(self, delta_time: float):
        move_speed = 400
        fade_speed = 300

        # Обновляем все плитки
        for tile in list(self.tile_list):
            if tile.animating_move:
                dx = tile.target_x - tile.center_x
                dy = tile.target_y - tile.center_y
                dist = (dx*dx + dy*dy) ** 0.5

                if dist < 1.0:
                    tile.center_x = tile.target_x
                    tile.center_y = tile.target_y
                    tile.animating_move = False
                else:
                    step = move_speed * delta_time
                    if step > dist:
                        step = dist
                    tile.center_x += dx / dist * step
                    tile.center_y += dy / dist * step

            if tile.animating_fade:
                tile.alpha -= int(fade_speed * delta_time)
                if tile.alpha <= 0:
                    tile.alpha = 0
                    tile.animating_fade = False
                    if tile in self.tile_list:
                        self.tile_list.remove(tile)
                    # Удаляем из сетки
                    for r in range(GRID_ROWS):
                        for c in range(GRID_COLS):
                            if self.grid[r][c] is tile:
                                self.grid[r][c] = None
                                break

        fading_tiles = [t for t in self.tile_list if t.animating_fade]
        if self._waiting_to_fill and not fading_tiles:
            self._waiting_to_fill = False
            self.fill_empty_spaces()
            if self._check_after_fill:
                self._check_after_fill = False
                self.check_matches()

    def save_game_result(self):
        # Сохранение результат игры
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

    def generate_initial_grid(self):
        max_attempts = 150

        for attempt in range(max_attempts):
            for row in range(GRID_ROWS):
                for col in range(GRID_COLS):
                    tile_type = random.randint(0, len(TILE_TYPES) - 1)
                    tile = Tile(tile_type, row, col)
                    self.grid[row][col] = tile
                    self.tile_list.append(tile)

            if not self.has_matches_in_grid():
                return

            self.tile_list.clear()
            self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        print(f"Предупреждение: не удалось сгенерировать поле без совпадений за {max_attempts} попыток")
        self.remove_initial_matches()

    def remove_initial_matches(self):
        while self.has_matches_in_grid():
            matches = self.find_all_matches()
            if matches:
                for match in matches:
                    if match:
                        row, col = match[0]
                        new_type = random.randint(0, len(TILE_TYPES) - 1)
                        while new_type == self.grid[row][col].tile_type:
                            new_type = random.randint(0, len(TILE_TYPES) - 1)

                        self.tile_list.remove(self.grid[row][col])
                        new_tile = Tile(new_type, row, col)
                        self.grid[row][col] = new_tile
                        self.tile_list.append(new_tile)


    def has_matches_in_grid(self):
        # Пятерки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 4):
                if all(self.grid[row][col + i] for i in range(5)):
                    tile_type = self.grid[row][col].tile_type
                    if all(self.grid[row][col + i].tile_type == tile_type for i in range(5)):
                        return True

        # Пятерки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 4):
                if all(self.grid[row + i][col] for i in range(5)):
                    tile_type = self.grid[row][col].tile_type
                    if all(self.grid[row + i][col].tile_type == tile_type for i in range(5)):
                        return True

        # Четверки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 3):
                if all(self.grid[row][col + i] for i in range(4)):
                    tile_type = self.grid[row][col].tile_type
                    if all(self.grid[row][col + i].tile_type == tile_type for i in range(4)):
                        return True

        # Четверки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 3):
                if all(self.grid[row + i][col] for i in range(4)):
                    tile_type = self.grid[row][col].tile_type
                    if all(self.grid[row + i][col].tile_type == tile_type for i in range(4)):
                        return True

        # Тройки по горизонтали
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 2):
                if all(self.grid[row][col + i] for i in range(3)):
                    tile_type = self.grid[row][col].tile_type
                    if all(self.grid[row][col + i].tile_type == tile_type for i in range(3)):
                        return True

        # Тройки по вертикали
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 2):
                if all(self.grid[row + i][col] for i in range(3)):
                    tile_type = self.grid[row][col].tile_type
                    if all(self.grid[row + i][col].tile_type == tile_type for i in range(3)):
                        return True

        return False

    def check_matches(self):
        matches = set()
        points_to_add = 0

        # Проверяем пятерки по горизонтали (50 очков)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 4):
                # Получаем все 5 плиток в ряду
                tiles = [self.grid[row][col + i] for i in range(5)]

                # Проверяем, что все плитки существуют и одного цвета
                if all(tile is not None for tile in tiles):
                    first_type = tiles[0].tile_type
                    if all(tile.tile_type == first_type for tile in tiles):
                        # Добавляем все 5 позиций в совпадения
                        for i in range(5):
                            pos = (row, col + i)
                            matches.add(pos)
                        points_to_add += 50
                        print(f"Найдена пятерка в строке {row}, столбец {col}-{col + 4}")

        # Проверяем пятерки по вертикали (50 очков)
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 4):
                tiles = [self.grid[row + i][col] for i in range(5)]

                if all(tile is not None for tile in tiles):
                    first_type = tiles[0].tile_type
                    if all(tile.tile_type == first_type for tile in tiles):
                        for i in range(5):
                            pos = (row + i, col)
                            matches.add(pos)
                        points_to_add += 50
                        print(f"Найдена пятерка в столбце {col}, строка {row}-{row + 4}")

        # Проверяем четверки по горизонтали (40 очков)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 3):
                tiles = [self.grid[row][col + i] for i in range(4)]

                if all(tile is not None for tile in tiles):
                    first_type = tiles[0].tile_type
                    if all(tile.tile_type == first_type for tile in tiles):
                        # Проверяем, что эти плитки еще не входят в пятерки
                        quad_positions = [(row, col + i) for i in range(4)]
                        if not any(pos in matches for pos in quad_positions):
                            for pos in quad_positions:
                                matches.add(pos)
                            points_to_add += 40
                            print(f"Найдена четверка в строке {row}, столбец {col}-{col + 3}")

        # Проверяем четверки по вертикали (40 очков)
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 3):
                tiles = [self.grid[row + i][col] for i in range(4)]

                if all(tile is not None for tile in tiles):
                    first_type = tiles[0].tile_type
                    if all(tile.tile_type == first_type for tile in tiles):
                        quad_positions = [(row + i, col) for i in range(4)]
                        if not any(pos in matches for pos in quad_positions):
                            for pos in quad_positions:
                                matches.add(pos)
                            points_to_add += 40
                            print(f"Найдена четверка в столбце {col}, строка {row}-{row + 3}")

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
                            print(f"Найдена тройка в строке {row}, столбец {col}-{col + 2}")

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
                            print(f"Найдена тройка в столбце {col}, строка {row}-{row + 2}")

        if matches:
            self.score += points_to_add
            print(f"Всего найдено {len(matches)} плиток в совпадениях")
            print(f"Добавлено очков: {points_to_add}")
            self.remove_matches(list(matches))
        else:
            print("Совпадений не найдено")

    def remove_matches(self, positions):
        has_fading = False
        for row, col in positions:
            tile = self.grid[row][col]
            if tile and not tile.animating_fade:
                tile.animating_fade = True
                has_fading = True

        if has_fading:
            self._waiting_to_fill = True
            self._check_after_fill = True

    def fill_empty_spaces(self):
        for col in range(GRID_COLS):
            # Собираем непустые плитки снизу вверх
            column_tiles = []
            for row in range(GRID_ROWS - 1, -1, -1):
                if self.grid[row][col]:
                    column_tiles.append(self.grid[row][col])

            # Обновляем позиции существующих
            for i, tile in enumerate(column_tiles):
                row = GRID_ROWS - 1 - i
                tile.row = row
                tile.col = col
                tile.target_x = GRID_X + col * TILE_SIZE + TILE_SIZE // 2
                tile.target_y = GRID_Y + (GRID_ROWS - 1 - row) * TILE_SIZE + TILE_SIZE // 2
                tile.animating_move = True
                self.grid[row][col] = tile

            # Создаём новые плитки сверху
            for i in range(len(column_tiles), GRID_ROWS):
                row = GRID_ROWS - 1 - i
                new_type = random.randint(0, len(TILE_TYPES) - 1)
                new_tile = Tile(new_type, row, col)
                # Позиция старта — сверху экрана
                new_tile.center_x = GRID_X + col * TILE_SIZE + TILE_SIZE // 2
                new_tile.center_y = SCREEN_HEIGHT + TILE_SIZE
                new_tile.target_x = new_tile.center_x
                new_tile.target_y = GRID_Y + (GRID_ROWS - 1 - row) * TILE_SIZE + TILE_SIZE // 2
                new_tile.animating_move = True
                self.grid[row][col] = new_tile
                self.tile_list.append(new_tile)

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
            self.draw_game_over_screen()

    def draw_ui(self):
        # Обновляем текст
        self.score_text.value = f"Очки: {self.score}"
        if self.moves_left > 5:
            self.moves_text.color = arcade.color.PALE_GREEN
        elif self.moves_left > 3:
            self.moves_text.color = arcade.color.YELLOW
        else:
            self.moves_text.color = arcade.color.RED
        self.moves_text.value = f"Ходы: {self.moves_left}"

        # Рисуем текстовые объекты
        self.score_text.draw()
        self.moves_text.draw()
        self.level_text.draw()

    def draw_game_over_screen(self):
        # Отрисовка экрана завершения игры
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 180)
        )

        if not self.showing_stats and not self.showing_high_scores:
            if not self.result_saved:
                self.save_game_result()

            # Показываем сообщение о загрузке
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

    def show_high_scores_screen(self):
        # Отображение таблицы лучших результатов
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 220)
        )

        title = arcade.Text(
            "ЛУЧШИЕ РЕЗУЛЬТАТЫ",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            arcade.color.GOLD, 36,
            anchor_x="center", font_name="Arial"
        )
        subtitle = arcade.Text(
            f"Уровень {self.level}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140,
            arcade.color.LIGHT_GRAY, 24,
            anchor_x="center", font_name="Arial"
        )
        title.draw()
        subtitle.draw()

        try:
            top_scores = db.get_top_scores(level=self.level, limit=5)

            if top_scores:
                y = SCREEN_HEIGHT - 200
                for rank, (player_name, score, moves_used, total_moves, game_date, level) in enumerate(top_scores, 1):
                    score_text = arcade.Text(
                        f"{rank}. {player_name[:10]}: {score} очков ({moves_used}/{total_moves} ходов)",
                        SCREEN_WIDTH // 2, y,
                        arcade.color.WHITE, 20,
                        anchor_x="center", font_name="Arial"
                    )
                    score_text.draw()
                    y -= 40
            else:
                no_scores = arcade.Text(
                    "Пока нет результатов для этого уровня",
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                    arcade.color.LIGHT_GRAY, 24,
                    anchor_x="center", font_name="Arial"
                )
                no_scores.draw()

        except Exception as e:
            error_text = arcade.Text(
                f"Ошибка загрузки: {str(e)[:30]}...",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                arcade.color.RED, 20,
                anchor_x="center", font_name="Arial"
            )
            error_text.draw()

        # Кнопка возврата
        back_text = arcade.Text(
            "Нажмите TAB для возврата",
            SCREEN_WIDTH // 2, 50,
            arcade.color.LIGHT_GRAY, 22,
            anchor_x="center", font_name="Arial"
        )
        back_text.draw()

    def show_statistics_screen(self):
        # Отображение статистики
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 220)
        )

        title = arcade.Text(
            "СТАТИСТИКА",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            arcade.color.CYAN, 36,
            anchor_x="center", font_name="Arial"
        )
        title.draw()

        try:
            # Статистика уровня
            level_stats = db.get_level_stats(self.level)
            if level_stats:
                total_games, wins, avg_score, max_score, min_score, avg_efficiency = level_stats
                win_rate = (wins / total_games * 100) if total_games > 0 else 0

                y = SCREEN_HEIGHT - 160
                stats_items = [
                    f"Всего игр: {int(total_games)}",
                    f"Побед: {int(wins)} ({win_rate:.1f}%)",
                    f"Средний счет: {avg_score:.1f}" if avg_score else "Средний счет: 0",
                    f"Лучший счет: {int(max_score) if max_score else 0}",
                ]

                for text in stats_items:
                    stat_text = arcade.Text(
                        text,
                        SCREEN_WIDTH // 2, y,
                        arcade.color.WHITE, 22,
                        anchor_x="center", font_name="Arial"
                    )
                    stat_text.draw()
                    y -= 40
            else:
                no_stats = arcade.Text(
                    "Нет статистики для этого уровня",
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                    arcade.color.LIGHT_GRAY, 24,
                    anchor_x="center", font_name="Arial"
                )
                no_stats.draw()

        except Exception as e:
            error_text = arcade.Text(
                f"Ошибка загрузки: {str(e)[:30]}...",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                arcade.color.RED, 20,
                anchor_x="center", font_name="Arial"
            )
            error_text.draw()

        # Кнопка возврата
        back_text = arcade.Text(
            "Нажмите S для возврата",
            SCREEN_WIDTH // 2, 50,
            arcade.color.LIGHT_GRAY, 22,
            anchor_x="center", font_name="Arial"
        )
        back_text.draw()

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

        # Проверяем, что нажали именно на стрелку
        for arrow in self.arrow_list:
            if arrow.collides_with_point((x, y)):
                self.shift_tile(arrow.direction)
                self.selected_tile = None
                self.arrow_list.clear()
                return

        # Проверяем, если кликнули по плитке
        for tile in self.tile_list:
            if tile.collides_with_point((x, y)):
                self.selected_tile = tile
                self._show_arrows()
                return

        # Если кликнули в пустое место, отменяем выбор
        if self.selected_tile:
            self.selected_tile = None
            self.arrow_list.clear()

    def shift_tile(self, direction):
        if not self.selected_tile or self.moves_left <= 0:
            return

        self.moves_left -= 1
        self.moves_used += 1
        old_row, old_col = self.selected_tile.row, self.selected_tile.col

        # Определяем новую позицию с циклическим сдвигом
        if direction == "up":
            new_row, new_col = (old_row - 1) % GRID_ROWS, old_col
        elif direction == "down":
            new_row, new_col = (old_row + 1) % GRID_ROWS, old_col
        elif direction == "left":
            new_row, new_col = old_row, (old_col - 1) % GRID_COLS
        elif direction == "right":
            new_row, new_col = old_row, (old_col + 1) % GRID_COLS

        # Меняем местами плитки
        other_tile = self.grid[new_row][new_col]
        self.grid[old_row][old_col] = other_tile
        self.grid[new_row][new_col] = self.selected_tile

        if other_tile:
            other_tile.row, other_tile.col = old_row, old_col
            other_tile.target_x = GRID_X + old_col * TILE_SIZE + TILE_SIZE // 2
            other_tile.target_y = GRID_Y + (GRID_ROWS - 1 - old_row) * TILE_SIZE + TILE_SIZE // 2
            other_tile.animating_move = True

        self.selected_tile.row, self.selected_tile.col = new_row, new_col
        self.selected_tile.target_x = GRID_X + new_col * TILE_SIZE + TILE_SIZE // 2
        self.selected_tile.target_y = GRID_Y + (GRID_ROWS - 1 - new_row) * TILE_SIZE + TILE_SIZE // 2
        self.selected_tile.animating_move = True

        # Проверяем совпадения после перемещения
        self.check_matches()

        if self.moves_left <= 0 and not self.game_over:
            self.game_over = True
            self.show_game_over()

    def on_key_press(self, key, modifiers):
        # ESC для возврата в меню
        if key == arcade.key.ESCAPE:
            if not self.game_over:
                self.return_to_menu()
            return

        # Управление на временном экране завершения
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
    # Отдельный запуск уровня (для тестирования)
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView()
    game_view.window = window
    game_view.player_name = "Player"
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
