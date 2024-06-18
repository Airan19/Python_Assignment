import logger
import pymssql

class DatabaseManager:

    def __init__(self, server, user, password, database, main_db, port, log_name='sql'):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.main_db = main_db
        self.port = port
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
                database=db,
                port=self.port
            )

            self.log.info(f"Connected to SQL Server ({self.server}), ({self.database})")
            self.create_table_if_not_exists()
            
        except pymssql.Error as e:
            self.log.error(f"Error connecting to SQL Server, please check the docker container: {e}")
            self.create_database_if_not_exists()


    def create_database_if_not_exists(self):
        try:
            self.connect(self.main_db)
            self._conn.autocommit(True)
            cursor = self._conn.cursor()
            cursor.execute(f"CREATE DATABASE {self.database}")
            self._conn.autocommit(False)
            self.log.info(f"Database '{self.database}' created successfully.")
           
            # Switch to WebsitesDB
            cursor.execute(f"USE {self.database}")
            self.create_table_if_not_exists()
            
        except pymssql.Error as e:
            self.log.error(f"Error creating database {e}")
            self.log.info('Please check the mssqsl server is running on docker or not.')



    def create_table_if_not_exists(self):
        try:
            cursor = self._conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = 'Employees'")
            exists = cursor.fetchone()[0]
            if not exists:
                # Create employees table
                cursor.execute("""CREATE TABLE Employees(
                            id INT IDENTITY(1,1),
                            emp_id INT PRIMARY KEY NOT NULL,
                            name VARCHAR(100) NOT NULL,
                            gender VARCHAR(10) NOT NULL,
                            phone VARCHAR(10),
                            department VARCHAR(100) NOT NULL,
                            date_of_birth DATE,
                            email VARCHAR(255) UNIQUE,
                            experience INT
                )""")
                self.log.info("Table 'Employees' created successfully.")
            else:
                self.log.info("Table 'Employees' already exists.")
            
        except pymssql.Error as e:
            self.log.error(f"Error creating table 'Employees': {e}")

        
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



