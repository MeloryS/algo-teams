import json
import os
import requests
import random
import string
import numpy as np
import networkx as nx
import config
import statistics
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
            name = self.random_string()
        #     self.create_channel(name, group)

        return split_user_arrays

# Network efficiency: average path length between two nodes in the collaboration graph
def get_efficiency(graph):
    path_lengths = []
    for c in nx.connected_components(graph):
        path_lengths.append(nx.average_shortest_path_length(graph.subgraph(c).copy()))
    return statistics.mean(path_lengths)
    
# Tie strength: average edge weight between people who are in the same team
def get_tie_strength(graph, teams):
    edge_weights = []
    for t in teams:
        pairs = combinations(t, 2)
        for p in pairs:
            edge_weights.append(graph[p[0]][p[1]]['weight'])
    return statistics.mean(edge_weights)

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

    # Creates a random, valid move
    def valid_move(self):
        teams_copy = self.teams.copy()
        random_team = random.choice(self.teams)
        random_user = random.choice(random_team)
        teams_copy.remove(random_team)
        new_team = random.choice(teams_copy)
        return([random_user, new_team])

    # Moves a user to another team
    def transform(self, user, team):
        G_copy = self.G.copy()
        teams_copy = self.teams
        # Update teams array
        for t in teams_copy:
            if user in t: 
                t.remove(user)
            elif t == team:
                t.append(user)

        # Update graph
        for member in team:
            if (not (G_copy.has_edge(user, member) or  user == member)):
                G_copy.add_weighted_edges_from([(user, member, 1)])
        
        return (G_copy, teams_copy)

    def stochastic_search(self):
        s_current = []
        return

if __name__ == '__main__':
    network = networkGraph([str(x) for x in list(range(10))])
    network.naive_group_assignment(5)
    # print(network.G.edges)
    # print(network.teams)
    # print (network.G.edges)
    # print (network.teams)
    random_move = network.valid_move()
    print (random_move)
    transform = network.transform(random_move[0], random_move[1])
    print (transform[0].edges)
    # api.naiveGroupAssignment(1, ["U0159QC3QDB", "U015CKGB5GD"])