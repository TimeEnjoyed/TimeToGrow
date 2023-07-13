# TimeToGrow 
### CodeJam Entry

Description here...


#### Installing
TimeToGrow requires **Python3.11**. **Note:** *This has not been tested on Python 3.12+.*

Download the latest [Python](https://www.python.org/downloads/)


**Windows**

In a terminal:

```shell
git clone https://github.com/TimeEnjoyed/TimeToGrow.git
cd TimeToGrow
py -3.11 -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```


**Linux/MacOS**

In a terminal:

```shell
git clone https://github.com/TimeEnjoyed/TimeToGrow.git
cd TimeToGrow
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


#### Running
After installation, in your activated venv:

```shell
python launcher.py
```


#### Development
To set up a development environment follow the steps in [Installing](#installing), then run:

```shell
pip install -r dev-requirements.txt
```

TimeToGrow uses Black and isort for linting.

After installation and before committing run:
```shell
black .
isort .
```

To check for typing errors, run:
```shell
pyright
```
