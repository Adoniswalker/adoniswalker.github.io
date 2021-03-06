create table if not exists users
(
	account_id serial not null
		constraint users_pkey
			primary key,
	first_name varchar(200),
	last_name varchar(200),
	email varchar(100),
	password_hash varchar(1000)
)
;

create table  if not exists questions
(
	question_id serial not null
		constraint questions_pkey
			primary key,
	question_subject varchar(2000) not null,
	question_body varchar(2000) not null,
	date_posted timestamp default now(),
	posted_by integer
		constraint questions_users_account_id_fk
			references users
				on update set null on delete set null
)
;

create table if not exists answers
(
	answer_id serial not null
		constraint answers_pkey
			primary key,
	question_id integer not null
		constraint answers_questions_question_id_fk
			references questions
				on delete cascade,
	answeres_by integer
		constraint answers_users_account_id_fk
			references users,
	answer_date timestamp default now(),
	answer varchar(1000),
	accepted boolean default false
)
;

create table if not exists blacklisttoken
(
	id serial not null
		constraint blacklisttoken_pkey
			primary key,
	token varchar(500) not null,
	blacklisted_on timestamp default now()
)
;

create unique index if not exists blacklisttoken_token_uindex
	on blacklisttoken (token)
;
