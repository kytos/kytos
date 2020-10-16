build: clean prepare
	python3 setup.py sdist bdist_wheel
	ls -l dist/

clean:
	rm -vrf build/ dist/ *.egg-info/ kytos/web-ui-*
	find . -name __pycache__ -type d | xargs rm -rf
	test -d docs && make -C docs/ clean

prepare:
	pip3 install --upgrade pip setuptools wheel twine

testupload: build
	twine upload -r pypitest dist/*

upload: build
	twine upload dist/*
