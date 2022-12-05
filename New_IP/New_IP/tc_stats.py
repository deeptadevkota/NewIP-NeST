import os
import time
import json
import re
import matplotlib.pyplot as plt


class tc_stats:
    def __init__(self, node, interface, duration, FOLDER=""):
        self.FOLDER = FOLDER
        if self.FOLDER != "":
            self.FOLDER = self.FOLDER + "/tc-stats"
        else:
            self.FOLDER = "../tc-stats"
        self.FOLDER = self.make_folder(self.FOLDER, True)
        self.get_raw_stats_tc(interface, duration)
        aggregate_stats, handle = self.parse_raw_stats()
        self.FOLDER = self.FOLDER + f"/{node}-{interface}"
        self.FOLDER = self.make_folder(self.FOLDER, False)

        self._plot_tc_stats(self.FOLDER, aggregate_stats[handle], node, interface)

    def make_folder(self, exp_name, add_timestamp=True):
        if add_timestamp:
            timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
            FOLDER = f"{exp_name}({timestamp})_dump"
        else:
            FOLDER = exp_name
        if not os.path.isdir(FOLDER):
            os.mkdir(FOLDER)
        return FOLDER

    def dump_plot(self, FOLDER, subfolder, filename, fig):
        path = os.path.join(FOLDER, filename)
        fig.savefig(path)

    def simple_plot(self, title, x_list, y_list, x_label, y_label, legend_string=None):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x_list, y_list)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        if legend_string is not None:
            ax.legend([legend_string])

        return fig

    def _extract_from_tc_stats(self, stats, node, interface):

        qdisc = stats[0]["kind"]
        start_time = float(stats[0]["timestamp"])

        timestamp = []
        stats_params = {}

        for param in stats[0]:
            if param not in ("timestamp", "kind"):
                stats_params[param] = []

        for data in stats:
            for param, param_data in stats_params.items():
                param_data.append(data[param])
            relative_time = float(data["timestamp"]) - start_time
            timestamp.append(relative_time)

        return (qdisc, timestamp, stats_params)

    def _plot_tc_stats(self, FOLDER, stats, node, interface):
        values = self._extract_from_tc_stats(stats, node, interface)
        if values is None:
            return
        (qdisc, timestamp, stats_params) = values

        for param in stats_params:
            fig = self.simple_plot(
                "Traffic Control (tc) Statistics",
                timestamp,
                stats_params[param],
                "Time (Seconds)",
                param,
                legend_string=f"Interface {interface} in {node}",
            )
            filename = f"{node}_{interface}_{qdisc}_{param}.png"
            self.dump_plot(FOLDER, "tc", filename, fig)
            plt.close(fig)

    def get_raw_stats_tc(self, interface, duration):
        comm = f"timeout {duration} bash ../extras/tc.sh {interface} {duration}  >> '{self.FOLDER}/output.json' 2>&1"
        os.system(comm)
        time.sleep(duration)

    def parse_raw_stats(self):
        with open(f"{self.FOLDER}/output.json") as f:
            stats = str(f.readlines()).split("---")
            f.seek(0)
            raw_stats = f.read().split("---")
        f.close()
        aggregate_stats = {}
        for raw_stat in raw_stats[:-1]:
            timestamp_pattern = r"timestamp:(?P<timestamp>\d+\.\d+)"
            timestamp = re.search(timestamp_pattern, raw_stat).group("timestamp")
            raw_stat = re.sub(timestamp_pattern, "", raw_stat)
            raw_stat = json.loads(raw_stat)
            stats_dict = {}
            for qdisc_stat in raw_stat:
                qdisc = qdisc_stat["kind"]
                if qdisc != "ingress":  # To ignore the ingress tc qdisc
                    handle = qdisc_stat["handle"]
                    if handle not in aggregate_stats:
                        aggregate_stats[handle] = []

                    stats_dict["timestamp"] = str(timestamp)
                    stats_dict.update(qdisc_stat)
                    stats_dict.pop("handle", None)
                    stats_dict.pop("options", None)
                    stats_dict.pop("parent", None)
                    aggregate_stats[handle].append(stats_dict)
        return aggregate_stats, handle
