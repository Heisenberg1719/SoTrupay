import mysql.connector
from http import HTTPStatus
from App.utilities.config import *
from mysql.connector import Error

class MySQLDatabase:
    @classmethod
    def get_connection(cls):
        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None

    @classmethod
    def execute_query(cls, query, params=None):
        connection = cls.get_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query, params)
                connection.commit()
                # print("Query executed successfully")
                return {"message": "Query executed successfully", "status": HTTPStatus.OK}
            except Error as e:
                print(f"Error executing query: {e}")
                return {"message": f"Error executing query: {e}", "status": HTTPStatus.INTERNAL_SERVER_ERROR}
            finally:
                cursor.close()
                connection.close()
        else:return {"message": "Failed to connect to the database", "status": HTTPStatus.SERVICE_UNAVAILABLE}

    @classmethod
    def fetch_results(cls, query, params=None):
        connection = cls.get_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return {"data": results, "status": HTTPStatus.OK}
            except Error as e:
                print(f"Error fetching results: {e}")
                return {"message": f"Error fetching results: {e}", "status": HTTPStatus.INTERNAL_SERVER_ERROR}
            finally:
                cursor.close()
                connection.close()
        else:return {"message": "Failed to connect to the database", "status": HTTPStatus.SERVICE_UNAVAILABLE}
