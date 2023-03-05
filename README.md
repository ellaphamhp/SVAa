# VISAREP


## Video demo: https://youtu.be/JTeoWfTlFVc

## Description:
 VISAREP is a web portal for visa applicants to create and organize their applications. It simplifies the preparation process by providing latest visa requirement updates, automatically generate clear to-do lists, put them in tidied interface and offer seamless connection to 3rd parties (travel agents, insurance).

The name is short for Visa Representatives: an agent who can help you query your visa requirements, and other useful information to help you with your visa application process. It's also short for Visa Application Repositories: a place where you can store all your ongoing or archived visa applications


## Overall architecture:
#### **FRONTEND:**
 The frontend element of the projects are built using Python Flask Framework. Jinja templates are utilized as much as possible. The CSS libraries are from Bootstrap 5.1. Some elements of Javascripts are included for user interations as well.

#### **BACKEND:**
 There is a small SQLlite database used to store users, visa and applications data. There is also some static data files inlcuded in the source code to feed static data to the websites such as airports, countries.
  The backend operations are written within helper.py and app.py files, using Python. One of these function establishes API call with a 3rd party called Duffle to get flight reservations details. The API used is test only and any reservations made are not live.



## Folde- by-folder explaination:
### **1.  'app.py' file:**
This is the main file containing the backend python code written following the Flask framework. The first 9 rows import the python functions required from several python libraries. It alsos imports the python functions written from 'helper.py' file.

Row 12 to 24 set out the basic configurations for the web app, including defining the app framework, the SQL lite database and its behaviour to store sessions.

Row 26 to 39 define sever global variables that will be used throughout the web app. This is to ensure within a session, global variables can be remembered and passed along different routes.

From row 54 onwards, different routes of the app are defined. Refer to the definition section within the code to understand what are the functions of each routes. Some of the main one are:
 - /inquiry: Allow user to query the visa types suitable for them
 - /requirement: Returning the requirements for the chosen visa types
 - /apply: Creating application for the chosen visa type
 - /prepare-doc: Get user's trip details for flight reservations
 - /get-doc: Query Duffle API and return flight reservations based on user's inputted trip details
 - /register: Allow user to register for an account on the web portal. The account is saved into SQLite DB
 - /application: Return list of applications for the signed-in user
 - /save-progress: Change progress of documents preparation for each applications of the signed-in user
 - /get-flight-iti: Return pdf format of the flight resevations



### **2. 'helper.py' file:**
This file contains code for functions performing some particular tasks accross the web portal:

 - book_flights:  Request flight offers and create flight ordersrased on applicant's desired trip information and personal details. It establishes(test) Duffle API call to search and creat flight reservations.
 - apology: Render message as an apology to user where there's input error(Source: Cs50 2022's week 9)
 - login_required: Decorate routes to require login (Source: Cs50 2022's week 9)
 - required_input(): Check if all required variables are provied
 - date_validate: Check if the input is compatible with type date
 - email_validate: check if the input is compatible with type email
 - input_validate: Check if the input contain special charactores


### **3. 'requirements.txt' file:**
This file contains all other requirements for the app to stand on (Assuming the app is developed within CS50 2022 environment)

### **4. 'visa.db' file:**
This is the SQLite database storing data for:
- users: List of registered users
- applications: List of all applications created for all users
- airports: List of all airports (covered in flight reservartion function)
- Visa_Type: List of all visa types supported by VISAREP
- Visa_Requirement: List of all requirements for all supported visa types
- Application Status: List of preparation status for each requirement items for all created visa applications.

### **5. 'static' folder:**
Some frontend elements including images, Javascript scripts and CSS

####  *scripts.js:*
Some Javascript functions used to enable interactive UX:
- updateCheckbox: Change the check box accordingly to acquire status
- validate: Change color of text when the required document is prepared
- updateProgress: Update the input variable to tell whether a requirement is prepared

#### *styles.css:*
Most CSS in the project is taken from Bootstrap library. However this file defines some other custom classes.

### **6. 'templates' folder:**
All html templates for the web portal.

### **7. 'data' folder:**
Storing 2 static csv files containing list of aiports and countries.

### **8. 'flask_session' folder:**
(This is not part of the source code) This is the overall flask_session so far. So if an valid existing credentials are used, the web portal can return its corressponding session'd data.

### **9. 'python_scripts' folder:**
(This is not part of the source code) This is either individual python functions written in 'helper.py' file or some other miscellaneous python functions written for testing purposes. This folder is not required in production.





