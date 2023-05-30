import json

# Read the JSON file
with open('data.json') as file:
    # Read the file content
    file_content = file.read()

    # Split the file content by newlines
    json_objects = file_content.strip().split('\n')

    # Process each JSON object and store results
    results = []
    for json_str in json_objects:
        # Load the JSON object
        data = json.loads(json_str)

        # Extract the values
        ip = data['ip_str']
        port = data['port']

        # Format as "ip_str:port"
        result = f"{ip}:{port}"

        results.append(result)

# Export results to a file
with open('result.txt', 'w') as result_file:
    result_file.write('\n'.join(results))