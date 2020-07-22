# Data Ocean

-------------------------------------------------------------------------------------------------------------------------
INSTALL ON UBUNTU 18.04 (DEV)
-------------------------------------------------------------------------------------------------------------------------

###### System update and packages install 
- $ sudo apt update && sudo apt upgrade
- $ sudo apt install dkms linux-headers-generic
- $ sudo apt install python3-setuptools python3-distutils python3-venv libpq-dev
- $ sudo apt install mc htop git

###### Install PostgreSQL
- $ sudo apt update
- $ sudo apt install postgresql postgresql-contrib
- $ psql --version

###### Create db & user
- $ sudo -u postgres psql
- postgres=# create database your_db_name;
- postgres=# create user your_db_user with password 'your_db_password';
- postgres=# grant all on database your_db_name to your_db_user;
- postgres=# /q

###### Install Python 3.7
- $ sudo apt install software-properties-common
- $ sudo add-apt-repository ppa:deadsnakes/ppa
- $ sudo apt update
- $ sudo apt install python3.7
- $ python3.7 --version
- $ sudo apt install python3.7-dev python3.7-venv

###### Create Your_Fork on GitHub from: https://github.com/3v-workspace/Data_converter

###### Clone Your_Fork repo & create virtual environment & install requirements
- $ git clone https://github.com/Your_Fork/Data_converter.git
- $ cd Data_converter
- $ python3.7 -m venv .venv
- $ source .venv/bin/activate
- (.venv)$ pip install -U pip setuptools wheel
- (.venv)$ pip install -r requirements.txt 

###### Create your settings_local.py
- Copy **`data_converter/settings_local.base.py`** to **`data_converter/settings_local.py`**

###### Setup your settings in settings_local.py
- Setup your settings in DATABASES section 
- Setup your settings in MAIL section (if use SMTP)
- ...

###### Migrate
- (.venv)$ ./manage.py migrate

###### Load fixtures
- (.venv)$ ./manage.py loaddata category
- (.venv)$ ./manage.py loaddata register

###### Collect static files
- (.venv)$ ./manage.py collectstatic

###### Run server
- (.venv)$ ./manage.py runserver 127.0.0.1:8000


-----------------------------------------------------------------------------------------------------
User API endpoint
-----------------------------------------------------------------------------------------------------
- Social Registration: `/api/accounts/signup/`
- Social Login: `/api/accounts/login/`
- Social Logout: `/api/accounts/logout/`
-----------------------------------------------------------------------------------------------------
- Registration (with email send): `/api/rest-auth/registration/`
- Registration Confirm: `/api/rest-auth/registration-confirm/<int:user_id>/<str:confirm_code>/`
- Login: `/api/rest-auth/login/`
- Logout: `/api/rest-auth/logout/`
- Password Change (with old password): `/api/rest-auth/password/change/`
- Password Reset (with email send): `/api/rest-auth/password/reset/`
- New Password after Password Reset: `/api/rest-auth/password/reset/confirm/<str:UID>/<str:token>/`
-----------------------------------------------------------------------------------------------------
- User list: `/api/users/`
- User Details: `/api/rest-auth/user/`
-----------------------------------------------------------------------------------------------------

-----------------------------------------------------------------------------------------------------
Setup Google Login
-----------------------------------------------------------------------------------------------------
To add Google login on your app, you’ll need to set up OAuth application via Google Developers Console:
https://console.developers.google.com/

Getting started
- Go to Dashboard, create a NEW PROJECT
- Name your new project, preferably your website or app name. User will be able to see this project name when we redirect them to Google login page.
- Click “CREATE” to proceed.

APIs Credentials
- Back to “Dashboard”, go to “Credentials” on left panel.
- Create credentials. On the dropdown, choose “OAuth Client ID” option.

OAuth consent screen
- Make sure you fill out the “OAuth Consent Screen” form.
- You’ll only need to provide “Application name”, “Email” and click “SAVE”.

Create OAuth client ID
- Now, you can create your OAuth Client ID by filling out these details;
- Authorized Javascript origins (http://127.0.0.1:8000)
- Authorized redirect URL (http://127.0.0.1:8000/accounts/google/login/callback/)

Obtain OAuth client
- Once you click “CREATE”, you will be able to obtain your “client ID” and “client Secret”.
- You’ll need this information to proceed the next steps


Add a site
On the SITES section, click “sites” and fill out the details and click “Save”:
Domain name: 127.0.0.1:8000
Display name: 127.0.0.1:8000

Add social applications
Back to admin homepage, under “SOCIAL ACCOUNTS” section, click “Social applications” to fill out these settings:
Provider: Google
Name: Google API
Client id: (refer step 7, your OAuth details)
Secret key: (refer step 7, your OAuth details)

See the result

