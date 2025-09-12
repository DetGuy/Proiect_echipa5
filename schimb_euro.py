import requests

def convert_to_euro(amount, currency):
    url = f"https://open.er-api.com/v6/latest/{currency}"
    response = requests.get(url)
    data = response.json()

    if data["result"] != "success":
        raise ValueError(f"Eroare API: {data}")

    rate = data["rates"]["EUR"]
    return amount * rate

print(convert_to_euro(150, 'RON'))
