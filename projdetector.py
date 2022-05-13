import json
import asyncio
import httpx as httpx


def fetch_config(config_file):
    with open(config_file) as file:
        config = json.load(file)
    return config['debug'], config['item_history_limit']


def fetch_item_info(items, client):
    new_items = []
    for item_id in items:
        response = client.get(f"https://ollie.fund/api/item/{item_id}")
        item_data = response.json()
        item = {
            'id': item_data['id'],
            'name': item_data['name'],
            'acronym': item_data['acronym'],
            'rap': item_data['rap'],
            'value': item_data['value']
        }
        new_items.append(item)
    return new_items


def parse_history(items, client, limit):
    print(limit)
    for item in items:
        item_id = item['id']
        response = client.get(f"https://ollie.fund/api/history/{item_id}")
        dates_checked = 0
        history = response.json()['history']
        raps = []
        for date, values in history.items():
            if dates_checked <= limit:
                if values['rap']:
                    raps.append(values['rap'])
                else:
                    break
                dates_checked += 1
            else:
                break

        if not raps:
            print(f"No data for item {item_id}")
            raps = None
        item['rapHistory'] = raps
    return items


class Detector:
    def __init__(self, items, config_file, async_client, client):
        self.async_client = client
        self.client = client
        self.config = fetch_config(config_file)
        self.debug = self.config[0]
        self.limit = self.config[1]
        self.items = parse_history(fetch_item_info(items, self.client), self.client, self.limit)

    def detect(self):
        items = self.items
        print(items)
        # projected algorithm goes here


async def main():
    async_client = httpx.AsyncClient()
    client = httpx.Client()
    detector = Detector([1028606, 1028720, 1029025], "config.json", async_client, client)
    detector.detect()


if __name__ == "__main__":
    asyncio.run(main())
