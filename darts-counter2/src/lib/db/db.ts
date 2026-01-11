import Database from 'better-sqlite3';

const db = new Database('darts.db');

db.exec(`
    CREATE TABLE IF NOT EXISTS game
    (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        training_plan_id INTEGER NULL,
        player1          TEXT    NOT NULL,
        player2          TEXT,
        mode             INTEGER NOT NULL,
        double_out       INTEGER NOT NULL,
        started_at       TEXT    DEFAULT CURRENT_TIMESTAMP,
        finished         INTEGER DEFAULT 0,
        auto             INTEGER NOT NULL,
        winner           TEXT,
        FOREIGN KEY (training_plan_id) REFERENCES training_plan (id)
    );

    CREATE TABLE IF NOT EXISTS throw
    (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id         INTEGER NOT NULL,
        player_id       INTEGER NOT NULL,
        points          INTEGER NOT NULL,
        multiplier      INTEGER NOT NULL DEFAULT 1,
        x               REAL    NULL,
        y               REAL    NULL,
        target_x        REAL    NULL,
        target_y        REAL    NULL,
        distance        REAL    NULL,
        created_at      TEXT             DEFAULT CURRENT_TIMESTAMP,
        expected_target TEXT    NULL,
        is_checkout     INTEGER          DEFAULT 0,
        is_bust         INTEGER          DEFAULT 0,
        FOREIGN KEY (game_id) REFERENCES game (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS training_plan
    (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS training_plan_target
    (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER NOT NULL,
        "order" INTEGER NOT NULL,
        value   INTEGER NOT NULL,
        type    TEXT    NOT NULL,
        FOREIGN KEY (plan_id) REFERENCES training_plan (id) ON DELETE CASCADE
    );
`);

export default db;
