python3 -m pytest --cov=carlhauser_client --cov=carlhauser_server --cov=common --cov-report html ./carlhauser_client_tests/* ./carlhauser_server_tests/* ./common_tests/
coverage-badge -o coverage.svg
