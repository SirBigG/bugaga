
test:
	PYTHONPATH=`pwd` python -m unittest discover . "test_*.py"


release:
	docker build --platform linux/x86_64 -t sirbigg/bugaga:latest .
	docker push sirbigg/bugaga:latest
