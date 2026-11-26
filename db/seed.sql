INSERT INTO app_user (user_id, given_name, surname, email, affiliation, country, phone_number) VALUES

 (1,  'Arman',     'Armanov',      'arman.armanov@example.com',         'Nazarbayev University', 'Kazakhstan', '+77700000001'),
 (2,  'Amina',     'Aminova',      'amina.aminova@example.com',         'Nazarbayev University',  'Kazakhstan','+77700000002'),
 (3,  'Dana',      'Orazgalieva',  'dana.orazgalieva@example.com',      'Nazarbayev University', 'Kazakhstan', '+77700000003'),
 (4,  'Iliyas',    'Zharylgassin', 'iliyas.zharylgassin@example.com',   'Al-Farabi KazNU',       'Kazakhstan', '+77700000004'),
 (5,  'Alikhan',   'Galymov',      'alikhan.galymov@example.com',       'Nazarbayev University', 'Kazakhstan', '+77700000005'),
 (6,  'Alikhan',   'Baiadil',      'alikhan.baiadil@example.com',       'KBTU',                  'Kazakhstan', '+77700000006'),
 (7,  'Nursultan', 'Tursyngazin',  'nursultan.tursyngazin@example.com', 'Nazarbayev University',  'Kazakhstan','+77700000007'),
 (8,  'Alisher',   'Kamidolla',    'alisher.kamidolla@example.com',     'Satbayev University',   'Kazakhstan', '+77700000008'),
 (9,  'Yerzat',    'Kabdullov',    'yerzat.kabdullov@example.com',      'Astana IT University',  'Kazakhstan', '+77700000009'),
 (10, 'Dias',      'Abdullin',     'dias.abdullin@example.com',         'Shakarim University',   'Kazakhstan', '+77700000010'),
 (11, 'Ramil',     'Orazgaliev',   'ramil.orazgaliev@example.com',      'Nazarbayev University', 'Kazakhstan', '+77700000011'),
 (12, 'Timur',     'Akbasov',      'timur.akbasov@example.com',         'KIMEP University',      'Kazakhstan', '+77700000012');

INSERT INTO author (author_id) VALUES
 (2),
 (3),
 (5),
 (7),
 (8),
 (10),
 (11);



INSERT INTO author_research_area (author_id, area_label) VALUES
 (2, 'Computer Science'),
 (3, 'Computer Science'),
 (5, 'Computer Science'),
 (7, 'Computer Science'),
 (8, 'Computer Science'),
 (10, 'Computer Science'),
 (11, 'Computer Science');

INSERT INTO reviewer (reviewer_id, years_experience) VALUES
 (1, 6), (3, 4), (4, 5), (6, 8), (7, 2), (9, 3), (10, 1), (12, 7);



INSERT INTO reviewer_expertise (reviewer_id, area_label) VALUES
 (1, 'Databases'),
 (3, 'Mathematics'),
 (4, 'Databases'),
 (6, 'Databases'),
 (7, 'Databases'),
 (9, 'Mathematics'),
 (10, 'Mathematics'),
 (12, 'Mathematics');


INSERT INTO conference (conference_id, name, acronym, description, city, country,
                        start_date, end_date, submission_deadline, review_deadline) VALUES

 (1, 'NU Orchestra Event', 'NUOE 2026',
     'Annual event.',
     'Astana', 'Kazakhstan', '2026-11-20', '2026-11-20', '2026-11-20', '2026-11-20'),
 (2, 'Math Carousel', 'MC 2026',
     'Annual event.',
     'Almaty', 'Kazakhstan', '2026-11-20', '2026-11-20', '2026-11-20', '2026-11-20'),
 (3, 'Semey Speedcubing Event', 'SSE 2026',
     'Annual event.',
     'Semey',  'Kazakhstan', '2026-11-20', '2026-11-20', '2026-11-20', '2026-11-20');

INSERT INTO conference_host (conference_id, host_name) VALUES
 (1, 'Nazarbayev University'),
 (2, 'Al-Farabi KazNU'),
 (3, 'Shakarim University');

INSERT INTO conference_reviewer (conference_id, reviewer_id) VALUES
 (1, 1), (1, 3), (1, 4), (1, 7), (1, 9), 

 (1, 12), (2, 3), (2, 4), (2, 6), (2, 7), (2, 10),
 (3, 1), (3, 9), (3, 12);


