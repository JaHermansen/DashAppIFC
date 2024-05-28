# Dash IFC Data Manager

Dash IFC Data Manager is a web application for managing and extracting information from Industry Foundation Classes (IFC) models.


## Description

The Data Manager Dash App is a multipage web application built using Dash, a Python framework for building analytical web applications. This application is designed to provide tools for managing and extracting information from Industry Foundation Classes (IFC) models.

## Functionality

### Pages
- Home Page: Upload IFC files and view basic information about the uploaded file.
- Extract IFC Information: Extract detailed information from the uploaded IFC file and visualize it.
- Batch Check IFC Models: To be developed.

## Features

- View and navigate through IFC models
- Extract nested information from IFC models
- Batch check IFC models for errors or inconsistencies

## Installation

1. Clone the repository:
    git clone https://github.com/yourusername/dash-ifc-data-manager.git

2. Install dependencies:
    cd dash-ifc-data-manager
    pip install -r requirements.txt

3. Run the application:
    python app.py

4. Open a web browser and go to [http://localhost:8888](http://localhost:8888)

## Usage

- Login with your username and password to access the application.
- Use the sidebar to navigate between different pages.
- Click on "Home" to go back to the main page.

## How to Use

### Home Page
* Drag and drop or select an IFC file to upload.
* View basic information about the uploaded file, such as project name and filename.
### Extract IFC Information Page
* After uploading an IFC file on the Home Page, navigate to this page.
* Detailed information extracted from the uploaded IFC file will be displayed in tabs, categorized by object class.
* Click on the "Download Excel" button to download the extracted information as an Excel spreadsheet.
### Batch Check IFC Models Page
To be developed.

## Dependencies

* Dash: A Python framework for building analytical web applications.
* Dash Bootstrap Components: Styled components for Dash applications.
* Flask: A lightweight WSGI web application framework.
* Dash Auth: Authentication for Dash applications.
* ifcopenshell: Python wrapper for the Open Source IFC library ifcopenshell.

## Credits

This project was developed by [Jacob Hermansen](https://github.com/yJahermansen).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
