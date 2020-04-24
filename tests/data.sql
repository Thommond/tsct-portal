-- Mock Data For Tests

INSERT INTO majors (name)
VALUES  ('CSET'),
        ('WELD'),
        ('CNSA'),
        ('ENG');

INSERT INTO users (name, major_id, email, password, role)
VALUES ('zach fedor', 1,'teacher@stevenscollege.edu', 'pbkdf2:sha256:150000$ZZ1nIlm2$c02fda91e5b9651a67fc7cbe3365c60b015c61067f92f2635adf930f97542b2a',  'teacher'),
       ('bob phillp', 2, 'student@stevenscollege.edu', 'pbkdf2:sha256:150000$MAbObnog$9619d197224a7203f891d78a1539110f40bbc095063173565fedea627abd1578',  'student'),
       ('tim smith', 3,'teacher1@stevenscollege.edu', 'pbkdf2:sha256:150000$uICQ7K2l$61c882bc65d02187c6735dcb6b635a74bd5cc5dc6654372371f8c6e1adacce17','teacher'),
       ('Ms.Sullivan', 4,'teacher2@stevenscollege.edu', 'pbkdf2:sha256:150000$DPyRMV3A$85b570c573c7069f4a8a4d6c06f580ca35ba1bb3ac4edac87bf865ba1155f303', 'teacher'),
       ('Marisa Kirisame', 3, 'student2@stevenscollege.edu', 'pbkdf2:sha256:150000$lHslL9Bd$f784056cba62ecd51de8f8e6251eb8bdf857cf2d2966827546720419f92bb9d5', 'student');


INSERT INTO courses (course_num, course_title, description, credits, teacher_id, major_id)
VALUES (180, 'Software Project 2', 'Recreation of the portal', 3, 1, 1),
        (216, 'Technical Writing', 'The practice of proffesional writing',
         3, 4, 2),
         (111, 'Tig Welding Basics', 'Learning how to operate and use the TIG welder',
         3, 3, 3);

INSERT INTO sessions (times, session_name, room_number, location, course_id)
VALUES ('We meet every Tues-Thurs at 1:30 to 2:45', 'ENG-216-D',
307, 'Main campus in Mellor', 216),
      ('We meet every day at Mon-Fri at 12:00-4:30 except on Wends which we start
        at 12:30', 'CSET-180-A', '103', 'GreenField Campus down the hall three doors then
        on your right.', 180 ),
      ('We meet every Wends-Fri at 12:00 - 3:30', 'TIG-A', 108,
      'GreenField campus our room is right by the vending machine', 111),
      ('We meet every tues-thurs at 12-4', 'CSET-180-B', '103', 'Greenfield', 180 );

INSERT INTO rosters (user_id, session_id)
VALUES (5, 1),
       (2, 1),
       (2, 2);


INSERT INTO assignments (sessions_id, assign_name, description, points, due_time)
VALUES (2, 'exam1', 'first exam of course', 25, '2020-06-22 19:10'),
        (1, 'test1', 'first test of course', 30, '2020-07-24 10:05');


INSERT INTO submissions (assignment_id, student_id, grade, feedback)
VALUES (2, 5, NULL, NULL),
       (1, 2, 24, 'good');
