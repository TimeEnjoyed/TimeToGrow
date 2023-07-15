CREATE TABLE IF NOT EXISTS test (
    id BIGINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS messages (
    rowid INTEGER PRIMARY KEY,
    content TEXT
);

CREATE TABLE IF NOT EXISTS plants (
    rowid INTEGER PRIMARY KEY,
    username TEXT,
    cycle INT,
    water BOOLEAN,
    sabotage BOOLEAN,
    growth_cycle INT
);