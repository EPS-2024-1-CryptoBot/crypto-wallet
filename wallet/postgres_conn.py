import os # pragma: no cover
import psycopg2 # pragma: no cover

from log import get_logger


class PostgresConnector: # pragma: no cover
    def __init__(self):
        self.__db_user = os.environ.get("PG_USER")
        self.__db_pass = os.environ.get("PG_PASS")
        self.__db_host = os.environ.get("PG_HOST")
        self.__db_name = os.environ.get("PG_DB")
        self.__db_ssl = os.environ.get("PG_SSL") or False
        self.__logger = get_logger(self.__class__.__name__)
        self.establish_connection()

    @property
    def __conn_string(self):
        ssl_mode = "?ssl=require" if bool(self.__db_ssl) else ""
        return f"postgres://{self.__db_user}:{self.__db_pass}@{self.__db_host}/{self.__db_name}{ssl_mode}"

    def establish_connection(self):
        self.__logger.info(f"ESTABLISHING CONNECTION TO POSTGRES DATABASE")
        self.connection = psycopg2.connect(self.__conn_string)

        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        self.__logger.info(f"POSTGRES CONNECTED SUCCESSFULLY")

    def execute_query(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def close_connection(self):
        self.connection.close()
