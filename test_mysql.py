import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='Amrahazra7890'
    )
    print('MySQL connection successful')
    conn.close()
except Exception as e:
    print(f'MySQL connection failed: {e}')