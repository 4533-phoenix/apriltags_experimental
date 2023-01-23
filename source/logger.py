import networktables
import pathlib
import logging
import os


fms = networktables.NetworkTables.getTable("FMSInfo")
match_type = fms.getEntry("MatchType")
match_number = fms.getEntry("MathNumber")

LOG_FILENAME = pathlib.Path(
    __file__).parent.parent.resolve() / "logs" / "log.txt"
TIME_FORMAT = f"%y %a %b {match_type.getString('Test Match')} {match_number.getString('0')}"
LOG_FORMAT = "%(asctime)s - %(module)s - %(levelname)s - %(message)s"

if not os.path.exists(LOG_FILENAME.parent):
    os.makedirs(LOG_FILENAME.parent)

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=TIME_FORMAT)
logger = logging.getLogger()
