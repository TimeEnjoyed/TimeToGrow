CREATE TABLE IF NOT EXISTS test (
    id BIGINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS messages (
    rowid INTEGER PRIMARY KEY,
    content TEXT
);

CREATE TABLE IF NOT EXISTS plants (
    rowid INTEGER PRIMARY KEY,
    time TIME,
    username TEXT,
    state INT,
    wilt BOOLEAN,
    message TEXT
);