import json
import asyncio
import httpx
import numpy as np


def fetch_config(config_file):
    with open(config_file) as file:
        config = json.load(file)
    return config['debug'], config['item_history_limit']


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


def create_history(items, client, limit, debug):
    if debug:
        print(f"Item history limit set to {limit}.")
    for item in items:
        item_id = item['id']
        response = client.get(f"https://ollie.fund/api/history/{item_id}")
        dates_checked = 0
        history = response.json()['history']
        raps = []
        for date, values in history.items():
            if dates_checked > limit:
                break
            if values['rap']:
                raps.append(values['rap'])
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
            rap_history = rap_history[(rap_history > np.quantile(rap_history, 0.08)) & (rap_history < np.quantile(rap_history, 0.5))].tolist()
            avg_rap = round(np.sum(rap_history) / np.size(rap_history))
            item['avgRAP'] = avg_rap
        else:
            print(f"No rap history for item {item['name']} ({item['id']})")
            continue
    return items


def avg_price_check(items):  # this check wont be super accurate until ollie.fund/api/history has kept item history for longer
    for item in items:
        if not item['projectedStatus']:
            avg_rap = item['avgRAP']
            current_price = item['price']
            price_rap_ratio = round(current_price / avg_rap, 2) * 100
            print(f"current_price ({current_price}) / avg_rap ({avg_rap}) = {price_rap_ratio}")
            if price_rap_ratio > 100.0:
                pct_over = price_rap_ratio - 100.0
                print(f"Current price is {pct_over}% over avg rap")
                if pct_over >= 30.0:
                    print("likely projected")
            else:
                print(f"Current price is {100 - price_rap_ratio}% below avg rap")
        else:
            print(f"{item['id']} has been marked as proj / inaccurate, skipping this item.")


def history_length_check(items):
    for item in items:
        if len(item['rapHistory']) < 15:
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
        self.limit = self.config[1]
        self.items = create_history(fetch_item_info(items, self.client, self.debug), self.client, self.limit, self.debug)

    def detect(self):
        items = self.items
        if self.debug:
            print(items)
        # projected algorithm goes here
        items = history_length_check(items)
        items = parse_history(items)
        avg_price_check(items)


async def main():
    head = {
        'user-agent': "hi ollie its marshall's proj detector"
    }
    async_client = httpx.AsyncClient(headers=head)
    client = httpx.Client(headers=head)
    detector = Detector([1028606, 1028720, 1029025, 1365767, 11297746, 1191129536], "proj_detector_config.json", async_client, client)
    detector.detect()


if __name__ == "__main__":
    asyncio.run(main())
