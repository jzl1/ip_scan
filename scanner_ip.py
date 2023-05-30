import requests
import json
import os
import concurrent.futures

API_KEY = os.environ['API_KEY']

# Read IP and port combinations from result.txt
with open('result.txt', 'r') as file:
    ip_ports = file.read().splitlines()

print('IP parsed!')

results = []
error_results = []

def api_check(API_KEY):
    response = requests.get(f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip=1.1.1.1")
    if response.status_code == 200:
        print('API works')
    else:
        print(f'IP check not available, code:{response.status_code}, response:{response.text}')
        input('Press any key to exit...')
        quit()

api_check(API_KEY)

# Function to process each IP and port combination
def process_ip_port(ip_port):
    ip, port = ip_port.split(':')
    url = f"http://{ip}:{port}/stream"
    host = os.environ['HOST']
    headers = {'Host': host, 'User-Agent': 'curl/8.0.1'}

    try:
        response = requests.get(url, headers=headers, timeout=1, verify=False)

        if response.status_code == 400:
            print(f'{ip}:{port}---Hit!')

            # Get IP location from 'h'
            h_ip_location = ''
            trace_url = f"http://{ip}:{port}/cdn-cgi/trace"
            trace_response = requests.get(trace_url, timeout=5, verify=False)
            trace_data = trace_response.text

            # Extract IP addresses and 'colo' from the trace data
            h_ip = None
            ip_ip = None
            colo = None
            for line in trace_data.splitlines():
                if line.startswith('h='):
                    h_ip = line.split('=')[1]
                elif line.startswith('ip='):
                    ip_ip = line.split('=')[1]
                elif line.startswith('colo='):
                    colo = line.split('=')[1]

            # Get the location information for the 'h' IP address using IP Geolocation API
            ip_location_data = ''
            if ip:
                ip_info_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={ip}"
                ip_info_response = requests.get(ip_info_url, timeout=5)
                if ip_info_response.status_code == 200:
                    ip_info_data = json.loads(ip_info_response.text)
                    city = ip_info_data.get('city', '')
                    state_prov = ip_info_data.get('state_prov', '')
                    country_name = ip_info_data.get('country_name', '')
                    isp = ip_info_data.get('isp', '')
                    ip_location_data = f"{city}, {state_prov}, {country_name}, {isp}"

            # Get the location information for the 'ip' IP address using IP Geolocation API
            ip_ip_location_data = ''
            if ip_ip:
                ip_ip_info_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={ip_ip}"
                ip_ip_info_response = requests.get(ip_ip_info_url, timeout=5)
                if ip_ip_info_response.status_code == 200:
                    ip_ip_info_data = json.loads(ip_ip_info_response.text)
                    ip_city = ip_ip_info_data.get('city', '')
                    ip_state_prov = ip_ip_info_data.get('state_prov', '')
                    ip_country_name = ip_ip_info_data.get('country_name', '')
                    ip_isp = ip_ip_info_data.get('isp', '')
                    ip_ip_location_data = f"{ip_city}, {ip_state_prov}, {ip_country_name}, {ip_isp}"

            # Print IP locations
            if ip_location_data and ip_ip_location_data:
                print(f"{h_ip}:{port} ({ip_location_data}) {ip_ip} ({ip_ip_location_data}) colo={colo}")

            # Append the result to the results list
            results.append(f"{ip}:{port} ({ip_location_data}) {ip_ip} ({ip_ip_location_data}) colo={colo}")

        else:
            print(f'{ip}:{port}---{response.status_code}')
            error_results.append(ip_port)
    except requests.exceptions.RequestException:
        return

# Create a ThreadPoolExecutor with a maximum of 10 threads
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    # Submit the tasks to the executor
    executor.map(process_ip_port, ip_ports)

# Export results to result1.txt
with open('result1.txt', 'w') as result_file:
    result_file.write('\n'.join(results))
