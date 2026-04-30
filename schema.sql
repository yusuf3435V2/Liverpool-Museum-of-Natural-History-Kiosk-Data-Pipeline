-- This file should contain all code required to create & seed database tables.
DROP TABLE IF EXISTS kiosk_interaction;
DROP TABLE IF EXISTS exhibition;

CREATE TABLE exhibition (
    exhibition_id INT,
    exhibition_name TEXT,
    floor TEXT,
    department TEXT,
    start_date DATE,
    description TEXT,
    PRIMARY KEY (exhibition_id)
);

CREATE TABLE kiosk_interaction (
    kiosk_interaction_id INT GENERATED ALWAYS AS IDENTITY,
    exhibition_id INT NOT NULL,
    rating_value INT,
    type TEXT,
    at TIMESTAMP,
    PRIMARY KEY (kiosk_interaction_id),
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id)
);

