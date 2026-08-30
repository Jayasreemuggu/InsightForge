import concurrent.futures
import requests
import time


URL = "http://127.0.0.1:8000/analyze"

PAYLOAD = {
    "sales_file": "data/sales.csv",
    "feedback_file": "data/customer_feedback.csv",
    "region": "North",
    "date": "2025-06-01",
    "persona": "Analyst"
}


def send_request(request_id):
    start = time.perf_counter()

    try:
        response = requests.post(
            URL,
            json=PAYLOAD,
            timeout=60
        )

        elapsed = time.perf_counter() - start

        return {
            "id": request_id,
            "status": response.status_code,
            "time": elapsed
        }

    except Exception as e:
        elapsed = time.perf_counter() - start

        return {
            "id": request_id,
            "status": "ERROR",
            "time": elapsed,
            "error": str(e)
        }


def run_test(number_of_requests):

    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=number_of_requests
    ) as executor:

        results = list(
            executor.map(
                send_request,
                range(number_of_requests)
            )
        )

    total_time = time.perf_counter() - start

    successful = [
        r for r in results
        if r["status"] == 200
    ]

    failed = [
        r for r in results
        if r["status"] != 200
    ]

    print("\n========== SCALABILITY TEST ==========")
    print(f"Requests        : {number_of_requests}")
    print(f"Total time      : {total_time:.2f} seconds")
    print(f"Successful      : {len(successful)}")
    print(f"Failed          : {len(failed)}")

    if successful:
        avg = (
            sum(r["time"] for r in successful)
            / len(successful)
        )

        print(f"Average latency : {avg:.2f} seconds")

    print("======================================")

    for result in results:
        print(result)


if __name__ == "__main__":

    for count in [2, 5, 10]:

        print(
            f"\n\nTesting {count} concurrent requests..."
        )

        run_test(count)