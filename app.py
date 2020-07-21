import json
import os
import requests
import random
import string
import numpy as np
import networkx as nx
import math
import config
import statistics
import matplotlib.pyplot as plt
from itertools import combinations, permutations
from copy import deepcopy

class algoTeamsAPI:
    def __init__(self, network):
        self.URL = "https://slack.com/api/"
        self.token = config.token
        self.headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(config.token)}
        self.network = network

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
    def naive_group_assignment(self, num_channel):
        network.naive_group_assignment(num_channel)
        user_arrays = [', '.join(group) for group in network.teams]

        for group in user_arrays:
            name = self.random_string()
        #     self.create_channel(name, group)

        return split_user_arrays

class networkGraph:
    def __init__(self, users):
        self.G = nx.Graph() # Network graph representation
        # self.B = nx.Graph()
        self.G.add_nodes_from(users)
        self.users = users
        self.clusters = [random.choice(['a', 'b', 'c', 'd']) for i in users]
        self.teams = []
        
    def naive_group_assignment(self, num_channel):
        random.shuffle(self.users)
        self.teams = [group.tolist() for group in np.array_split(self.users, num_channel)]
        for i in range(num_channel):
            t = self.teams[i]
            pairs = combinations(t, 2)
            
            for p in pairs:
                self.G.add_weighted_edges_from([(p[0], p[1], np.random.normal(0.5))])
            
            # self.B.add_node('TEAM ' + str(i))
            # for member in t:
            #     self.B.add_weighted_edges_from([(member, 'TEAM ' + str(i), 1)])

        return self.teams
    
    # Network efficiency: average path length between two nodes in the graph
    # def get_efficiency(self):
    #     path_lengths = 0
    #     paths = 0
    #     for c in nx.connected_components(self.G):
    #         subgraph = self.G.subgraph(c).copy()
    #         path_lengths += nx.average_shortest_path_length(subgraph)*(math.comb(subgraph.number_of_nodes(), 2))
    #         paths += math.comb(subgraph.number_of_nodes(), 2)
    #     if paths == 0: return 0
    #     return path_lengths/paths

    def get_efficiency(self):
        path_lengths = 0
        paths = 0
        for c in nx.connected_components(self.G):
            subgraph = self.G.subgraph(c).copy()
            pairs = combinations(subgraph.nodes, 2)
            
            for p in pairs:
                for path in nx.all_simple_paths(self.G, source = p[0], target = p[1]):
                    path_lengths += len(path) - 1
                    # print (len(path) - 1)
                    paths += 1

        if paths == 0: return 0
        return path_lengths/paths

    def get_norm_efficiency(self):
        min_efficiency = 0
        for t in self.teams:
            min_efficiency += len(nx.all_simple_paths)
        min_efficiency = min_efficiency/len(self.teams)

        max_efficiency = len(self.users) - 1
        # return (self.get_efficiency()-min_efficiency)/max_efficiency
        return min_efficiency
    
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
    
    def get_diversity(self):
        f = 0
        for t in self.teams:
            count = dict()
            for m in t:
                membership = self.clusters[m]       # Checks which group the member is in
                if membership in count:
                    count[membership] += 1          # Appends 1 if count exists
                else:
                    count[membership] = 1           # Starts count otherwise
            for c in count:
                f += (count[c])**2
        return f
    
    def get_norm_diversity(self):
        min_diversity = len(self.users)
        max_diversity = len(self.users)**2
        return 1-(self.get_diversity()-min_diversity)/(max_diversity-min_diversity)

    def get_team_diversity(self):
        diverse_teams = []
        for t in self.teams:
            team = [self.clusters[i] for i in t]
            diverse_teams.append(team)
        return diverse_teams

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
    
    def efficiency_tie_strength_obj_eq(self, alpha):
        return alpha*self.get_tie_strength() + (1-alpha)*self.get_efficiency()

    # Swaps two users if they're in different teams
    def transform(self, user_a, user_b, alpha):      
        for t in self.teams:
            if user_a in t and user_b in t:
                # return -self.get_diversity() + self.get_efficiency()*len(self.users)
                return self.get_norm_diversity()
            elif user_a in t:
                t.remove(user_a)
                self.add_user_to_team(user_b, t)
            elif user_b in t:
                t.remove(user_b)
                self.add_user_to_team(user_a, t)
        
        return self.get_norm_diversity()
        # return -self.get_diversity()

    def stochastic_search(self, eps, alpha=0.5):
        s_current = []
        while True:
            s_candidate = self.valid_move()

            G_prime = deepcopy(self)
            G_prime_transform = G_prime.transform(s_candidate[0], s_candidate[1], alpha)

            if (G_prime_transform > self.get_norm_diversity()):
                s_current.append(s_candidate)
                self.transform(s_candidate[0], s_candidate[1], alpha)

            if (random.random() < eps):
                return s_current

if __name__ == '__main__':
    network = networkGraph(list(range(12)))
    network.naive_group_assignment(4)

    # print(network.get_efficiency())
    print(network.get_norm_diversity())
    print(network.get_diversity())
    network.stochastic_search(0.05)
    print(network.get_norm_diversity())
    print(network.get_diversity())
    # print(network.get_efficiency())

    # nx.draw(network.G)
    # plt.show()