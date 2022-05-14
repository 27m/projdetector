# projDetector

A lightweight module for detecting projecteds.

Takes item ids and returns the following information:

id, name, acronym, value, RAP, lowestPrice, projectedStatus, avgRAP (since 2021)

## Instantiating a detector and detecting projecteds

```
from projdetector import Detector

detector = Detector([list_of_ids], "config_file_name", async_client_instance, sync_client_instance)

items = detector.detect() -- returns list of items each item being a dict with their respective information
```

There is also an example in main() of projdetector.py

## Configuration

```
{
"debug": 0, -- 1 for true, 0 for false (prints info that will be helpful for debugging errors when you bring them to me)
"minimum_days_of_history": 30 -- minimum days of rap history needed for an item to be considered 'accurate' (non accurate items are marked as projected)
}
```


## NOTICE

This module is meant for other developers to use as a projected check, but ideally should not be used alone and is not guaranteed to catch every projected.
When used with a do not trade for list that blocks out most smalls like gucci and other highly fluctuating items, it should catch most projecteds if not nearly all.

## DISCLAIMER

I am not responsible for your use of this module and any false positives or false negatives that may occur. I am still working on this detector and as such it will improve.
