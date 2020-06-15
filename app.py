import json
import os
import requests
import numpy as np

import config

class algoTeamsAPI:
    def __init__(self):
        self.URL = "https://slack.com/api/"
        self.token = config.token
        self.headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(config.token)}

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
    
    def naiveGroupAssignment(self, num_channel, users):
        """Splits users into num_channel channels"""
        split_user_arrays = [x.tolist() for x in np.array_split(users, num_channel)]
        return(split_user_arrays)

if __name__ == '__main__':
    api = algoTeamsAPI()
    # cc = api.createChannel("testcreatechannel", "U0159QC3QDB, U015CKGB5GD")
    print(api.naiveGroupAssignment(3, [1, 2, 3]))
