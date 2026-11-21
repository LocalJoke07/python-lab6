import os

import httpx

base_url = os.environ["GATEWAY_BASE_URL"]

with httpx.Client(base_url=base_url, timeout=5.0) as client:
    created = client.post(
        "/items",
        json={"name": "CPU", "price": 199.0, "quantity": 3},
    )
    created.raise_for_status()
    item = created.json()
    print(f"created id={item['id']} name={item['name']}")

    loaded = client.get(f"/items/{item['id']}")
    loaded.raise_for_status()
    print(f"loaded id={loaded.json()['id']} name={loaded.json()['name']}")