INSERT INTO track (track_id, conference_id, name, description, research_area, coordinator_id) VALUES

 (1, 1, 'Track 1', 'Track.', 'Computer Science', 1),
 (2, 1, 'Track 2', 'Track.', 'Computer Science', 12),
 (3, 2, 'Track 3', 'Track.', 'Computer Science', 6),
 (4, 2, 'Track 4', 'Track.', 'Computer Science', 4),
 (5, 3, 'Track 5', 'Track.', 'Computer Science', 9);

INSERT INTO conference_session (session_id, conference_id, title, session_date,
                                start_time, end_time, room_label, chair_id) VALUES

 (1, 1, 'Session 1', '2026-11-20', '12:00', '13:00', 'Room 100', 4),
 (2, 1, 'Session 2', '2026-11-20', '12:00', '13:00', 'Room 101', 3),
 (3, 1, 'Session 3', '2026-11-20', '12:00', '13:00', 'Room 102', 12),
 (4, 2, 'Session 4', '2026-11-20', '12:00', '13:00', 'Room 103', 6),
 (5, 2, 'Session 5', '2026-11-20', '12:00', '13:00', 'Room 104', 7);

INSERT INTO paper (paper_id, track_id, title, abstract, submission_date, status, session_id) VALUES


 (1, 1, 'Paper 1', 'This paper studies databases.', '2026-11-20', 'accepted', 1),
 (2, 1, 'Paper 2', 'This paper uses Machine Learning.', '2026-11-20', 'accepted', 1),
 (3, 2, 'Paper 3', 'This paper uses machine learning.', '2026-11-20', 'accepted', 2),
 (4, 2, 'Paper 4', 'This paper studies databases.', '2026-11-20', 'accepted', NULL),
 (5, 1, 'Paper 5', 'This paper studies databases.', '2026-11-20', 'rejected', NULL),
 (6, 2, 'Paper 6', 'This paper studies databases.', '2026-11-20', 'under review', NULL),
 (7, 1, 'Paper 7', 'This paper studies databases.', '2026-11-20', 'submitted', NULL),
 (8, 1, 'Paper 8', 'This paper studies databases.', '2026-11-20', 'withdrawn', NULL),
 (9, 2, 'Paper 9', 'This paper studies databases.', '2026-11-20', 'withdrawn', NULL),
 (10, 3, 'Paper 10', 'This paper studies databases.', '2026-11-20', 'accepted', 4),
 (11, 3, 'Paper 11', 'This paper studies databases.', '2026-11-20', 'rejected', NULL),
 (12, 4, 'Paper 12', 'This paper studies databases.', '2026-11-20', 'withdrawn', NULL);

INSERT INTO paper_keyword (paper_id, keyword) VALUES


 (1, 'computer science'),
 (2, 'computer science'),
 (3, 'computer science'),
 (4, 'computer science'),
 (5, 'computer science'),
 (6, 'computer science'),
 (7, 'computer science'),
 (8, 'computer science'),
 (9, 'computer science'),
 (10, 'computer science'),
 (11, 'computer science'),
 (12, 'computer science');

INSERT INTO paper_author (paper_id, author_id, author_position, is_corresponding) VALUES


 (1,  5,  1, TRUE),  (1,  8,  2, FALSE),
 (2,  3,  1, TRUE),  (2,  5,  2, FALSE),
 (3,  11, 1, TRUE),  (3,  3,  2, FALSE),
 (4,  8,  1, TRUE),
 (5,  7,  1, TRUE),
 (6,  11, 1, TRUE),  (6,  2,  2, FALSE),
 (7,  8,  1, TRUE),
 (8,  2,  1, TRUE),
 (9,  2,  1, TRUE),  (9,  5,  2, FALSE),
 (10, 10, 1, TRUE),  (10, 7,  2, FALSE),
 (11, 10, 1, TRUE),
 (12, 3,  1, TRUE),  (12, 2,  2, FALSE);

