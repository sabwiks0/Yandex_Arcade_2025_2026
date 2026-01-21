import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional


def adapt_datetime(dt: datetime) -> str:
    # Адаптер для преобразования datetime в строку для SQLite
    return dt.isoformat()


def convert_datetime(text: bytes | str) -> datetime:
    # Конвертер для преобразования строки из SQLite в datetime
    return datetime.fromisoformat(text.decode() if isinstance(text, bytes) else text)


class GameDatabase:
    # Класс для управления базой данных результатов игры
    
    def __init__(self, db_path: str = "game_results.db"):
        # Инициализация базы данных
        self.db_path = db_path
        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_converter("timestamp", convert_datetime)
        self._init_database()
    
    def _init_database(self) -> None:
        #Инициализация базы данных и создание таблиц
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            # Таблица результатов игр
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL DEFAULT 'Player',
                    score INTEGER NOT NULL,
                    moves_used INTEGER NOT NULL,
                    total_moves INTEGER NOT NULL,
                    level INTEGER NOT NULL DEFAULT 1,
                    game_date TIMESTAMP NOT NULL,
                    victory BOOLEAN NOT NULL
                )
            ''')
            
            # Таблица статистики игроков
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_stats (
                    player_name TEXT PRIMARY KEY,
                    total_games INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    best_score INTEGER DEFAULT 0,
                    last_played TIMESTAMP
                )
            ''')
            
            # Индексы для быстрого поиска
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_score_level ON game_results(score DESC, level)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_date ON game_results(game_date DESC)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_player ON game_results(player_name, score DESC)
            ''')
            
            conn.commit()
    
    def save_game_result(self, 
                        player_name: str, 
                        score: int, 
                        moves_used: int, 
                        total_moves: int, 
                        level: int = 1, 
                        victory: bool = True) -> int:
        # Сохранение результата игры в базу данных
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO game_results 
                (player_name, score, moves_used, total_moves, level, game_date, victory)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (player_name, score, moves_used, total_moves, level, datetime.now(), victory))
            
            game_id = cursor.lastrowid
            
            # Обновляем статистику игрока
            cursor.execute('''
                INSERT OR REPLACE INTO player_stats 
                (player_name, total_games, total_wins, total_score, best_score, last_played)
                VALUES (
                    ?,
                    COALESCE((SELECT total_games + 1 FROM player_stats WHERE player_name = ?), 1),
                    COALESCE((SELECT total_wins + ? FROM player_stats WHERE player_name = ?), ?),
                    COALESCE((SELECT total_score + ? FROM player_stats WHERE player_name = ?), ?),
                    MAX(?, COALESCE((SELECT best_score FROM player_stats WHERE player_name = ?), 0)),
                    ?
                )
            ''', (player_name, player_name, 
                  1 if victory else 0, player_name, 1 if victory else 0,
                  score, player_name, score,
                  score, player_name,
                  datetime.now()))
            
            conn.commit()
            return game_id
    
    def get_top_scores(self, 
                      level: Optional[int] = None, 
                      limit: int = 10) -> List[Tuple]:
        # Получение лучших результатов
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            if level is not None:
                cursor.execute('''
                    SELECT player_name, score, moves_used, total_moves, game_date, level
                    FROM game_results 
                    WHERE level = ? AND victory = 1
                    ORDER BY score DESC, moves_used ASC
                    LIMIT ?
                ''', (level, limit))
            else:
                cursor.execute('''
                    SELECT player_name, score, moves_used, total_moves, game_date, level
                    FROM game_results 
                    WHERE victory = 1
                    ORDER BY score DESC, moves_used ASC
                    LIMIT ?
                ''', (limit,))
            
            return cursor.fetchall()
    
    def get_recent_games(self, 
                        player_name: Optional[str] = None, 
                        limit: int = 10) -> List[Tuple]:
        # Получение последних игр
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            if player_name:
                cursor.execute('''
                    SELECT player_name, score, moves_used, total_moves, game_date, level, victory
                    FROM game_results 
                    WHERE player_name = ?
                    ORDER BY game_date DESC
                    LIMIT ?
                ''', (player_name, limit))
            else:
                cursor.execute('''
                    SELECT player_name, score, moves_used, total_moves, game_date, level, victory
                    FROM game_results 
                    ORDER BY game_date DESC
                    LIMIT ?
                ''', (limit,))
            
            return cursor.fetchall()
    
    def get_player_stats(self, player_name: str) -> Optional[Tuple]:
        # Получение статистики игрока
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM player_stats WHERE player_name = ?
            ''', (player_name,))
            return cursor.fetchone()
    
    def get_level_stats(self, level: int) -> Tuple:
        # Получение статистики по уровню
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_games,
                    SUM(CASE WHEN victory = 1 THEN 1 ELSE 0 END) as wins,
                    AVG(score) as avg_score,
                    MAX(score) as max_score,
                    MIN(score) as min_score,
                    AVG(moves_used * 1.0 / total_moves) * 100 as avg_efficiency
                FROM game_results
                WHERE level = ?
            ''', (level,))
            return cursor.fetchone()
    
    def get_global_stats(self) -> Tuple:
        # Получение статистики по всем играм
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_games,
                    SUM(CASE WHEN victory = 1 THEN 1 ELSE 0 END) as wins,
                    AVG(score) as avg_score,
                    MAX(score) as max_score,
                    MIN(score) as min_score,
                    COUNT(DISTINCT player_name) as unique_players
                FROM game_results
            ''')
            return cursor.fetchone()
    
# Создаем экземпляр базы данных для удобства использования
db = GameDatabase()

def init_database(db_path: str = "game_results.db") -> GameDatabase:
    # Инициализация базы данных с указанным путем
    return GameDatabase(db_path)


def get_database() -> GameDatabase:
    # Получение глобального экземпляра базы данных
    return db


if __name__ == "__main__":
    # Тестирование базы данных
    test_db = GameDatabase("test.db")
    print("База данных инициализирована успешно!")
    print("Доступные методы:")
    print("save_game_result(): сохранение результата игры")
    print("get_top_scores(): получение лучших результатов")
    print("get_recent_games(): получение последних игр")
    print("get_player_stats(): статистика игрока")
    print("get_level_stats(): статистика уровня")
    print("get_global_stats(): глобальная статистика")
