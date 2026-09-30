import re
import math

latency_re = re.compile(r"latency_ms=[0-9]+")
service_re = re.compile(r"service=[a-z]+-service")
bucket_width = 5
num_buckets = 6000
services = {}

with open("latency_logs.txt") as f:
    for line in f:
        latency = re.search(latency_re, line)
        service = re.search(service_re, line)
        if latency and service:
            service_value = service.group(0).split("=")[1]
            if service_value not in services:
                 services[service_value] = [1, [0 for _ in range(num_buckets)]]
            else:
                 services[service_value][0] += 1
            latency_value = int(latency.group(0).split("=")[1])
            bucket_index = min((latency_value//bucket_width), num_buckets - 1)
            services[service_value][1][bucket_index] += 1

for service,values in services.items():
    total_requests = values[0]
    p95_requests = math.ceil(0.95 * total_requests)
    p99_requests = math.ceil(0.99 * total_requests)
    p95_index, p99_index = None, None
    for index,requests in enumerate(values[1]):
            p95_requests -= requests
            p99_requests -= requests
            if p95_index is None and p95_requests <= 0:
                p95_index = index

            if p99_index is None and p99_requests <= 0:
                p99_index = index

            if p95_index is not None and p99_index is not None:
                break

    print(f"{service} 95th percentile: {p95_index * 5}ms")
    print(f"{service} 99th percentile: {p99_index * 5}ms")
