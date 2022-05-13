# projdetector

## temporary README: 

a lightweight module for detecting projecteds

input will just be item ids, will return the following info for each item id:

id, name, acronym, value, RAP, lowestPrice, projectedStatus, projPercentage

## instantiating a detector

example in main() of projdetector.py

from projdetector import Detector

detector = Detector([list_of_ids], "config_file_name", async_client_instance, sync_client_instance)