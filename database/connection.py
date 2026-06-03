import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            sslmode="prefer"  # IMPORTANTE para Supabase
        )
        
        cursor = conn.cursor()
        cursor.execute('SET search_path TO "personal-finance-ai", public;')
        conn.commit()
        cursor.close()
        
        return conn

    except Exception as e:
        print("❌ Error de conexión a la BD:", e)
        return None