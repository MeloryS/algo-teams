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
from copy import deepcopy

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
    def add_user(self, user, channel):
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
    def remove_user(self, user, channel):
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
    
    # Network efficiency: average path length between two nodes in the graph
    def get_efficiency(self):
        path_lengths = []
        for c in nx.connected_components(self.G):
            path_lengths.append(nx.average_shortest_path_length(self.G.subgraph(c).copy()))
        return statistics.mean(path_lengths)
    
    # Tie strength: average edge weight between people who are in the same team
    def get_tie_strength(self):
        try:
            edge_weights = []
            for t in self.teams:
                pairs = combinations(t, 2)
                for p in pairs:
                    edge_weights.append(self.G[p[0]][p[1]]['weight'])
            return statistics.mean(edge_weights)
        except (KeyError):
            return ('p[0]: {}, p[1]: {}'.format(p[0], p[1]))

    # Generates a random, valid swap move
    def valid_move(self):
        team_a, team_b = random.sample(self.teams, 2)
        return([random.choice(team_a), random.choice(team_b)])
    
    # Adds user to a team
    def add_user_to_team(self, user, team):
        team.append(user)
        for member in team:
            if (not (self.G.has_edge(user, member) or user == member)):
                self.G.add_weighted_edges_from([(user, member, 1)])

    # Swaps two users if they're in different teams
    def transform(self, user_a, user_b, alpha):      
        for t in self.teams:
            if user_a in t and user_b in t:
                return alpha*self.get_tie_strength() + (1-alpha)*self.get_efficiency()
            elif user_a in t:
                t.remove(user_a)
                self.add_user_to_team(user_b, t)
            elif user_b in t:
                t.remove(user_b)
                self.add_user_to_team(user_a, t)
    
        return alpha*self.get_tie_strength() + (1-alpha)*self.get_efficiency()

    def stochastic_search(self, eps, alpha=0.5):
        s_current = []
        G_current = deepcopy(self)
        while True:
            s_candidate = G_current.valid_move()
            s_current.append(s_candidate)

            G_prime = deepcopy(self)
            G_prime_transform = G_prime.transform(s_candidate[0], s_candidate[1], alpha)

            G_current_transform = G_current.transform(s_candidate[0], s_candidate[1], alpha)
            if (G_prime_transform > G_current_transform):
                s_current = [s_candidate]
                print (G_prime_transform, G_current_transform)

            if (random.random() < eps):
                return s_current

if __name__ == '__main__':
    network = networkGraph([str(x) for x in list(range(20))])
    network.naive_group_assignment(5)
    print (network.stochastic_search(0.0005))