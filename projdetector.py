import json
import asyncio
import httpx
import numpy as np


def fetch_config(config_file):
    with open(config_file) as file:
        config = json.load(file)
    return config['debug'], config['minimum_days_of_history']


def fetch_item_info(items, client, debug):
    new_items = []
    for item_id in items:
        response = client.get(f"https://ollie.fund/api/item/{item_id}")
        item_data = response.json()

        if item_data['value']:
            value = int(item_data['value'])
        else:
            value = None
        if item_data['lowestPrice']:
            price = int(item_data['lowestPrice'])
        else:
            price = None

        item = {
            'id': int(item_data['id']),
            'name': item_data['name'],
            'acronym': item_data['acronym'],
            'rap': int(item_data['rap']),
            'value': value,
            'price': price
        }

        new_items.append(item)
    return new_items


def create_history(items, client, debug):
    for item in items:
        item_id = item['id']
        response = client.get(f"https://m2rsh.xyz/raphistory/{item_id}")
        dates_checked = 0
        history = response.json()
        raps = []
        for date, values in history.items():
            if values[1]:
                if values[1] != 0:
                    raps.append(values[1])
            else:
                break
            dates_checked += 1

        if not raps:
            print(f"No data for {item['name']} ({item_id}).")
        item['rapHistory'] = raps
        if debug:
            print(f"Dates checked for {item_id}: {dates_checked}")
    return items


def parse_history(items):
    for item in items:
        rap_history = item['rapHistory']
        if rap_history:
            rap_history = np.array(rap_history)
            rap_history = rap_history[(rap_history > np.quantile(rap_history, 0.30)) & (rap_history < np.quantile(rap_history, 0.8))].tolist()
            avg_rap = round(np.sum(rap_history) / np.size(rap_history))
            item['avgRAP'] = avg_rap
        else:
            print(f"No rap history for item {item['name']} ({item['id']})")
            continue
    return items


def avg_price_check(items, debug):  # this check is being worked on and seems pretty accurate as of now
    for item in items:
        if not item['projectedStatus']:
            avg_rap = item['avgRAP']
            current_price = item['price']
            price_rap_ratio = (current_price / avg_rap) * 100
            if debug:
                print(f"current_price ({current_price}) / avg_rap ({avg_rap}) = {price_rap_ratio}")
            if price_rap_ratio > 100.0:
                pct_over = round(price_rap_ratio - 100.0, 2)
                if debug:
                    print(f"Current price is {pct_over}% over avg rap")
                if pct_over >= 30.0 and current_price <= 1_000:
                    print(f"{item['id']} likely projected, setting projectedStatus to True")
                elif pct_over >= 40.0 and 1_000 < current_price <= 10_000:
                    print(f"{item['id']} likely projected, setting projectedStatus to True")
                    item['projectedStatus'] = True
                elif pct_over >= 50.0 and 10_000 < current_price <= 100_000:
                    print(f"{item['id']} likely projected, setting projectedStatus to True")
                    item['projectedStatus'] = True
                elif pct_over >= 60.0 and 100_000 < current_price <= 200_000:
                    print(f"{item['id']} likely projected, setting projectedStatus to True")
                    item['projectedStatus'] = True
                elif pct_over >= 70.0 and 200_000 < current_price:
                    print(f"{item['id']} likely projected, setting projectedStatus to True")
                    item['projectedStatus'] = True
            else:
                print(f"Current price is {round(100 - price_rap_ratio, 2)}% below avg rap")
        else:
            print(f"{item['id']} has been marked as proj / inaccurate, skipping this item.")
    return items


def history_length_check(items, minimum_days, debug):
    for item in items:
        if len(item['rapHistory']) < minimum_days:
            if debug:
                print(f"{item['id']} only has {len(item['rapHistory'])} days of RAP recorded. Data for this item will most likely be inaccurate.\nSetting projectedStatus to True so this item will not be further used.")
            item['projectedStatus'] = True
        else:
            item['projectedStatus'] = None
    return items


class Detector:
    def __init__(self, items, config_file_name, async_client, client):
        self.async_client = async_client
        self.client = client
        self.config = fetch_config(config_file_name)
        self.debug = bool(self.config[0])
        self.min_days = self.config[1]
        self.items = create_history(fetch_item_info(items, self.client, self.debug), self.client, self.debug)

    def detect(self):
        items = self.items
        items = history_length_check(items, self.min_days, self.debug)
        items = parse_history(items)
        avg_price_check(items, self.debug)
        if self.debug:
            print(items)
            print("Items that are likely not projected and / or have accurate data:")
            for item in items:
                if not item['projectedStatus']:
                    print(item)
        return items


# async def main():
#     # head = {
#     #     'user-agent': "hi ollie its marshall's proj detector"
#     # }
#     # async_client = httpx.AsyncClient(headers=head)
#     # client = httpx.Client(headers=head)
#     # detector = Detector([1028606, 1029025, 1365767, 11297746, 138932314, 1125510, 19043710, 37819478, 6807134749], "proj_detector_config.json", async_client, client)
#     # final_items = detector.detect()
#     # print(json.dumps(final_items, indent=4))
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
