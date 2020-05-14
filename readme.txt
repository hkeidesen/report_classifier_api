conda activate env(MacBook)/api_env(PC)
conda evn list

#run on your computer. Requires Visual Studio Code

install Anaconda
create a virtual environment (https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
tl;dr: 
in a terminal, type (replece 'myenv' with a name of your choosing), followed by enter:
    $ conda create -n myenv python=3.7 
then type:
    $ yes
after the environment has been sucessfully set-up, and activated (see the terminal output)

install all packages in requirements.txt by typing:
    $ pip install -r requirements.txt

after all that has been installed, laumnch Postman and specify the HTTP request (remember to select correct method for the request!)


