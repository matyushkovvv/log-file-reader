import pytest
import json

from main import create_report


@pytest.fixture
def sample_logs():
    return [
        json.dumps({"url": "/api/v1/users", "response_time": 0.123}),
        json.dumps({"url": "/api/v1/users", "response_time": 0.456}),
        json.dumps({"url": "/api/v1/orders", "response_time": 0.789}),
    ]

def test_result_aggregation(sample_logs):
    result = {}
    for line in sample_logs:
        data = json.loads(line)
        endpoint = data['url']
        response_time = data['response_time']

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

    assert result["/api/v1/users"]["total"] == 2
    assert abs(result["/api/v1/users"]["sum_response_time"] - (0.123+0.456)) < 1e-6
    assert result["/api/v1/users"]["max_response_time"] == 0.456
    assert result["/api/v1/orders"]["total"] == 1
    assert result["/api/v1/orders"]["max_response_time"] == 0.789

def test_create_report_average():
    result = {
        "/api/v1/users": {"total": 2, "sum_response_time": 0.579, "max_response_time": 0.456},
        "/api/v1/orders": {"total": 1, "sum_response_time": 0.789, "max_response_time": 0.789},
    }

    report = create_report(result, 'average')

    assert report[0]["handler"] == "/api/v1/users"
    assert report[0]["total"] == 2
    assert report[0]["avg_response_time"] == f"{0.579/2:.3f}"
    assert report[1]["handler"] == "/api/v1/orders"
    assert report[1]["avg_response_time"] == f"{0.789/1:.3f}"


def test_create_report_summary():
    result = {
        "/api/v1/users": {"total": 2, "sum_response_time": 0.579, "max_response_time": 0.456},
        "/api/v1/orders": {"total": 1, "sum_response_time": 0.789, "max_response_time": 0.789},
    }

    report = create_report(result, 'summary')

    assert report[0]["handler"] == "/api/v1/users"
    assert report[0]["total_response_time"] == f"{0.579:.3f}"
    assert report[0]["avg_response_time"] == f"{0.579/2:.3f}"
    assert report[0]["max_response_time"] == f"{0.456:.3f}"


def test_create_report_invalid_type():
    result = {}
    assert create_report(result, 'invalid') is None


def test_create_report_empty():
    result = {}
    report = create_report(result, 'summary')
    assert report == []