INSERT INTO paper_version (paper_id, version_no, file_location, uploaded_at) VALUES

 (1,  1, '/files/paper11.pdf',  '2026-11-20 12:00'),
 (1,  2, '/files/paper12.pdf',  '2026-11-20 12:00'),
 (2,  1, '/files/paper21.pdf',  '2026-11-20 12:00'),
 (2,  2, '/files/paper22.pdf',  '2026-11-20 12:00'),
 (2,  4, '/files/paper24.pdf',  '2026-11-20 12:00'),
 (3,  1, '/files/paper31.pdf',  '2026-11-20 12:00'),
 (4,  1, '/files/paper41.pdf',  '2026-11-20 12:00'),
 (4,  2, '/files/paper42.pdf',  '2026-11-20 12:00'),
 (5,  1, '/files/paper51.pdf',  '2026-11-20 12:00'),
 (6,  1, '/files/paper61.pdf',  '2026-11-20 12:00'),
 (7,  1, '/files/paper71.pdf',  '2026-11-20 12:00'),
 (8,  1, '/files/paper81.pdf',  '2026-11-20 12:00'),
 (8,  2, '/files/paper82.pdf',  '2026-11-20 12:00'),
 (9,  1, '/files/paper91.pdf',  '2026-11-20 12:00'),
 (10, 1, '/files/paper101.pdf', '2026-11-20 12:00'),
 (10, 2, '/files/paper102.pdf', '2026-11-20 12:00'),
 (11, 1, '/files/paper111.pdf', '2026-11-20 12:00'),
 (12, 1, '/files/paper121.pdf', '2026-11-20 12:00');

INSERT INTO review (review_id, paper_id, reviewer_id, overall_score, recommendation,
                    comments_for_authors, review_submission_date) VALUES


 (1,  1,  1,  5, 'accept', 'Good paper.', '2026-11-20'),
 (2,  1,  4,  4, 'accept', 'Good paper.', '2026-11-20'),
 (3,  1,  12, 4, 'accept', 'Good paper.', '2026-11-20'),
 (4,  2,  1,  4, 'accept', 'Good paper.', '2026-11-20'),
 (5,  2,  4,  5, 'accept', 'Good paper.', '2026-11-20'),
 (6,  3,  12, 5, 'accept', 'Good paper.', '2026-11-20'),
 (7,  3,  1,  4, 'accept', 'Good paper.', '2026-11-20'),
 (8,  4,  4,  4, 'accept', 'Good paper.', '2026-11-20'),
 (9,  4,  3,  4, 'accept', 'Good paper.', '2026-11-20'),
 (10, 5,  1,  2, 'reject', 'Good paper.', '2026-11-20'),
 (11, 5,  12, 2, 'reject', 'Good paper.', '2026-11-20'),
 (12, 6,  1,  3, 'accept', 'Good paper.', '2026-11-20'),
 (13, 8,  4,  3, 'reject', 'Good paper.', '2026-11-20'),
 (14, 9,  12, 2, 'reject', 'Good paper.', '2026-11-20'),
 (15, 10, 6,  5, 'accept', 'Good paper.', '2026-11-20'),
 (16, 10, 4,  4, 'accept', 'Good paper.', '2026-11-20'),
 (17, 11, 6,  2, 'reject', 'Good paper.', '2026-11-20'),
 (18, 11, 3,  1, 'reject', 'Good paper.', '2026-11-20'),
 (19, 12, 7,  3, 'accept', 'Good paper.', '2026-11-20'),
 (20, 12, 10, 2, 'reject', 'Good paper.', '2026-11-20');



SELECT setval(pg_get_serial_sequence('app_user',           'user_id'),       (SELECT MAX(user_id)       FROM app_user));

SELECT setval(pg_get_serial_sequence('conference',         'conference_id'), (SELECT MAX(conference_id) FROM conference));

SELECT setval(pg_get_serial_sequence('track',              'track_id'),      (SELECT MAX(track_id)      FROM track));

SELECT setval(pg_get_serial_sequence('conference_session', 'session_id'),    (SELECT MAX(session_id)    FROM conference_session));

SELECT setval(pg_get_serial_sequence('paper',              'paper_id'),      (SELECT MAX(paper_id)      FROM paper));
SELECT setval(pg_get_serial_sequence('review',             'review_id'),     (SELECT MAX(review_id)     FROM review));
