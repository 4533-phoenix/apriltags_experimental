from config import load_config
from shared_memory_dict import SharedMemoryDict
from time import sleep
from  numpy import array
import ntcore

CONFIG = load_config("config")

class NetworkTable:
    NO_DATA = array([-2])

    def __init__(self, solved_position: SharedMemoryDict) -> None:
        """Initialize the network table class."""
        self.solved_position = solved_position

        self.config = CONFIG["networktables"]

        self.instance = ntcore.NetworkTableInstance.getDefault()
        self.table = self.instance.getTable(self.config["table"])

        self.position_pub = self.table.getDoubleArrayTopic("position").publish()
        self.rotation_pub = self.table.getDoubleArrayTopic("rotation").publish()
        self.transformation_pub = self.table.getDoubleArrayTopic("transformation").publish()

    def run(self) -> None:
        """Run the network table."""
        while True:
            self.position_pub.set(self.solved_position.get("position", NetworkTable.NO_DATA).flatten().tolist())
            self.rotation_pub.set(self.solved_position.get("rotation", NetworkTable.NO_DATA).flatten().tolist())
            self.transformation_pub.set(self.solved_position.get("transformation", NetworkTable.NO_DATA).flatten().tolist())

            sleep(self.config["update_rate"])

def start_networktable_process(solved_position: SharedMemoryDict) -> None:
    """Start the network table process."""
    network_table = NetworkTable(solved_position)
    network_table.run()