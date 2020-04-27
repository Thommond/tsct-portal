
-- TSCT Portal Database Schema
--
-- This file will drop and recreate all tables necessary for
-- the application and can be run with the `flask init-db`
-- command in your terminal.

-- Drop existing tables
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS majors CASCADE;
DROP TABLE IF EXISTS assignments CASCADE;
DROP TABLE IF EXISTS rosters CASCADE;
DROP TABLE IF EXISTS submissions CASCADE;

-- Major
CREATE TABLE majors (
    id bigserial PRIMARY KEY,
    name text NOT NULL
);

-- Users
CREATE TABLE users (
    id bigserial PRIMARY KEY,
    name text NOT NULL,
    major_id bigint REFERENCES majors (id),
    email text UNIQUE NOT NULL,
    password text NOT NULL,
    role varchar(7) NOT NULL CHECK (role IN ('teacher', 'student'))
);

--Courses
CREATE TABLE courses (
 course_num bigserial PRIMARY KEY,
 course_title text NOT NULL,
 description text,
 credits integer NOT NULL,
 teacher_id bigint REFERENCES users (id),
 major_id bigint REFERENCES majors (id)
);

--Sessions
CREATE TABLE sessions (
id bigserial PRIMARY KEY,
times text NOT NULL,
session_name text NOT NULL,
room_number text NOT NULL,
location text NOT NULL,
course_id bigint REFERENCES courses (course_num)
);

--Assignments
CREATE TABLE assignments (
  id bigserial PRIMARY KEY,
  sessions_id bigint REFERENCES sessions (id),
  assign_name text NOT NULL,
  description text NOT NULL,
  points integer NOT NULL,
  due_time timestamp NOT NULL
);

-- Rosters
CREATE TABLE rosters (
id bigserial PRIMARY KEY,
user_id bigint REFERENCES users (id),
session_id bigint REFERENCES sessions (id)
);

--Submissions
CREATE TABLE submissions (
  id bigserial PRIMARY KEY,
  assignment_id bigint REFERENCES assignments (id),
  student_id bigint REFERENCES users (id),
  grade integer,
  feedback text
);
