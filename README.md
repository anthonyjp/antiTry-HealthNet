## antiTry HealthNet
---

### Installation
---

Once extracted, simply run:

For windows:

    run.cmd

For linux:

    run.sh

Then simply go to `127.0.0.1:8000` and your app will be running! The scripts will make sure everything is set up properly assuming you
have python3 setup properly (as 'python'). The script will also create a Super User with the credentials:

- Email: admin@admin.com
- Password: qwerty123

And create a hospital called 'Test Hospital'. This will you to do almost any action currently available. The password can of course be
changed in the admin site under '/admin'.

---
#### Development Environment
---
To setup the development environment, the following is required:

 - [Python 3.4.x](https://www.python.org/)
 - [PyCharm Professional (Free for Students)](https://www.jetbrains.com/pycharm/): Yes, we are requiring IDE use
 - [pip](https://pip.pypa.io/en/stable/): Comes with python3
 - [node.js](https://nodejs.org/en/): Simply for npm
 - [npm](https://www.npmjs.com/): Comes with node.js 

In the process you will be installing [bower](http://bower.io/) for managing frontend dependencies. To setup your development environment it is recommended you setup a virtual environment, namely using [virtualenv](https://virtualenv.readthedocs.org/en/latest/) or the support [pycharm has for virtualenv](https://www.jetbrains.com/pycharm/help/creating-virtual-environment.html).

In the terminal in pycharm (after setting up virtualenv if you opted for that) run,

    npm install -g bower
    npm install -g coffee-script

This will install Bower and CoffeeScript. Once that is done you can run

    bower install

in the project and those dependencies will be installed to a directory called bower\_components, don't worry about git, the provided .gitignore will ignore bower_components from being pushed unnecessarily. After that you must set up pip
requirements, in the terminal run:

    pip install -r requirements.txt

This will run through the requirements file and ensure the requirements are met, in not they are then installed. Once that is done you have set up the development environment!

Congrats!

---
#### Deployment
---

Deploying HealthNet is a bit of a challenge becuase of the mix we have regarding static files and databases. Ideally we want to include only the functionally required portions of the app, that would be the app directories, private_static, static, templates and so on while ignoring the gitignore, bower.json, database, git-to-svn script, .idea folder and so on.

Fortunately, this is done for us using [setuptools!](http://pythonhosted.org/setuptools/) Once you have configured everything properly and gone through the [django deployment checklist](https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/), all that is required is to run

    python setup.py

This will run few a few steps:

1. Check that DEBUG is set to false
2. Execute `python manage.py check --deploy` which will be spit out and then you are asked to confirm to continue.
3. Execute `python manage.py makemigrations`
4. Execute `python manage.py migrate`
4. Read `MANIFEST.json`
    1. Retrieve APPNAME
    2. Retrieve VERSION
    3. Retrieve INCLUDES
    4. Retrieve EXCLUDES and filter patterns out of INCLUDES
5. Package all includes into a file named APPNAME-VERSION.zip

Steps 3 and 4 can be skipped by adding the `--no-migrate` flag.

This will create a new `dist` directory containing the packaged app. Then it can be extracted anywhere.

### Primary Developers:
---
- Matthew Crocco as Development Coordinator
- Lisa Ni as Requirements Coordinator
- Anthony Perez as Quality Assurance Coordinator
- Alice Fischer as Team Coordinator
- Kyle Scagnelli as Test Coordinator