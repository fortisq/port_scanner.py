import socket
import threading
from queue import Queue
import argparse
import sys

# Function to scan a single port
def scan_port(ip, port, timeout, output_queue):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        if result == 0:
            try:
                banner = sock.recv(1024).decode().strip()
            except:
                banner = ""
            output_queue.put((port, "Open", banner))
        sock.close()
    except Exception as e:
        output_queue.put((port, "Error", str(e)))

# Worker thread function
def worker(ip, timeout, output_queue, port_queue):
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(ip, port, timeout, output_queue)
        port_queue.task_done()

# Main function
def main():
    parser = argparse.ArgumentParser(description="Simple Port Scanner")
    parser.add_argument("ip", help="IP address to scan")
    parser.add_argument("-p", "--ports", help="Comma-separated list of ports or range (e.g., 80,443 or 1-1024)", default="1-1024")
    parser.add_argument("-t", "--timeout", help="Timeout in seconds for each port scan", type=float, default=1.0)
    parser.add_argument("-o", "--output", help="Output file to save results", default=None)
    parser.add_argument("-v", "--verbose", help="Verbose mode", action="store_true")
    args = parser.parse_args()

    # Parse ports
    ports = []
    if "-" in args.ports:
        start_port, end_port = map(int, args.ports.split("-"))
        ports = range(start_port, end_port + 1)
    else:
        ports = map(int, args.ports.split(","))

    # Queues
    port_queue = Queue()
    output_queue = Queue()

    # Enqueue ports
    for port in ports:
        port_queue.put(port)

    # Start worker threads
    threads = []
    for _ in range(100):  # Adjust number of threads as needed
        t = threading.Thread(target=worker, args=(args.ip, args.timeout, output_queue, port_queue))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    port_queue.join()
    for t in threads:
        t.join()

    # Collect and display results
    results = []
    while not output_queue.empty():
        port, status, banner = output_queue.get()
        results.append((port, status, banner))
        if args.verbose:
            print(f"Port {port}: {status} {banner}")

    # Save results to file if specified
    if args.output:
        with open(args.output, "w") as f:
            for port, status, banner in results:
                f.write(f"Port {port}: {status} {banner}\n")

    print("Scan complete.")

if __name__ == "__main__":
    main()
