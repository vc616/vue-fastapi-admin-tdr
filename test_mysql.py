import pymysql

host = '192.168.6.8'
port = 3306
user = 'root'
password = 'grafana123'
database = 'grafana'

print(f'测试 MySQL 连接: {host}:{port}/{database}')
print(f'用户名: {user}')
print()

try:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        connect_timeout=5
    )
    print('连接成功!')

    with connection.cursor() as cursor:
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        print(f'数据库中有 {len(tables)} 个表:')
        for t in tables:
            print(f'  - {t[0]}')

    connection.close()
    print('\n测试成功!')
except Exception as e:
    print(f'连接失败: {type(e).__name__}: {e}')