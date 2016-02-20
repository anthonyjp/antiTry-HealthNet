## antiTry HealthNet Implementation (Placeholder)
---
To setup the development environment, pip, node.js and npm are required. Once npm is installed run:

npm install -g bower

This will install Bower. Once that is done you can run

bower install

in the project and those dependencies will be installed to a directory called bower_components, don't worry about git,
the provided .gitignore will ignore bower_components from being pushed unnecessarily. After that you must set up pip
requirements, in the project directory run:

pip install -r requirements.txt

This will run through the requirements file and ensure the requirements are met, otherwise they are installed. Once that
is done you have set up the development environment! At any moment you could have imported this into PyCharm, but if you
haven't, you should now to finalize the setup.

Congrats!