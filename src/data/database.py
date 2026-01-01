"""
SQLite database for saving race data.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Tuple


class Database:
    """SQLite database manager for race data."""

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection."""
        # Create directory if needed
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def _create_tables(self):
        """Create tables if they don't exist."""
        cursor = self.conn.cursor()

        # Players table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_on DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Races table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS races (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                track TEXT NOT NULL,
                laps INTEGER NOT NULL,
                best_lap_time REAL,
                total_time REAL,
                race_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id)
            )
        ''')

        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')

        self.conn.commit()

    def get_or_create_player(self, name: str) -> int:
        """Get player ID, creating if doesn't exist."""
        cursor = self.conn.cursor()

        # Try to get existing player
        cursor.execute('SELECT id FROM players WHERE name = ?', (name,))
        row = cursor.fetchone()

        if row:
            return row['id']

        # Create new player
        cursor.execute('INSERT INTO players (name) VALUES (?)', (name,))
        self.conn.commit()
        return cursor.lastrowid

    def save_race(self, player_id: int, track: str, laps: int,
                  best_lap_time: Optional[float], total_time: Optional[float]):
        """Save a race result."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO races (player_id, track, laps, best_lap_time, total_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_id, track, laps, best_lap_time, total_time))
        self.conn.commit()

    def get_best_lap_time(self, player_id: int, track: str) -> Optional[float]:
        """Get player's best lap time for a track."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT MIN(best_lap_time) as best
            FROM races
            WHERE player_id = ? AND track = ? AND best_lap_time IS NOT NULL
        ''', (player_id, track))
        row = cursor.fetchone()
        return row['best'] if row and row['best'] else None

    def get_track_record(self, track: str) -> Optional[Tuple[str, float]]:
        """Get the track record (best lap time by any player)."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT p.name, MIN(r.best_lap_time) as best
            FROM races r
            JOIN players p ON r.player_id = p.id
            WHERE r.track = ? AND r.best_lap_time IS NOT NULL
            GROUP BY r.track
            ORDER BY best
            LIMIT 1
        ''', (track,))
        row = cursor.fetchone()
        return (row['name'], row['best']) if row and row['best'] else None

    def get_setting(self, key: str, default: str = '') -> str:
        """Get a setting value."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row['value'] if row else default

    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
        self.conn.commit()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
