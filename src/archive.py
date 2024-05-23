import os
import shutil
import sys
import time
import csv

def log_operation(operation, status):
    with open('log.csv', 'a') as log_file:
        writer = csv.writer(log_file)
        writer.writerow([int(time.time()), operation, status])

def process_create_type(params):
    type_name = params[0]
    if os.path.exists(type_name):
        log_operation(f"create type {' '.join(params)}", "failure")
        return "failure"
    os.makedirs(type_name)
    schema = ' '.join(params[1:])
    with open(os.path.join(type_name, 'schema.txt'), 'w') as schema_file:
        schema_file.write(schema)
    
    shutil.copy('index_template.py', os.path.join(type_name, 'index.py')) #copy index template to the folder 
    
    log_operation(f"create type {' '.join(params)}", "success")
    return "success"

def process_create_record(params):
    type_name = params[0]
    if not os.path.exists(type_name):
        log_operation(f"create record {' '.join(params)}", "failure")
        return "failure"
    # Delegate to the relation's index.py
    result = os.system(f"python3 {os.path.join(type_name, 'index.py')} create_record {' '.join(params[1:])}")
    status = "success" if result == 0 else "failure"
    log_operation(f"create record {' '.join(params)}", status)
    return status

def process_delete_record(params):
    type_name = params[0]
    if not os.path.exists(type_name):
        log_operation(f"delete record {' '.join(params)}", "failure")
        return "failure"
    # Delegate to the relation's index.py
    result = os.system(f"python3 {os.path.join(type_name, 'index.py')} delete_record {params[1]}")
    status = "success" if result == 0 else "failure"
    log_operation(f"delete record {' '.join(params)}", status)
    return status

def process_search_record(params):
    type_name = params[0]
    if not os.path.exists(type_name):
        log_operation(f"search record {' '.join(params)}", "failure")
        return "failure"
    # Delegate to the relation's index.py
    result = os.system(f"python3 {os.path.join(type_name, 'index.py')} search_record {params[1]}")
    status = "success" if result == 0 else "failure"
    log_operation(f"search record {' '.join(params)}", status)
    return status

def main(input_file):
    with open(input_file, 'r') as file:
        commands = file.readlines()

    with open('output.txt', 'w') as output_file:
        for command in commands:
            parts = command.strip().split()
            operation = parts[0]
            params = parts[1:]
            if operation == "create" and params[0] == "type":
                result = process_create_type(params[1:])
            elif operation == "create" and params[0] == "record":
                result = process_create_record(params[1:])
            elif operation == "delete" and params[0] == "record":
                result = process_delete_record(params[1:])
            elif operation == "search" and params[0] == "record":
                result = process_search_record(params[1:])
            else:
                result = commands + " failure"
            output_file.write(result + '\n')

if __name__ == "__main__":
    input_file = sys.argv[1]
    main(input_file)
