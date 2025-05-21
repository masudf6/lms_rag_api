import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch environment variables
USER = os.getenv("DBUSER")
PASSWORD = os.getenv("DBPASSWORD")
HOST = os.getenv("DBHOST")
PORT = os.getenv("DBPORT")
DBNAME = os.getenv("DBNAME")


psycopg2.extras.register_uuid()

# Establish a connection to the database
def get_db_connection():
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        sslmode='require'
    )
    return conn

# Database table creation queries
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the courses table if it doesn't exist
    create_courses_table = """
        CREATE TABLE IF NOT EXISTS courses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    
    # Create the sections table if it doesn't exist
    create_sections_table = """
        CREATE TABLE IF NOT EXISTS sections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
            parent_folder_id UUID REFERENCES sections(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    # Create the files table with course_id as a foreign key
    create_files_table = """
        CREATE TABLE IF NOT EXISTS files (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            section_id UUID REFERENCES sections(id) ON DELETE CASCADE,
            course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
            file_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    # Execute the queries
    cursor.execute(create_courses_table)
    cursor.execute(create_sections_table)
    cursor.execute(create_files_table)
    conn.commit()

    cursor.close()
    conn.close()
