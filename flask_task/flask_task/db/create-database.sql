PRINT 'Creating WebsitesDB...';
USE master;
GO

CREATE DATABASE WebsitesDB;
GO

PRINT 'Creating websites table...';
USE WebsitesDB;
GO

CREATE TABLE websites (
    id INT PRIMARY KEY IDENTITY (1,1),
    site_name VARCHAR(100),
    url VARCHAR(255),
    status VARCHAR(4)
);
GO

PRINT 'Database and table creation completed.';
