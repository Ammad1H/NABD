.PHONY: all test retune forecast score
all:            ## full US-A pipeline with the frozen config (clones the hub if missing)
	python3 -m eval.run_all --cached
retune:         ## re-run 2023/24 tuning, then forecast and score
	python3 -m eval.run_all --cached --retune
test:
	python3 -m pytest -q tests
