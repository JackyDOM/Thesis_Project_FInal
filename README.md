# Set Up Python Environment
### Follow the steps below to set up the Python environment in your local project.
#### 1. Install Python in Your Local Project
Ensure that Python is configured on your local machine. To verify,run: 
````courseignore
python3 --version or python --version
````
If Python is not installed, you can install it and set up a virtual environment:
````courseignore
python3 or python -m venv /path/to/env
````
#### 2. Activate the Environment
Activate the virtual environment by running:
````courseignore
source /path/to/env/bin/activate
````
#### 3. Install Necessary Modules
After activating the environment, install the required modules using:
````courseignore
pip install -r requirements.txt