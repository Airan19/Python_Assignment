# API Documentation

## Overview
This API allows you to manage and check the status of websites. It includes endpoints for creating website entries and retrieving their statuses. Additionally, a background task periodically checks the status of all websites.

## Base URL
The base URL for all endpoints is assumed to be `http://<your-domain>:5000`.

## Endpoints

### 1. Create a Website Entry

- **Endpoint:** `/websites`
- **Method:** `POST`
- **Description:** Creates a new entry for a website and checks its initial status.
- **Request Body:**
  ```json
  {
      "site_name": "youtube",
      "url": "https://youtube.com"
  }
*   **Response:**
    * **Success**: 201 Created
    ```json
    { 
        "message": "Website created successfully"
    }
    ```

### 2\. Get Status of All Websites

*   **Endpoint:** /website/status
    
*   **Method:** GET
    
*   **Description:** Retrieves the status of all websites.
    
*   **Response:** 
    * **Success**: 200 OK
    ```json
    {
        "response": [
            {
                "site_name": "youtube",
                "url": "https://youtube.com",
                "status": "UP"
            },
            {
                "site_name": "google",
                "url": "https://google.com",
                "status": "DOWN"
            }
        ]
    }
    ```
    * **Failure**: 404 Not Found
    ```json
    {
        "message": "No records found!"
    }

    ```

        
### 3\. Get Status of a Specific Website

*   **Endpoint:** /website/status/
    
*   **Method:** GET
    
*   **Description:** Retrieves the status of a specific website by its site name.
    
*   **Path Parameter:**
    
    *   site\_name (string) - The name of the website.
        
*   **Response:**
    * **Success** : 200 OK
    ```json
    {
        "site_name": "youtube",
        "url": "https://youtube.com",
        "status": "UP"
    }
    ```

    * **Failure**: 404 Not Found
    ```json
    {
        "message": "No such site-name found!"
    }
    ```
    
        

## Background Task
A background task is scheduled to run every 10 seconds to check the status of all websites and update their status in the database if there is a change.

## Helper Functions

### `check_status(url)`
- **Description:** Checks the status of a given URL. Returns 'UP' if the status code is between 200 and 299, otherwise returns 'DOWN'.

### `execute_sql_query(query, params=None, fetchone=False, fetchall=False)`
- **Description:** Executes the given SQL query with optional parameters and fetch options.

### `wait_for_mssql(app)`
- **Description:** Waits for the MSSQL server to be ready before proceeding with database operations.

## Error Handling
The application logs errors encountered while requesting URLs and during database operations.

## Scheduler
The `run_check_website_status` function is scheduled to run every 10 seconds using the scheduler object from the main module. It calls the `check_webiste_status` function inside it to check the status of all websites and updates the database accordingly.

## Logging
The Logger class is used for logging informational and error messages.

## Dependencies

- Flask
- waitress
- flask_apscheduler
- requests
- time
- config
- pymssql
- DatabaseManager
- Logger
- os
- dotenv

## Usage
1. Start the Flask application.
2. Use the provided endpoints to create website entries and check their statuses.
3. The background task will automatically update the status of all websites every 10 seconds.

## Configuration
Ensure that your configuration settings (e.g., database credentials) are correctly set in the config module.

Replace `<your-domain>` with the actual domain or IP address where your application is running.
