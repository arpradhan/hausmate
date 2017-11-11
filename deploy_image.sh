#!/bin/bash
tag=$1
project=hausmate-185516

docker tag hausmate gcr.io/$project/hausmate:$tag
gcloud docker -- push gcr.io/$project/hausmate:$tag
