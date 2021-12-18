import psycopg2
import datetime

# print(datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))351

DATABASE_URL = os.environ["DATABASE_URL"]

# Connect to database
try:
    connection = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = connection.cursor()

    # Этот запрос нужен для начального создания базы данных
    # sql = """CREATE TABLE weather_log (
    #         id_data INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    #         detail VARCHAR,
    #         temp INT,
    #         tg_id INT,
    #         "time" VARCHAR
    #         );"""

    # cursor.execute(sql)

    postgres_insert_query = (
        """INSERT INTO weather_log (time, tg_id, temp, detail) VALUES (%s,%s,%s,%s)"""
    )
    record_to_insert = (datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), 145708128, (int(15.77) * 100 // 100), 'hello')
    cursor.execute(postgres_insert_query, record_to_insert)

    connection.commit()
    count = cursor.rowcount
    print(count, "Record inserted successfully into weather_log table")

except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into weather_log table", error)

finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
