from datetime import datetime, timedelta

import requests

from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image


class Auth:
    def create_api_key(self, description=None):
        response = requests.post(
            url=f"{OneAtlasClient.AUTH_URL}/api/v1/apikeys",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_AAA),
            json={"description": description},
        )
        response.raise_for_status()
        return response.json()

    def delete_api_keys(self):
        response = requests.delete(
            url=f"{OneAtlasClient.AUTH_URL}/api/v1/apikeys",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_AAA),
        )
        response.raise_for_status()

    def list_api_keys(self):
        response = requests.get(
            url=f"{OneAtlasClient.AUTH_URL}/api/v1/apikeys",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_AAA),
        )
        response.raise_for_status()
        return response.json()


class Data:

    def create_order(self, body):
        response = requests.post(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/orders",
            json=body,
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def download_order_to_file(self, order, download_path):
        try:
            download_link = order["deliveries"][0]["_links"]["download"]["href"]
        except KeyError:
            raise ValueError(
                'Invalid order provided; the entire order is required, { "_links": {...}, "id": ...}'
            )
        self.download_url_to_file(download_link, download_path)
        print(f"Downloaded to {download_path}")

    def get_account_information(self):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/me",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def get_contract(self, contract_id):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/contracts/{contract_id}",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def get_contract_subscription(self, contract_id, subscription_id):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/contracts/{contract_id}/subscriptions/{subscription_id}",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def get_contract_payment(self, contract_id, payment_id):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/contracts/{contract_id}/payments/{payment_id}",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def get_order(self, order_id):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/orders/{order_id}",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def get_price(self, body):
        response = requests.post(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/prices",
            json=body,
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def list_analytics(self, page=1, items_per_page=10):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/analytics",
            params={
                "page": page,
                "itemsPerPage": items_per_page,
            },
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def list_contracts(self, page=1, items_per_page=10):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/contracts",
            params={
                "page": page,
                "itemsPerPage": items_per_page,
            },
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def list_contract_payments(self, contract_id, page=1, items_per_page=10):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/contracts/{contract_id}/payments",
            params={
                "page": page,
                "itemsPerPage": items_per_page,
            },
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def list_contract_subscriptions(
        self, contract_id, page=1, items_per_page=10, type=None
    ):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/contracts/{contract_id}/subscriptions",
            params={"page": page, "itemsPerPage": items_per_page, "type": type},
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def list_orders(
        self, status=None, kind=None, customerRef=None, page=1, items_per_page=10
    ):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/orders",
            params={
                "status": status,
                "kind": kind,
                "customerRef": customerRef,
                "page": page,
                "itemsPerPage": items_per_page,
            },
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def list_subscription_payments(self, subscription_id, page=1, items_per_page=10):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/subscriptions/{subscription_id}/payments",
            params={
                "page": page,
                "itemsPerPage": items_per_page,
            },
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def get_user_roles(self):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/me/services",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def revoke_subscription(self, subscription_id):
        response = requests.get(
            url=f"{OneAtlasClient.DATA_URL}/api/v1/{subscription_id}/revoke",
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()


class Search:

    def search(self, body):
        response = requests.post(
            url=f"{OneAtlasClient.SEARCH_URL}/api/v2/opensearch",
            json=body,
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
        )
        response.raise_for_status()
        return response.json()

    def download_quicklook_to_file(self, scene, download_path):
        try:
            quicklook_link = scene["_links"]["quicklook"]["href"]
        except KeyError:
            raise ValueError(
                'Invalid scene provided; the entire scene is required, { "_links": {...}, "geometry": ...}'
            )
        self.download_url_to_file(quicklook_link, download_path)

    def plot_quicklook(self, scene):
        try:
            quicklook_link = scene["_links"]["quicklook"]["href"]
        except KeyError:
            raise ValueError(
                'Invalid scene provided; the entire scene is required, { "_links": {...}, "geometry": ...}'
            )
        self.plot_image_from_url(quicklook_link)


class OneAtlasClient(Auth, Data, Search):
    CLIENT_ID_AAA = "AAA"
    CLIENT_ID_IDP = "IDP"

    AUTH_URL = "https://authenticate.foundation.api.oneatlas.airbus.com"
    DATA_URL = "https://data.api.oneatlas.airbus.com"
    SEARCH_URL = "https://search.foundation.api.oneatlas.airbus.com"

    def __init__(self, api_key=None):
        self._access_tokens = {}
        self.api_key = api_key
        self.result_data = []
        self.result_index = 0
        self.current_image = ""

    def _authenticate(self, client_id=None):
        response = requests.post(
            url=f"{OneAtlasClient.AUTH_URL}/auth/realms/IDP/protocol/openid-connect/token",
            data={
                "apikey": self.api_key,
                "client_id": client_id,
                "grant_type": "api_key",
            },
        )
        response.raise_for_status()
        access_token = response.json()
        access_token["expiration"] = datetime.now() + timedelta(
            seconds=access_token["expires_in"] - 10
        )
        self._access_tokens[client_id] = access_token

    def _access_token(self, client_id=None):
        if client_id not in self._access_tokens:
            self._authenticate(client_id)
        elif self._access_tokens[client_id]["expiration"] < datetime.now():
            self._authenticate(client_id)

        return {
            "Authorization": f"Bearer " + self._access_tokens[client_id]["access_token"]
        }

    def download_url_to_file(self, url, path, params=None):
        with requests.get(
            url,
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
            params=params,
            stream=True,
        ) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    def plot_image_from_url(self, url, params=None):
        with requests.get(
            url,
            headers=self._access_token(OneAtlasClient.CLIENT_ID_IDP),
            params=params,
            stream=True,
        ) as r:
            r.raise_for_status()
            # Read the image from the response's bytes directly in memory
            image_bytes = BytesIO(r.content)
            # Open the image using PIL
            img = Image.open(image_bytes)
            # Plot the image
            plt.imshow(img)
            plt.axis("off")  # Optional: Turn off the axis labels
            plt.show()

    def extract_results(self, results):
        self.result_data = [
            {
                "image_id": f["properties"]["id"],
                "quicklook_link": f["_links"]["quicklook"]["href"],
                "acquisition_date": f["properties"]["acquisitionDate"],
                "constellation": f["properties"]["constellation"],
                "cloud_cover": f["properties"]["cloudCover"],
            }
            for f in results["features"]
        ]
        self.result_index = 0

    def show_result(self):
        if not self.result_data:
            print(
                "No results to display. Please run a search and extract results first."
            )
            return
        # Print certain properties of the current item
        item = self.result_data[self.result_index]
        print(f"result {self.result_index + 1} of {len(self.result_data)}")
        print(f"Image ID: {item['image_id']}")
        print(f"Acquisition Date: {item['acquisition_date']}")
        print(f"Constellation: {item['constellation']}")
        print(f"Cloud Cover: {item['cloud_cover']}%")
        self.current_image = item["image_id"]
        self.plot_image_from_url(item["quicklook_link"])

        # Increment the index and wrap around if at the end of the list
        self.result_index = (self.result_index + 1) % len(self.result_data)


if __name__ == "__main__":
    API_KEY = "PUT YOUR API KEY HERE"
    client = OneAtlasClient(api_key=API_KEY)

    api_keys = client.list_api_keys()
    account_information = client.get_account_information()
    user_roles = client.get_user_roles()

    contracts = client.list_contracts()
    contract_id = contracts["items"][0]["id"]
    contract = client.get_contract(contract_id)

    subscriptions = client.list_contract_subscriptions(contract_id)
    subscription_id = subscriptions["items"][0]["id"]
    subscription = client.get_contract_subscription(contract_id, subscription_id)

    c_payments = client.list_contract_payments(contract_id)
    s_payments = client.list_subscription_payments(subscription_id)

    payment_id = c_payments["items"][0]["id"]
    payment = client.get_contract_payment(contract_id, payment_id)

    analytics = client.list_analytics()

    results = client.search(
        {
            "cloudCover": "[0,30]",
            "incidenceAngle": "[0,40]",
            "processingLevel": "SENSOR",
            "relation": "intersects",
            "bbox": "-122.537,37.595,-122.303,37.807",
        }
    )
    result = results["features"][0]
    client.download_quicklook_to_file(result, "/tmp/quicklook.jpg")

    order_body = {
        "kind": "order.product",
        "products": [
            {
                "productType": "bundle",
                "radiometricProcessing": "REFLECTANCE",
                "imageFormat": "image/jp2",
                "crsCode": "urn:ogc:def:crs:EPSG::4326",
                "id": "d42de348-110b-4ed6-a597-755867b3ee54",
                "aoi": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [1.4089965820312502, 43.59829500262717],
                            [1.4089965820312502, 43.63408731864001],
                            [1.5078735351562496, 43.63408731864001],
                            [1.5078735351562496, 43.59829500262717],
                            [1.4089965820312502, 43.59829500262717],
                        ]
                    ],
                },
            }
        ],
    }
    price = client.get_price(order_body)
    order = client.create_order(order_body)

    orders = client.list_orders(kind="order.data.gb.product", status="delivered")
    order = orders["items"][0]
    client.download_order_to_file(order, "/tmp/order.zip")
