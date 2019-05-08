IMAGE := quay.io/app-sre/catalog-image
IMAGE_TAG := latest

.PHONY: build
build:
	docker build -t $(IMAGE):$(IMAGE_TAG) .
