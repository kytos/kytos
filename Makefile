build: clean prepare
	python3 setup.py sdist bdist_wheel
	ls -l dist/

clean:
	rm -rf build/ dist/ *.egg-info/ kytos/web-ui-*

prepare:
	pip3 install --upgrade pip setuptools wheel twine

testupload: build
	twine upload -r pypitest dist/*

upload: build
	twine upload dist/*
