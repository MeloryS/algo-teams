# Algorithm-Driven Virtual Teams
Studying how to create effective virtual teams with the help of machine learning algorithms

## Local Setup 
1. Install dependencies by running following command:
```
pip install requirements.txt
```
2. [Create a new Slack app for your workspace](https://api.slack.com/apps)
3. Add the token for your app to config.py with the following OAuth scopes enabled:
```
channels:manage, channels:read, chat:write, groups:read, groups:write
```
4. Run the file
```
python3 app.py
```
