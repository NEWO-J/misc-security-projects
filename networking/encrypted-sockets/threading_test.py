from concurrent.futures import ThreadPoolExecutor

def worker(item):
    return item ** item
    2

items = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(worker, items))

print(results)