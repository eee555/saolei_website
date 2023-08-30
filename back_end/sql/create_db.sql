# CREATE DATABASE saolei;

drop table if exists player;

create table player
(
id INT,
playerName VARCHAR(8),
begTimeMs INT,
begBvs FLOAT,
intTimeMs INT,
intBvs FLOAT,
expTimeMs INT,
expBvs FLOAT
) CHARSET=utf8mb4;







