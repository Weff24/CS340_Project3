from simulator.node import Node
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dvs = {}
        self.links = {}
        self.neighboring_dvs = {} 
        self.neighboring_seq_nums = {}
        self.seq_num = 0

    # Return a string
    def __str__(self):
        return "Node " + str(self.id)

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
            del self.neighboring_dvs[neighbor]
            del self.neighboring_seq_nums[neighbor]
            del self.links[neighbor]
                
        else: 
            self.neighbors.append(neighbor)
            self.links[neighbor] = latency
            
        # Update node's distance vector links
        self.dvs = {}
        for (n, cost) in self.links.items():
            self.dvs[n] = {
                "cost": cost,
                "path": [self.id, n]
            }

        # Update distance vectors based on neighbors and send updated distance vector to neighbors
        self.update_dv()
        self.send_to_neighbors(json.dumps(self.get_message()))

    #  Update distance vectors of current node based on known neighboring distance vectors
    def update_dv(self):
        # Update node sequence number
        self.seq_num += 1
        for (n, neighbor_dv) in self.neighboring_dvs.items():
            if n in self.links:
                for (destination, val) in neighbor_dv.items():
                    # Check for potential loops or removed links
                    if destination == self.id or self.id in val["path"] or val["cost"] <= 0:
                        continue

                    # Update distance vector based on cost
                    if (destination not in self.dvs.keys()) or ((destination in self.dvs.keys()) and (self.links[n] + val["cost"] < self.dvs[destination]["cost"])):
                        new_path = val["path"].copy()
                        new_path.insert(0, self.id)
                        self.dvs[destination] = {
                            "cost": self.links[n] + val["cost"],
                            "path": new_path
                        }

    # Get the json of the message that is sent to neighbors
    def get_message(self):
        message = {
            self.id: {},
            "seq_num": self.seq_num
        }
        for (key, val) in self.dvs.items():
            message[self.id][str(key)] = val
        return message

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # Make a copy of node's distance vectors to check for changes
        prev_dvs = self.dvs.copy()

        # Load message
        neighboring_dv = json.loads(m)
        neighbor = int(list(neighboring_dv.keys())[0])
        seq_num = neighboring_dv["seq_num"]

        # Check if this message is new
        if (neighbor not in self.neighboring_dvs.keys()) or (seq_num > self.neighboring_seq_nums[neighbor]):
            parsed_neighboring_dvs = {
                int(key):val for (key, val) in neighboring_dv[str(neighbor)].items()
            } 
            self.neighboring_dvs[neighbor] = parsed_neighboring_dvs
            self.neighboring_seq_nums[neighbor] = seq_num

            # Update node's distance vector
            self.dvs = {}
            for (n, cost) in self.links.items():
                self.dvs[n] = {
                    "cost": cost,
                    "path": [self.id, n]
                }
            self.update_dv()
            
            # Send distance vector to neighbors if there was a change
            if self.dvs != prev_dvs:
                self.send_to_neighbors(json.dumps(self.get_message()))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # Get the next node in the path
        if destination in self.dvs.keys():
            return self.dvs[destination]["path"][1]
        return -1
