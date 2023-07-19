import socket
import threading
from queue import Queue
from IPy import IP

NUM_THREADS = 200

def scan_ports(target, port_queue, open_ports):
    # this function scans the specified ports on the target IP/hostname
    # it checks if the ports are open or closed and adds open ports to the open_ports list

    while not port_queue.empty():
        port = port_queue.get()
        try:
            # create a socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # set a timeout (in seconds) for the connection attempt
            s.settimeout(1)

            # attempt to connect to the target w/port
            result = s.connect_ex((target, port))

            # check if the connection was successful (port open)
            if result == 0:
                open_ports.append(port)
                print(f"Port {port}: Open")
            else:
                print(f"Port {port}: Closed")

            # close the socket
            s.close()

        except socket.gaierror:
            print("Hostname could not be resolved")
            break

        except socket.error:
            print("Couldn't connect to the server")
            break

        except Exception as e:
            # catch any other exceptions that might occur during the scan
            print(f"Error while scanning port {port}: {e}")

def main():
    try:
        # get the target host IP address or hostname from the user & the port range
        target_host = input("Enter the target host IP address or hostname: ")
        target_ports = input("Enter the range of ports to scan (e.g., 1-100): ")

        # parse the target ports range
        start_port, end_port = map(int, target_ports.split('-'))
        port_range = range(start_port, end_port + 1)

        try:
            # check if the input is an IP address or hostname and get the target IP (the actual ip if hostname)
            IP(target_host)
            target_ip = target_host
        except ValueError:
            target_ip = socket.gethostbyname(target_host)

        # a queue to hold the ports to be scanned
        port_queue = Queue()

        # add the ports to the queue
        for port in port_range:
            port_queue.put(port)

        # a list to hold the open ports found during the scan
        open_ports = []

        # a list to hold the threads
        thread_list = []

        # threads for scanning ports
        for _ in range(min(NUM_THREADS, len(port_range))):
            thread = threading.Thread(target=scan_ports, args=(target_ip, port_queue, open_ports))
            thread_list.append(thread)
            thread.start()

        # wait for all threads to complete
        for thread in thread_list:
            thread.join()

        # print summary of open ports
        if open_ports:
            print("\nSummary:")
            for port in open_ports:
                print(f"Port {port}: Open")
        else:
            print("\nNo open ports found.")

    except KeyboardInterrupt:
        print("\nPort scanning process interrupted.")

    except ValueError:
        print("Invalid input. Please enter a valid IP address or hostname and port range.")

# just to make it look "professional"
if __name__ == "__main__":
    main()
