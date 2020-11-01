DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS user_info;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS connections;
DROP TABLE IF EXISTS user_activity;
DROP TABLE IF EXISTS  likes;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS share;

CREATE TABLE user_info (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    data_of_birth TEXT,
    email_id TEXT,
    phone_number TEXT,
    profile_photo TEXT
);

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY,
    user_caption TEXT,
    num_followers INTEGER default 0 check(num_followers >= 0),
    num_followings INTEGER default 0 check(num_followings >= 0),
    num_posts INTEGER default 0 check(num_posts >= 0),
    FOREIGN KEY (user_id) REFERENCES user_info (user_id) ON DELETE CASCADE
);

CREATE TABLE posts (
    post_user_id INTEGER,
    post_id INTEGER,
    num_likes INTEGER default 0 check(num_likes >= 0),
    num_comments INTEGER default 0 check(num_comments >= 0),
    image_url TEXT,
    image_caption TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_user_id, post_id),
    FOREIGN KEY (post_user_id) REFERENCES user (user_id) ON DELETE CASCADE
);


CREATE TABLE connections (
    user_id_follower INTEGER,
    user_id_following INTEGER,
    mutual_connection BOOLEAN default False,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id_follower, user_id_following),
    FOREIGN KEY (user_id_follower) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id_following) REFERENCES user (user_id) ON DELETE CASCADE
);


CREATE TABLE user_activity (
    user_id INTEGER,
    post_id INTEGER,
    post_user_id INTEGER,
    type_of_activity INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id, post_user_id, type_of_activity, created),
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_user_id) REFERENCES posts (user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts (posts_id) ON DELETE CASCADE
);


CREATE TABLE likes (
    user_id INTEGER,
    post_id INTEGER,
    post_user_id INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id, post_user_id),
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_user_id) REFERENCES posts (user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts (posts_id) ON DELETE CASCADE
);

CREATE TABLE comments (
    comment_id INTEGER,
    user_id INTEGER,
    post_id INTEGER,
    post_user_id INTEGER,
    comment_text TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (comment_id, user_id, post_id, post_user_id),
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_user_id) REFERENCES posts (user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts (posts_id) ON DELETE CASCADE
);

CREATE TABLE share (
    user_id integer,
    post_id integer,
    post_user_id INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, post_id, post_user_id, created),

    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_user_id) REFERENCES posts (user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts (posts_id) ON DELETE CASCADE
);

-- For debugging purposes
INSERT INTO user_info 
(username, password, data_of_birth, email_id, phone_number)
VALUES ("admin", "admin", "11/01/2000", "a@b.c", "1234567890");

INSERT INTO user_info 
(username, password, data_of_birth, email_id, phone_number)
VALUES ("test", "test", "11/02/2000", "a@b.c", "1234567890");

INSERT INTO user_info 
(username, password, data_of_birth, email_id, phone_number)
VALUES ("user", "user", "11/03/2000", "a@b.c", "1234567890");


INSERT INTO user (user_id) VALUES (1);
INSERT INTO user (user_id) VALUES (2);
INSERT INTO user (user_id) VALUES (3);
