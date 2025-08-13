CREATE TABLE IF NOT EXISTS urls (
            id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            name VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES urls (id),
    status_code integer,
    h1 varchar(255),
    title varchar(255),
    description text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);