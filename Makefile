setup:
	python3 -m venv env && . env/bin/activate && pip install -r requirements.txt

run:
	bash -c '. env/bin/activate && python -m scripts.journey_cron --debug'

clean:
	rm -rf env