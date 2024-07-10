import logger
import pymssql

class DatabaseManager:

    def __init__(self, server, user, password, database, log_name='lfe_logs'):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.log = logger.Logger()
        self._conn = None
        
        
    def __enter__(self):
        self.connect()
        return self
    

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


    def connect(self):
        try:
            self._conn = pymssql.connect(
                server=self.server,
                user=self.user,
                password=self.password,
                database=self.database
            )

            self.log.info(f"Connected to SQL Server ({self.server}), ({self.database})")

        except pymssql.Error as e:
            self.log.error(f"Error connecting to SQL Server, please check the docker container: {e}")


    def execute_query(self, query):
        try:
            cursor = self._conn.cursor()
            cursor.execute(query)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            self._conn.commit()
            return None  # Return None for successful non-SELECT queries
        except pymssql.ProgrammingError as e:
            self.log.error(f"Error executing query: {e}")
            return 'Error', str(e)  # Return tuple indicating error status and message
        

    def close(self):
        if self._conn:
            self._conn.close()
            self.log.info('Closing DB connection')

