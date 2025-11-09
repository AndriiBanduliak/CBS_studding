import time 

def mesure_time(runs: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            total_time = 0
            last_result = None
            for _ in range(runs):
                start_time = time.time()
                last_result = func(*args, **kwargs)
                end_time = time.time()
                total_time += (end_time - start_time)
            avg_time = total_time / runs
            print(f"Average execution time over {runs} runs: {avg_time:.6f} seconds")
            return last_result
        return wrapper
    return decorator

@mesure_time(runs=5)
def example_function(number_of_iterations: int):
    return sum(range(number_of_iterations))

if __name__ == "__main__":
    total = example_function(1000000)
    print("Done")
    print(total)