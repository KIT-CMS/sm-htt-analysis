#!/bin/bash

systemctl start docker
docker build --rm --tag=stwunsch/slc6-condocker:smhtt . | tee docker_build.log
docker push stwunsch/slc6-condocker:smhtt
