from config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
# -----------------------------------------------------------
import psycopg2
from psycopg2 import sql


def check_and_create_database(host, port, user, password, database_name):
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        connection.autocommit = True
        cursor = connection.cursor()

        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
            [database_name]
        )
        exists = cursor.fetchone()

        if exists:
            print(f"Database '{database_name}' already exists.")
        else:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
            print(f"Database '{database_name}' has been created.")

        if connection:
            cursor.close()
            connection.close()

    except psycopg2.Error as e:
        print("An error occurred:", e)


def check_database():
    check_and_create_database(
        config.DB_HOST,
        config.DB_PORT,
        config.DB_USER,
        config.DB_PASSWORD,
        config.DB_NAME,
    )


DATABASE_URL = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

sessionLocal = sessionmaker(bind=engine)
