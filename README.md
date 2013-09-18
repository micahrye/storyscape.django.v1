StoryScape v1.1
---------------

This is a temporary project, meant to be a standalone StoryScape application, forked off from the Sodiioo project.

Best practice would be to create a virtual environment with the python virtualenv: 
$ mkdir env
$ virtualenv env --no-site-packages

Now use your virtualenv python: 
$ source env/bin/activate

In order to install it, first install the requirements:

$ pip install -r requirements.txt

Then, follow the instructions in src/localsettings.py.template

Once your localsettings are configured you will use those for running 
the project etc. Here is an example:

$ python manage.py runserver 0.0.0.0:8888  --settings=localsettings




