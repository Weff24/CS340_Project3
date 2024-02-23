from simulator.node import Node
import json


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.links = {}

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
        else: 
            self.neighbors.append(neighbor)
            # self.send_to_neighbors("hello")
            # self.send_to_neighbor(neighbor, "hello")
        
        seq_num = 0
        if frozenset((self.id, neighbor)) in self.links.keys():
            seq_num = self.links[frozenset((self.id, neighbor))]["seq_num"] + 1

        self.links[frozenset((self.id, neighbor))] = {
            # "src": id,
            # "dest": neighbor,
            "seq_num": seq_num,
            "cost": latency
        }

        self.send_to_neighbors(json.dumps(self.get_message()))

        self.logging.debug('link update, neighbor %d, latency %d, time %d' % (neighbor, latency, self.get_time()))

    def get_message(self):
        message = {}
        for (key, val) in self.links.items():
            # if key[0] == self.id:
            #     message[str((key[1], key[0]))] = val
            # else:
            #     message[str(key)] = val
            message[str(tuple(key))[1:-1]] = val
        return message

    # Fill in this function
    def process_incoming_routing_message(self, m):
        message_links = json.loads(m)
        change_occurred = False

        for (key, val) in message_links.items():
            parsed_key = frozenset(tuple(map(int, key.split(', '))))
            if parsed_key in self.links.keys():
                if val["seq_num"] > self.links[parsed_key]["seq_num"]:
                    self.links[parsed_key] = val
                    change_occurred = True
            else:
                self.links[parsed_key] = val
                change_occurred = True

        
        if change_occurred:
            self.send_to_neighbors(json.dumps(self.get_message()))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # distances maps from node id to cost to get the specific node
        distances = {
            self.id: 0
        }
        queue = [{
            "id": self.id,
            "cost": 0,
            "next": self.id 
        }]

        while queue:
            node = queue.pop(0)

            if node["id"] == destination:
                return node["next"]

            for (key, val) in self.links.items():
                if (val["cost"] > 0) and (node["id"] in key):
                    neighbor = tuple(key)[1] if tuple(key)[0] == node["id"] else tuple(key)[0]
                    
                    new_cost = node["cost"] + val["cost"] 
                    if (neighbor not in distances) or (new_cost < distances[neighbor]):
                        distances[neighbor] = new_cost
                        queue.append({
                            "id": neighbor,
                            "cost": new_cost,
                            "next": neighbor if self.id == node["id"] else node["next"]
                        })
            queue.sort(key=lambda x: x["cost"])

        return -1
