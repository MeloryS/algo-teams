import json
import os
import requests
import random
import string
import numpy as np
import networkx as nx
import config
from itertools import combinations

class algoTeamsAPI:
    def __init__(self):
        self.URL = "https://slack.com/api/"
        self.token = config.token
        self.headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(config.token)}

    # Create a new Channel with given users
    def create_channel(self, channel_name, users):
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
    
    # Invite user to given channel
    def add_user(self, channel, user):
        response = requests.post(
            url=self.url+"/conversations.invite",
            data=json.dumps({
                "channel": channel,
                "user": user
            })
        )
        response_json = response.json()
        return (response_json["ok"])

    # Remove user from given channel
    def remove_user(self, channel, user):
        response = requests.post(
            url=self.url+"/conversations.kick",
            data=json.dumps({
                "channel": channel,
                "user": user
            })
        )
        response_json = response.json()
        return (response_json["ok"])
    
    # Generates a random string for channel naming
    def random_string(self, string_length=8):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(string_length))
    
    # Splits users into num_channel channels
    def naive_group_assignment(self, num_channel, users):
        random.shuffle(users)
        split_user_arrays = [group.tolist() for group in np.array_split(users, num_channel)]
        user_arrays = [', '.join(group) for group in split_user_arrays]

        for group in user_arrays:
            name = self.randomString()
            self.create_channel(name, group)

        return split_user_arrays

class networkGraph:
    def __init__(self, users):
        self.G = nx.Graph()
        self.G.add_nodes_from(users)
        self.users = users
        self.teams = []
        self.api = algoTeamsAPI()
        
    def naive_group_assignment(self, num_channel):
        self.teams = self.api.naive_group_assignment(num_channel, self.users)
        for t in self.teams:
            pairs = combinations(t, 2)
            for p in pairs:
                self.G.add_weighted_edges_from([(p[0], p[1], 1)])

    # Network efficiency: average path length between two nodes in the collaboration graph
    def get_efficiency(self):
        return
    
    # Tie strength: average edge weight between people who are in the same team
    def get_tie_strength(self):
        return

if __name__ == '__main__':
    network = networkGraph([str(x) for x in list(range(20))])
    network.naive_group_assignment(5)
    print(network.G.edges)
    print(network.teams)
    # api.naiveGroupAssignment(1, ["U0159QC3QDB", "U015CKGB5GD"])