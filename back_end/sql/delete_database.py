import pymysql  
  
# 连接MySQL数据库  
conn = pymysql.connect(host='localhost', user='root', password='123456', database='saolei')  
cursor = conn.cursor()  
  
cursor.execute("SET FOREIGN_KEY_CHECKS=0;")  
# 获取数据库中的所有表名  
cursor.execute("SHOW TABLES")  
table_names = cursor.fetchall()  
  
# 遍历表名并删除每个表  
for table_name in table_names:  
    table_name = table_name[0]  
    cursor.execute(f"DROP TABLE {table_name}")  
  
# 关闭数据库连接  
cursor.execute("SET FOREIGN_KEY_CHECKS=1;")  
conn.close()


# python manage.py flush
# redis-cli -h localhost -p 6379 flushall


