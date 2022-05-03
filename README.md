# Create and upload metadata to database based on google drive file system

- Author: MinDong Sung
- Create Date: 2022-04-28
- Updated Date: 2022-05-03

---

## Objective

- The data files are stored in the google driver.
- Using google drive api and database, create metadata database.

## Database structure

- project - list all project and project saved folder id(google drive)
- project_patient - the patient(or status)
- project_cell - the cell table
- project_image - the image table
- project_image_quality - the image quality labelled table - fill with dashboard

## Related repository

- https://github.com/mdsung/2022_tomocube_image_quality_labeller
