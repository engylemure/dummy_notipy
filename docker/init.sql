CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    CONSTRAINT name_unique UNIQUE(name)
);
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    user_id integer NOT NULL REFERENCES users(id),
    viewed BOOLEAN NOT NULL DEFAULT FALSE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO users (name) VALUES ('First User - Admin');