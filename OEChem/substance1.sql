CREATE TABLE IF NOT EXISTS `substance1` (
    `sid` int(11) NOT NULL PRIMARY KEY,
    `cid` int(11)
);

LOAD DATA LOCAL  INFILE 'substance1.csv' 
INTO TABLE substance1
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS (sid,@vcid)
SET cid = nullif(@vcid,'');

ALTER TABLE substance1 ADD INDEX(cid);

