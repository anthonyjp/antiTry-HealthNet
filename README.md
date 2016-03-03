## antiTry HealthNet Implementation (Placeholder)
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

This will install Bower. Once that is done you can run

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

    python setup.py sdist

This will create a new `dist` directory containing the packaged app. Then it can be extracted anywhere. Once extracted, run:

    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

Then simply go to `127.0.0.1:8000` and your app will be running! The rest is simply server configuration. _(* - When using pip install you may need to add the flag `--user` to the end in environments where admin privileges are not available.)_
