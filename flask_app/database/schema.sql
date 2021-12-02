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

CREATE TABLE IF NOT EXISTS PostReaction  (
	post_reaction_id INTEGER PRIMARY KEY,
	question_id INTEGER NOT NULL,
	answer_id INTEGER,
	user_id INTEGER NOT NULL,
	reaction_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Reactions  (
	reaction_id INTEGER PRIMARY KEY,
	reaction_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS AnswerVote  (
	user_id INTEGER NOT NULL,
	answer_id INTEGER NOT NULL,
	vote_id INTEGER NOT NULL,
	PRIMARY KEY (user_id, answer_id)
);

CREATE TABLE IF NOT EXISTS Vote  (
	vote_id INTEGER NOT NULL PRIMARY KEY,
	vote_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Report  (
	report_id INTEGER PRIMARY KEY,
	user_id INTEGER NOT NULL,
	question_id INTEGER NOT NULL,
	answer_id INTEGER
);

INSERT OR REPLACE INTO Vote (vote_id, vote_name) VALUES (1, 'upvote');
INSERT OR REPLACE INTO Vote (vote_id, vote_name) VALUES (2, 'downvote');

INSERT OR REPLACE INTO Reactions (reaction_id, reaction_name) VALUES (1, 'like');
INSERT OR REPLACE INTO Reactions (reaction_id, reaction_name) VALUES (2, 'dislike');
INSERT OR REPLACE INTO Reactions (reaction_id, reaction_name) VALUES (3, 'cry');
INSERT OR REPLACE INTO Reactions (reaction_id, reaction_name) VALUES (4, 'angry');
INSERT OR REPLACE INTO Reactions (reaction_id, reaction_name) VALUES (5, 'laugh');