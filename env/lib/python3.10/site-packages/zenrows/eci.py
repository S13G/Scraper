
# # pip install zenrows
# from zenrows import ZenRowsClient

# # // TODO
# # client = ZenRowsClient("YOUR_API_KEY", concurrency=5, retries=2)
# # client = ZenRowsClient("071a4acb990f72a0b1126216120b55205b754536", concurrency=5, retries=2)
# client = ZenRowsClient("913820d92490e767a700b424c41d71d391b2fdad", concurrency=5, retries=2)
# url = "https://www.elcorteingles.es/electrodomesticos/ofertas-de-electrodomesticos/"
# params = {"autoparse": "true", "antibot": "true"}

# for i in range(1, 56): # max page - 1
#     try:
#         final_url = url if i == 1 else f"{url}?page={i}"
#         response = client.get(final_url, params=params)
#         print(response.text)
#     except Exception as e:
#         print(e)



# pip install zenrows
from zenrows import ZenRowsClient

# // TODO
# client = ZenRowsClient("YOUR_API_KEY", concurrency=5, retries=2)
# client = ZenRowsClient("071a4acb990f72a0b1126216120b55205b754536", concurrency=5, retries=2)
client = ZenRowsClient("913820d92490e767a700b424c41d71d391b2fdad", concurrency=5, retries=2)
url = "https://www.autoscout24.es/lst/audi/a4"
# params = {"autoparse": "true", "antibot": "true"}
params = {"autoparse": "true"}


for i in range(1, 6): # max page - 1
    try:
        final_url = url if i == 1 else f"{url}?page={i}"
        response = client.get(final_url, params=params)
        print(response.text)
    except Exception as e:
        print(e)