import networktables
from pathlib import Path
from logging import DEBUG, basicConfig, getLogger
from os import path, makedirs

fms = networktables.NetworkTables.getTable("FMSInfo")
match_type = fms.getEntry("MatchType")
match_number = fms.getEntry("MathNumber")

LOG_FILENAME = Path(
    __file__).parent.parent.resolve() / "logs" / "apriltag.log"
TIME_FORMAT = f"%y %a %b {match_type.getString('Test Match')} {match_number.getString('0')}"
LOG_FORMAT = "%(asctime)s - %(module)s - %(levelname)s - %(message)s"

if not path.exists(LOG_FILENAME.parent):
    makedirs(LOG_FILENAME.parent)

basicConfig(filename=LOG_FILENAME, level=DEBUG,
            format=LOG_FORMAT, datefmt=TIME_FORMAT)
logger = getLogger()
