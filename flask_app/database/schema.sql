CREATE TABLE IF NOT EXISTS User  (
	user_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	_username TEXT NOT NULL UNIQUE,
	_password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Reply  (
	reply_id INTEGER PRIMARY KEY,
	answer_id INTEGER,
	question_id INTEGER,
	user_id INTEGER NOT NULL,
	contents TEXT,
	date_created DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS Answer  (
	answer_id INTEGER PRIMARY KEY,
	question_id INTEGER,
	user_id INTEGER NOT NULL,
	contents TEXT,
	date_created DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS Question  (
	question_id INTEGER PRIMARY KEY,
	user_id INTEGER NOT NULL,
	title TEXT,
	contents TEXT,
	date_created DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS QuestionReaction  (
	question_id INTEGER PRIMARY KEY,
	user_id INTEGER NOT NULL,
	reaction_id INTEGER
);

CREATE TABLE IF NOT EXISTS Reactions  (
	reaction_id INTEGER PRIMARY KEY,
	reaction_name INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS AnswerVote  (
	answer_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	vote_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Vote  (
	vote_id INTEGER NOT NULL,
	vote_name TEXT NOT NULL
);
