import psycopg2

try:
    conn = psycopg2.connect(
        dbname="poliom_bot",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    print("Successfully connected to the database!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to the database: {e}") 