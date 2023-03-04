# python3 and requests library required
# pip install requests
import requests
response = requests.get(
    "https://api.zenrows.com/v1/?apikey=5d1ca2812ca836b1e5cbd0d5e25e0cd7f3509efc&url=https%3A%2F%2Fwww.classcentral.com")
print(response.text)
