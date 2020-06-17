import json
import os
import requests
import random
import string
import numpy as np

import config

class algoTeamsAPI:
    def __init__(self):
        self.URL = "https://slack.com/api/"
        self.token = config.token
        self.headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(config.token)}

    def createChannel(self, channel_name, users):
        """Create a new Channel with given users"""        
        # Create a new channel
        response = requests.post(
            url=self.URL + "conversations.create",
            data=json.dumps({
                "name": channel_name,
                "is_private": True
            }),
            headers=self.headers
        )

        response_json = response.json()
        print(response_json)

        # Invite users to channel
        requests.post(
            url=self.URL + "conversations.invite",
            data=json.dumps({
                "channel": response_json["channel"]["id"],
                "users": users
            }),
            headers=self.headers
        )

        # Send welcome message
        requests.post(
            url=self.URL+"/chat.postMessage",
            data=json.dumps({
                "channel": response_json["channel"]["id"],
                "text": "Hello there!"
            }),
            headers=self.headers
        )
        return(response_json)
    
    def addUser(self, channel, user):
        """Invite user to given channel"""

        response = requests.post(
            url=self.url+"/conversations.invite",
            data=json.dumps({
                "channel": channel,
                "user": user
            })
        )
        response_json = response.json()
        return (response_json["ok"])
    
    def removeUser(self, channel, user):
        """Remove user from given channel"""
        response = requests.post(
            url=self.url+"/conversations.kick",
            data=json.dumps({
                "channel": channel,
                "user": user
            })
        )
        response_json = response.json()
        return (response_json["ok"])
    
    def randomString(self, stringLength=8):
        """Generates a random string for channel naming"""
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(stringLength))
    
    def naiveGroupAssignment(self, num_channel, users):
        """Splits users into num_channel channels"""
        # Separate users into num_channel arrays
        users = random.shuffle(users)
        split_user_arrays = [group.tolist() for group in np.array_split(users, num_channel)]
        user_arrays = [', '.join(group) for group in split_user_arrays]

        for group in user_arrays:
            name = self.randomString()
            self.createChannel(name, group)
        
if __name__ == '__main__':
    api = algoTeamsAPI()
