from simulator.node import Node
import json
import copy


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
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)

            # if neighbor in self.neighboring_dvs:
            del self.neighboring_dvs[neighbor]
            del self.neighboring_seq_nums[neighbor]
            del self.links[neighbor]
                
        else: 
            self.neighbors.append(neighbor)
        
            self.links[neighbor] = latency
        # self.update_dv()


        # prev_dvs = copy.deepcopy(self.dvs)
        # seq_num = 0
        # if neighbor in self.dvs.keys():
        #     seq_num = self.dvs[neighbor]["seq_num"] + 1

        # self.dvs[neighbor] = {
        #     # "seq_num": seq_num,
        #     "cost": latency,
        #     "path": [neighbor]
        # }

        # self.update_dv()

        # for (n, neighbor_dv) in self.neighboring_dvs.items():
        #     self.update_dv(n, neighbor_dv)
        self.dvs = {}
        for (n, cost) in self.links.items():
            self.dvs[n] = {
                "cost": cost,
                "path": [self.id, n]
            }

        self.update_dv()
        self.send_to_neighbors(json.dumps(self.get_message()))

        
    def update_dv(self):
        self.seq_num += 1
        # print(self.neighboring_dvs)
        # print(self.links)
        for (n, neighbor_dv) in self.neighboring_dvs.items():
            for (destination, val) in neighbor_dv.items():
                if destination == self.id or self.id in val["path"] or val["cost"] <= 0 or n not in self.links:
                    continue

                if (destination not in self.dvs.keys()) or ((destination in self.dvs.keys()) and (self.links[n] + val["cost"] < self.dvs[destination]["cost"])):
                    new_path = copy.deepcopy(val["path"])
                    new_path.insert(0, self.id)
                    self.dvs[destination] = {
                        "cost": self.links[n] + val["cost"],
                        "path": new_path
                    }


    def get_message(self):
        message = {
            self.id: {},
            "seq_num": self.seq_num
        }
        for (key, val) in self.dvs.items():
            message[self.id][str(key)] = copy.deepcopy(val)
        return message

    # Fill in this function
    def process_incoming_routing_message(self, m):
        prev_dvs = copy.deepcopy(self.dvs)
        neighboring_dv = json.loads(m)
        neighbor = int(list(neighboring_dv.keys())[0])
        seq_num = neighboring_dv["seq_num"]

        # change_occurred = False

        if (neighbor not in self.neighboring_dvs.keys()) or (seq_num > self.neighboring_seq_nums[neighbor]):
            parsed_neighboring_dvs = {
                int(key):val for (key, val) in neighboring_dv[str(neighbor)].items()
            } 
            self.neighboring_dvs[neighbor] = parsed_neighboring_dvs
            self.neighboring_seq_nums[neighbor] = seq_num

            # self.links[neighbor] = parsed_neighboring_dvs[self.id]
            # print(parsed_neighboring_dvs)

            self.dvs = {}
            for (n, cost) in self.links.items():
                self.dvs[n] = {
                    "cost": cost,
                    "path": [self.id, n]
                }
            
            self.update_dv()
            # print("HIHIHIHIH")
            # print(neighbor)
            # print(self.id)
            # print(self.dvs)
            
            if self.dvs != prev_dvs:
                self.send_to_neighbors(json.dumps(self.get_message()))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # print("DVSSSSS")
        # print(self.dvs)
        if destination in self.dvs.keys():
            return self.dvs[destination]["path"][1]
        return -1
