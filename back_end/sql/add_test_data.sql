DROP PROCEDURE IF EXISTS addTestData;

delimiter $$
create procedure addTestData()
begin
	declare number int;
	set number = 1;
	while number <= 100 #插入N条数据
	do
	insert into player values(number, concat('姓名_', number), ceiling(rand()*60), rand()*4, ceiling(rand()*60), rand()*4, ceiling(rand()*60), rand()*4);
	set number = number + 1;
	end
	while;
end$$
delimiter ;
call addTestData();


