# 2FA
o	This application provides a registration and login system for users as well as a two-factor authentication component. The backend of this application is built with Python and Flask. The front end is built with HTML, Bootstrap, and CSS.
o	When a user registers by providing an email and password it inserts the user’s login data into a MySQL table with the passwords hashed.
o	To authenticate the user the application accepts a phone number and country code from the user and sends a verification code via Authy API to the provided phone number. The user then enters the verification code the application checks it against the code sent to the user’s phone via Authy API. If the code is correct a success message is displayed.
