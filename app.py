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
        self.utility_one = [random.random() for i in users]
        self.utility_two = [random.random() for i in users]
        self.teams = []

        for user in self.users:
            if self.clusters[user] == 'a':
                self.G.nodes[user]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 0}}
            elif self.clusters[user] == 'b':
                self.G.nodes[user]['viz'] = {'color': {'r': 0, 'g': 255, 'b': 0, 'a': 0}}
            elif self.clusters[user] == 'c':
                self.G.nodes[user]['viz'] = {'color': {'r': 0, 'g': 0, 'b': 255, 'a': 0}}
            elif self.clusters[user] == 'd':
                self.G.nodes[user]['viz'] = {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 255}}
        
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
    
    def get_efficiency(self):
        path_lengths = 0
        paths = 0
        for c in nx.connected_components(self.G):
            subgraph = self.G.subgraph(c).copy()
            pairs = combinations(subgraph.nodes, 2)
            
            for p in pairs:
                for path in nx.all_simple_paths(self.G, source = p[0], target = p[1]):
                    path_lengths += len(path) - 1
                    paths += 1

        if paths == 0: return 0
        return path_lengths/paths

    def get_norm_efficiency(self):
        min_efficiency = 0
        for t in self.teams:
            min_efficiency += len(list(combinations(t, 2)))
        min_efficiency = min_efficiency/len(self.teams)

        max_efficiency = len(self.users) - 1
        return (self.get_efficiency())/(max_efficiency)
    
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
    
    def get_utility(self):
        f = 0
        for t in self.teams:
            count_one = 0
            count_two = 0
            for m in t:
                count_one += self.utility_one[m]          # Appends utility values
                count_two += self.utility_two[m]
            f += (count_one**2 + count_two**2)/(2*len(t))
        return f/len(self.teams)

    # Generates a random, valid swap move
    def valid_move(self):
        team_a, team_b = random.sample(self.teams, 2)
        return([random.choice(team_a), random.choice(team_b)])
    
    # Adds user to a team
    def add_user_to_team(self, user, team):
        team.append(user)
        for member in team:
            if (not (self.G.has_edge(user, member) or user == member)):
                self.G.add_weighted_edges_from([(user, member, np.random.normal(0.5))])
    
    def efficiency_tie_strength_obj_eq(self, alpha):
        return alpha*self.get_tie_strength() + (1-alpha)*self.get_efficiency()

    def efficiency_diversity_obj_eq(self, alpha=0.5):
        return alpha*self.get_norm_efficiency() + (1-alpha)*self.get_norm_diversity()
    
    def efficiency_diversity_utility_obj_eq(self, e_w=0.333, d_w=0.333, u_w=0.333):
        return e_w*self.get_norm_efficiency() + d_w*self.get_norm_diversity() + u_w*self.get_utility()

    # Swaps two users if they're in different teams
    def transform(self, user_a, user_b, e_w=0.333, d_w=0.333, u_w=0.333):      
        for t in self.teams:
            if user_a in t and user_b in t:
                return self.efficiency_diversity_utility_obj_eq(e_w, d_w, u_w)
            elif user_a in t:
                t.remove(user_a)
                self.add_user_to_team(user_b, t)
            elif user_b in t:
                t.remove(user_b)
                self.add_user_to_team(user_a, t)
        
        return self.efficiency_diversity_utility_obj_eq(e_w, d_w, u_w)

    def stochastic_search(self, eps=0.1, e_w=0.333, d_w=0.333, u_w=0.333):
        s_current = []
        nx.write_gexf(self.G, "start.gexf")
        diversity = [self.get_diversity()]
        efficiency = [self.get_efficiency()]
        utility = [self.get_utility()]
        for i in range(50):
            print(i)
            s_candidate = self.valid_move()

            G_prime = deepcopy(self)
            G_prime_transform = G_prime.transform(s_candidate[0], s_candidate[1], e_w, d_w, u_w)

            if (G_prime_transform > self.efficiency_diversity_utility_obj_eq(e_w, d_w, u_w)):
                s_current.append(s_candidate)
                self.transform(s_candidate[0], s_candidate[1], e_w, d_w, u_w)
                nx.write_gexf(self.G, "round " + str(i) + ".gexf")
            
            diversity.append(self.get_diversity())
            efficiency.append(self.get_efficiency())
            utility.append(self.get_utility())
            # if (random.random() < eps):
            #     return s_current
        print(diversity)
        print(efficiency)
        print(utility)

    
    def random_assignment(self):
        diversity = [self.get_diversity()]
        efficiency = [self.get_efficiency()]
        utility = [self.get_utility()]
        for i in range(50):
            if (random.choice([True, False])):
                move = self.valid_move()
                self.transform(move[0], move[1])
            diversity.append(self.get_diversity())
            efficiency.append(self.get_efficiency())
            utility.append(self.get_utility())
        print(diversity)
        print(efficiency)
        print(utility)

if __name__ == '__main__':
    network = networkGraph(list(range(50)))
    network.naive_group_assignment(10)

    network_copy = deepcopy(network)
    network_copy.random_assignment()
    network.stochastic_search()

    # nx.draw(network.G)