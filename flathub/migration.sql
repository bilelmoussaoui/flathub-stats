-- SQLite
CREATE TABLE `applications` (
  `id` INTEGER PRIMARY KEY,
  `app_id` TEXT NOT NULL UNIQUE
);
CREATE TABLE `applications_history` (
  `application_id` INTEGER NOT NULL,
  `date` DATE,
  `downloads` INTEGER DEFAULT 0,
  `updates` INTEGER DEFAULT 0
);