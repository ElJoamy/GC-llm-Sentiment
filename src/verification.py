import os
import csv

def check_and_create_csv(file_path, headers):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

def get_csv_file_path(report_type):
    if report_type == "sentiment":
        return 'report_sentiment.csv'
    elif report_type == "analysis":
        return 'report_analysis.csv'
    else:
        return 'report_general.csv' 

def append_to_csv(file_path, data, headers):
    with open(file_path, 'a+', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)
