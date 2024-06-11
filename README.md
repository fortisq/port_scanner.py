###     port_scanner.py Script Breakdown

1. **Imports and Dependencies**:
    - `socket`: For network connections.
    - `threading`: For creating multiple threads.
    - `Queue`: For managing the ports to be scanned and storing results.
    - `argparse`: For parsing command-line arguments.
    - `sys`: For system-specific parameters and functions.

2. **Function to Scan a Single Port**:
    ```python
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
    ```
    - This function attempts to connect to a specified port on the given IP address.
    - If the connection is successful, it tries to read a banner (if any) from the port.
    - The result (port status and banner) is put into the `output_queue`.

3. **Worker Thread Function**:
    ```python
    def worker(ip, timeout, output_queue, port_queue):
        while not port_queue.empty():
            port = port_queue.get()
            scan_port(ip, port, timeout, output_queue)
            port_queue.task_done()
    ```
    - This function runs in each thread, pulling ports from the `port_queue` and scanning them using `scan_port`.

4. **Main Function**:
    ```python
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
    ```
    - **Argument Parsing**: Uses `argparse` to handle command-line arguments for IP address, ports, timeout, output file, and verbosity.
    - **Port Parsing**: Handles both comma-separated lists and ranges of ports.
    - **Queue Initialization**: Initializes `port_queue` for ports to be scanned and `output_queue` for storing results.
    - **Thread Creation**: Creates and starts 100 worker threads (adjustable as needed).
    - **Result Collection**: Collects results from `output_queue` and optionally prints them if verbose mode is enabled.
    - **Output to File**: Saves results to a specified file if the `-o` argument is provided.

### Usage Example

To scan ports 80 and 443 on IP address `192.168.1.1` with a timeout of 2 seconds and verbose output:
```sh
python port_scanner.py 192.168.1.1 -p 80,443 -t 2 -v
```

To scan a range of ports from 1 to 1024 and save the results to `scan_results.txt`:
```sh
python port_scanner.py 192.168.1.1 -p 1-1024 -o scan_results.txt
```

This script is a basic yet effective tool for port scanning, leveraging multithreading to improve performance.
