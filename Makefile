test_unit:
	PYTHONPATH=. pytest-3 -v -s tests/unit/network.py

test_integration:
	PYTHONPATH=. pytest-3 -v -s tests/integration/modules.py