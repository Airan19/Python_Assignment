import logger
import pymssql

class DatabaseManager:

    def __init__(self, server, user, password, database, main_db, log_name='sql'):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.main_db = main_db
        self.log = logger.Logger()
        self._conn = None

    
    def __enter__(self):
        self.connect(self.database)
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


    def connect(self, db):
        try:
            self._conn = pymssql.connect(
                server=self.server,
                user=self.user,
                password=self.password,
                database=db
            )
            return True
            # self.log.info(f"Connected to SQL Server ({self.server}), ({self.database})")

        except pymssql.Error as e:
            self.log.error(f"Error connecting to SQL Server, please check the docker container: {e}")
            self.create_database_if_not_exists()
            return False


    def create_database_if_not_exists(self):
        try:
            self.connect(self.main_db)
            self._conn.autocommit(True)
            cursor = self._conn.cursor()
            cursor.execute(f"CREATE DATABASE {self.database}")
            self._conn.autocommit(False)
            self.log.info(f"Database 'WebsitesDB' created successfully.")
        
            # Switch to WebsitesDB
            cursor.execute(f"USE {self.database}")
            self.create_table_if_not_exists()
            
        except pymssql.Error as e:
            self.log.error(f"Error creating database {e}")
            self.log.info('Please check the mssqsl server is running on docker or not.')

        
    def create_table_if_not_exists(self):
        try:
            cursor = self._conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = 'Websites'")
            exists = cursor.fetchone()[0]

            if not exists:
                # Create websites table
                cursor.execute("""CREATE TABLE websites(\
                            id INT PRIMARY KEY IDENTITY (1,1),\
                            site_name VARCHAR(100),\
                            url VARCHAR(255),\
                            status VARCHAR(4)\
                )""")
                self.log.info("Table 'websites' created successfully.")
            else:
                self.log.info("Table 'websites' already exists.")

        except pymssql.Error as e:
            self.log.error(f"Error creating table 'websites': {e}")

        
    def execute_query(self, query, params=None, fetchone=False, fetchall=False):
        try:
            cursor = self._conn.cursor()
            cursor.execute(query,params)
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                result = None
            self._conn.commit()
            return result
        except pymssql.Error as e:
            self.log.error(f"Error executing query: {e}")
            return None
        

    def close(self):
        if self._conn:
            self._conn.close()
            self.log.info('Closing DB connection')



