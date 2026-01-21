import arcade
from database import db


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class StatisticsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window = None
        self.player_name = "Player"
        
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        
    def on_draw(self):
        self.clear()
        
        # Заголовок
        arcade.draw_text("СТАТИСТИКА ИГРЫ",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT - 80,
                         arcade.color.GOLD,
                         font_size=40,
                         anchor_x="center",
                         bold=True)
        
        try:
            # Получаем статистику из базы данных
            global_stats = db.get_global_stats()
            
            if global_stats:
                total_games, wins, avg_score, max_score, min_score, unique_players = global_stats
                win_rate = (wins / total_games * 100) if total_games > 0 else 0
                
                y = SCREEN_HEIGHT - 140
                
                # Общая статистика
                stats_items = [
                    (f"ОБЩАЯ СТАТИСТИКА:", arcade.color.YELLOW),
                    (f"Всего игр: {int(total_games)}", arcade.color.WHITE),
                    (f"Побед: {int(wins)} ({win_rate:.1f}%)", arcade.color.GREEN),
                    (f"Средний счет: {avg_score:.1f}" if avg_score else "Средний счет: 0", arcade.color.LIGHT_BLUE),
                    (f"Лучший счет: {int(max_score) if max_score else 0}", arcade.color.GOLD),
                    (f"Уникальных игроков: {unique_players}", arcade.color.ORANGE),
                ]
                
                for text, color in stats_items:
                    stat_text = arcade.Text(
                        text,
                        SCREEN_WIDTH // 2, y,
                        color, 24,
                        anchor_x="center", font_name="Arial"
                    )
                    stat_text.draw()
                    y -= 40
                
                # Статистика по уровням
                y -= 20
                level_title = arcade.Text(
                    "СТАТИСТИКА ПО УРОВНЯМ:",
                    SCREEN_WIDTH // 2, y,
                    arcade.color.YELLOW, 24,
                    anchor_x="center", font_name="Arial"
                )
                level_title.draw()
                y -= 40
                
                # Получаем статистику для каждого уровня
                for level in [1, 2, 3]:
                    level_stats = db.get_level_stats(level)
                    if level_stats:
                        level_games, level_wins, level_avg, level_max, level_min, level_efficiency = level_stats
                        level_win_rate = (level_wins / level_games * 100) if level_games > 0 else 0
                        
                        level_text = arcade.Text(
                            f"Уровень {level}: {level_games} игр, {level_win_rate:.1f}% побед, "
                            f"средний счет: {level_avg:.1f}",
                            SCREEN_WIDTH // 2, y,
                            arcade.color.LIGHT_GRAY, 20,
                            anchor_x="center", font_name="Arial"
                        )
                        level_text.draw()
                        y -= 35
                
                # Личная статистика
                player_stats = db.get_player_stats(self.player_name)
                if player_stats:
                    y -= 40
                    personal_title = arcade.Text(
                        f"ВАША СТАТИСТИКА ({self.player_name}):",
                        SCREEN_WIDTH // 2, y,
                        arcade.color.CYAN, 24,
                        anchor_x="center", font_name="Arial"
                    )
                    personal_title.draw()
                    y -= 40
                    
                    player_name, total_games, total_wins, total_score, best_score, last_played = player_stats
                    personal_win_rate = (total_wins / total_games * 100) if total_games > 0 else 0
                    
                    personal_items = [
                        (f"Игр сыграно: {total_games}", arcade.color.WHITE),
                        (f"Побед: {total_wins} ({personal_win_rate:.1f}%)", arcade.color.GREEN),
                        (f"Всего очков: {total_score}", arcade.color.LIGHT_BLUE),
                        (f"Лучший счет: {best_score}", arcade.color.GOLD),
                    ]
                    
                    for text, color in personal_items:
                        stat_text = arcade.Text(
                            text,
                            SCREEN_WIDTH // 2, y,
                            color, 22,
                            anchor_x="center", font_name="Arial"
                        )
                        stat_text.draw()
                        y -= 35
                    
                    # Дата последней игры
                    if last_played:
                        if isinstance(last_played, str):
                            date_str = last_played[:16]
                        else:
                            date_str = last_played.strftime("%Y-%m-%d %H:%M")
                        
                        date_text = arcade.Text(
                            f"Последняя игра: {date_str}",
                            SCREEN_WIDTH // 2, y,
                            arcade.color.LIGHT_GRAY, 18,
                            anchor_x="center", font_name="Arial"
                        )
                        date_text.draw()
                        y -= 30
            else:
                # Нет данных в базе
                no_data = arcade.Text(
                    "Нет данных для статистики",
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                    arcade.color.LIGHT_GRAY, 28,
                    anchor_x="center", font_name="Arial"
                )
                no_data.draw()
                
        except Exception as e:
            # Ошибка загрузки статистики
            error_text = arcade.Text(
                f"Ошибка загрузки статистики: {str(e)[:50]}...",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                arcade.color.RED, 20,
                anchor_x="center", font_name="Arial"
            )
            error_text.draw()
        
        # Кнопка возврата
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH // 2 - 100,
            right=SCREEN_WIDTH // 2 + 100,
            bottom=50,
            top=100,
            color=arcade.color.DARK_RED
        )
        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - 100,
            right=SCREEN_WIDTH // 2 + 100,
            bottom=50,
            top=100,
            color=arcade.color.RED,
            border_width=2
        )
        back_text = arcade.Text(
            "НАЗАД",
            SCREEN_WIDTH // 2, 75,
            arcade.color.WHITE, 22,
            anchor_x="center", anchor_y="center",
            bold=True, font_name="Arial"
        )
        back_text.draw()
    
    def on_mouse_press(self, x, y, button, modifiers):
        # Проверка кнопки возврата
        back_left = SCREEN_WIDTH // 2 - 100
        back_right = SCREEN_WIDTH // 2 + 100
        back_top = 100
        back_bottom = 50
        
        if back_left <= x <= back_right and back_bottom <= y <= back_top:
            self.return_to_menu()
    
    def on_key_press(self, key, modifiers):
        #Оработка нажатий клавиш
        if key == arcade.key.ESCAPE:
            self.return_to_menu()
    
    def return_to_menu(self):
        #Возврат в главное меню
        from start_view import StartView
        start_view = StartView()
        start_view.window = self.window
        self.window.show_view(start_view)
