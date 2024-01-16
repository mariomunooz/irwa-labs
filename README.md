# Search Engine with Web Analytics
# IRWA Final Project

This projects contains the  Flaskfiles of a Search Engine web application.
Developed for the Information Retrieval and Web Analysis course under the guidance of [Ricardo Baeza-Yates](https://users.dcc.uchile.cl/~rbaeza/index.html).
At first, there are some instructions for the cloning repository and starting the
environment. At the end, there are the instructions for executing the code.

## To download this repo locally

Open a terminal console and execute:

```
cd <your preferred projects root directory>

git clone https://github.com/mariomunooz/irwa-labs.git

cd irwa-labs\search-engine-web-app

```


## Virtualenv for the project (first time use)
### Install virtualenv
Having different version of libraries for different projects.  
Solves the elevated privilege issue as virtualenv allows you to install with user permission.

In the project root directory execute:
```bash
pip3 install virtualenv
virtualenv --version
```
virtualenv 20.10.0

### Prepare virtualenv for the project
In the root of the project folder run:
```bash
virtualenv .
```

If you list the contents of the project root directory, you will see that it has created several sub-directories, including a bin folder (Scripts on Windows) that contains copies of both Python and pip. Also, a lib folder will be created by this action.

The next step is to activate your new virtualenv for the project:

```bash
source bin/activate
```

or for Windows...
```cmd
myvenv\Scripts\activate.bat
```

This will load the python virtualenv for the project.

### Installing Flask and other packages in your virtualenv
```bash
pip install -r requirements.txt
```


## Executing the code
1. Open the Project Folder (IRWA-2023-part-4)
2. Run in the terminal the following command
```bash
python -V
# Make sure we use Python 3
python3 web_app.py
```
3. To access the Search Engine Web App, press on the address that appears to be running in.

Example:
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8088
 * Running on http://192.168.1.19:8088

4. Once in the Web, you can do the searches you want and keep playing and clicking on the different options displayed
5. In case you want to quit, close the tab window or press Ctrl + C in terminal




