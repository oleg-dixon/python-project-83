import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

def get_connection():
    try:
        print('The connection is established')
        return conn
    except:
        print("Can`t establish connection to database")


# if __name__ == '__main__':
#     conn = get_connection()
#     if conn:
#         print('The connection is closed')
#         conn.close()

