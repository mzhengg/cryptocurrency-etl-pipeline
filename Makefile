# start up services and build images
docker compose up --build -d

# open bash shell in pipelinerunner container
docker exec -ti pipelinerunner bash

# run pytest on code to make sure there are no errors
	pytest /code/tests/integration

# start cronjob
	service cron start

# set up dashboard
	localhost:3000

# stop cronjob
	service cron stop

# tear down services and destroy images
docker compose down --volumes --rmi all