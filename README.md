# Create and upload metadata to database based on google drive file system

- Author: MinDong Sung
- Create Date: 2022-04-28
- Updated Date: 2022-05-24

---

## Objective

- The data files are stored in the google driver.
- Using google drive api, create metadata database.

## Database structure

- project - list all project and project saved folder id(google drive)
- {project}\_patient - the patient(or status)
- {project}\_cell - the cell table
- {project}\_image - the image table
- {project}\_image_quality - the image quality labelled table - fill from dashboard
- {project}\_image_center - the image quality labelled table - fill from dashboard

## Prerequisites

### Google API credentials

    - `token.json` : google drive api credentials for authentication
    - `credentials.json` : google api token

### Other parameters

    - `.env`: Other environment variables

    ```
    #.env file
    PYTHONPATH=.        # Python running path in VSCode
    RAW_DATA_FOLDER_ID= # Raw data google folder id for all tomocube data was stored

    MYSQL_HOST=         # mysql HOST
    MYSQL_PORT=         # mysql port
    MYSQL_DB=           # mysql database
    MYSQL_USER=         # mysql username
    MYSQL_PASSWORD=     # mysql password
    MYSQL_CHARSET=utf8

    ```

### Dependencies

```
poetry install
```

```
[tool.poetry.dependencies]
python = "^3.9"
pandas = "^1.4.2"
google-api-python-client = "^2.45.0"
google-auth-httplib2 = "^0.1.0"
google-auth-oauthlib = "^0.5.1"
python-dotenv = "^0.20.0"
PyMySQL = "^1.0.2"

```

## How to run

```
python main.py
```

## Related repository

- Dashboard (https://github.com/mdsung/2022_tomocube_image_quality_labeller)
