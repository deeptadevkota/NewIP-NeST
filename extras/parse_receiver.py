import matplotlib.pyplot as plt


class parse_receiver:
    def __init__(self, file_path):
        if "../test_results/" in file_path:
            file_path = file_path.split("../test_results/")[1]
        self.file_path = file_path
        if "/" in self.file_path:
            self.folder = self.file_path.split("/")[0]
            self.file_name = self.file_path.split("/")[1]
        else:
            self.folder = "../test_results/"
            self.file_name = self.file_path
        self.jitter = []

    def read_receiver_file(self):
        f = open(f"../test_results/{self.file_path}")
        lines = f.readlines()
        f.close()
        for line in lines:
            if ":lbf [" in line:
                del_exp = (
                    int(line.split(":lbf [")[1].split(",")[2].split("]\n")[0]) * 0.1
                )
                min_del = int(line.split(":lbf [")[1].split(",")[0])
                # print(del_exp)
                # print(round(del_exp - min_del,4))
                self.jitter.append(round(del_exp - min_del, 4))

    def dump_jitter(self):
        # self.parsed_file_path = f'{self.folder}/parsed_{self.file_name}'
        f = open(f"../test_results/{self.folder}/parsed_{self.file_name}", "w")
        pkt_number = 0
        for value in self.jitter:
            f.write(f"{pkt_number} {value}")
            f.write("\n")
            pkt_number += 1
        f.close()

    def plot(self):
        self.pkt_number = []
        for i in range(0, len(self.jitter)):
            self.pkt_number.append(i)
        plt.plot(self.pkt_number, self.jitter)
        plt.xlabel("Received Order Packet Number")
        plt.ylabel("Jitter (ms)")
        # plt.show()
        plt.savefig(f"../test_results/{self.folder}/jitter_{self.file_name}.jpg")


# parse = parse_receiver('../test_results/Test1/receiver_stats_20-10-2022-00:00:03.txt')
# parse.read_receiver_file()
# parse.plot()
