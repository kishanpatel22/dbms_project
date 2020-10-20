DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_caption TEXT,
    num_followers INTEGER default 0, check(num_followers >= 0),
    num_followings INTEGER default 0, check(num_followings >= 0),
    num_posts INTEGER default 0, check(num_posts >= 0),
);

CREATE TABLE user_info (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT,
    data_of_birth TEXT,
    email_id TEXT,
    phone_number INTEGER,
    profile_photo TEXT,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE TABLE posts (
    post_user_id INTEGER PRIMARY KEY,
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    num_likes INTEGER default 0, check(num_likes >= 0),
    num_comments INTEGER default 0, check(num_comments >= 0),
    image_url TEXT,
    image_caption TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_user_id) REFERENCES user (user_id)
);


CREATE TABLE connections (
    user_id_follower INTEGER PRIMARY KEY,
    user_id_following INTEGER PRIMARY KEY,
    mutual_connection BOOLEAN default False,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id_follower) REFERENCES user (user_id),
    FOREIGN KEY (user_id_following) REFERENCES user (user_id)
);


CREATE TABLE user_activity (
    user_id integer primary key,
    post_id integer primary key,
    post_user_id INTEGER PRIMARY KEY,
    type_of_activity INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id),
    FOREIGN KEY (post_user_id) REFERENCES post (user_id),
    FOREIGN KEY (post_id) REFERENCES post (posts_id)
);


CREATE TABLE likes (
    user_id integer primary key,
    post_id integer primary key,
    post_user_id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id),
    FOREIGN KEY (post_user_id) REFERENCES post (user_id),
    FOREIGN KEY (post_id) REFERENCES post (posts_id)
);

CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id integer primary key,
    post_id integer primary key,
    post_user_id INTEGER PRIMARY KEY,
    comment_text TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id),
    FOREIGN KEY (post_user_id) REFERENCES post (user_id),
    FOREIGN KEY (post_id) REFERENCES post (posts_id)
);

CREATE TABLE share (
    user_id integer primary key,
    post_id integer primary key,
    post_user_id INTEGER PRIMARY KEY,
    type_of_activity INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id),
    FOREIGN KEY (post_user_id) REFERENCES post (user_id),
    FOREIGN KEY (post_id) REFERENCES post (posts_id)
);



