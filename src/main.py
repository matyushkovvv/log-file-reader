import argparse
import json
from tabulate import tabulate

def parse_logs(filenames):
    result = {}
    for filename in filenames:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data = json.loads(line)
                endpoint = data.get('url')
                response_time = data.get('response_time')

                if endpoint in result:
                    result[endpoint]['total'] += 1
                    result[endpoint]['sum_response_time'] += response_time
                    if response_time > result[endpoint]['max_response_time']:
                        result[endpoint]['max_response_time'] = response_time
                else:
                    result[endpoint] = {
                        'total': 1,
                        'sum_response_time': response_time,
                        'max_response_time': response_time
                    }
    return result


def create_report(result, report):
    table_data = []

    if report == 'average':
        for endpoint, stats in result.items():
            avg_response_time = stats['sum_response_time'] / stats['total']
            table_data.append({
                'handler': endpoint,
                'total': stats['total'],
                'avg_response_time': f"{avg_response_time:.3f}"
            })
    elif report == 'summary':
        for endpoint, stats in result.items():
            avg_response_time = stats['sum_response_time'] / stats['total']
            table_data.append({
                'handler': endpoint,
                'total': stats['total'],
                'total_response_time': f"{stats['sum_response_time']:.3f}",
                'avg_response_time': f"{avg_response_time:.3f}",
                'max_response_time': f"{stats['max_response_time']:.3f}"
            })
    else:
        return None

    return table_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Log Parser',
        description='This program parses log-files'
    )
    parser.add_argument('--file', nargs='+')
    parser.add_argument('--report', choices=['average', 'summary'], default='summary')
    args = parser.parse_args()

    if not args.file:
        print("No input files provided")
        exit(1)

    result = parse_logs(args.file)
    print(tabulate(create_report(result, args.report), headers='keys'))
