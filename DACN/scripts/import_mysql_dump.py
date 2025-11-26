import pymysql

# Thông tin kết nối Railway
host = "ballast.proxy.rlwy.net"
port = 43052
user = "root"
password = "UHRSmsuSvwIjYsBRKXfhcRqrnQdJowGs"
database = "railway"

# Đường dẫn file dump
sql_file = "dump-attendance_db-202511261526.sql"

connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
cursor = connection.cursor()

with open(sql_file, "r", encoding="utf-8") as f:
    sql = f.read()

for statement in sql.split(";"):
    statement = statement.strip()
    if statement:
        try:
            cursor.execute(statement)
        except Exception as e:
            print(f"Error: {e}\nStatement: {statement}\n")

cursor.close()
connection.close()
print("Import completed!")
