import json
import asyncio
import httpx as httpx


def fetch_config(config_file):
    with open(config_file) as file:
        config = json.load(file)
    return config['debug'], config['test_value']


def fetch_item_info(items, client):
    new_items = []
    for item_id in items:
        response = client.get(f"https://ollie.fund/api/item/{item_id}")
        new_items.append(response.json())
    return new_items


class Detector:
    def __init__(self, items, config_file, async_client, client):
        self.async_client = client
        self.client = client
        self.config = fetch_config(config_file)
        self.debug = self.config[0]
        self.items = fetch_item_info(items, self.client)

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
