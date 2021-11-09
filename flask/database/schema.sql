CREATE TABLE IF NOT EXISTS users  (
	user_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	_username TEXT NOT NULL UNIQUE,
	_password TEXT NOT NULL
);