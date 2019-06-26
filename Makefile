prepare:
	pip3.6 install --upgrade pip setuptools wheel twine
clean:
	rm -rf build/ dist/ *.egg-info/
build: clean
	python3.6 setup.py sdist
testupload: build
	twine upload -r pypitest dist/*
upload: build
	twine upload dist/*
