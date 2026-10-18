# Build the Go executable and keep its embedded catalogue in sync with the Python one.
#
#   make            build bin/Ergaelion
#   make test       run the Python and Go tests
#   make sync       copy the game data files into goplaybook/data/

GO_DIR := goplaybook
BIN := bin/Ergaelion

.PHONY: all build sync test test-docker clean

all: build

sync:
	cp gtplaybook/data/*.json gtplaybook/data/*.txt $(GO_DIR)/data/

build: sync
	mkdir -p bin
	cd $(GO_DIR) && go build -o ../$(BIN) .

test: build sync
	python3 -m unittest discover -s tests
	cd $(GO_DIR) && go test ./...

# Run both suites on Linux in a container. The project is copied first, so the
# macOS binary in bin/ is never touched.
test-docker:
	docker run --rm -v "$(CURDIR)":/src:ro golang:1.24 bash -c "\
		apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq python3 >/dev/null 2>&1; \
		cp -r /src /w && cd /w/goplaybook && go vet ./... && go test ./... && \
		go build -o /w/bin/Ergaelion . && cd /w && python3 -m unittest discover -s tests"

clean:
	rm -rf bin
