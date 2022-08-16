# most docker images aren't made from scratch
# can take existing image and use it as the basis for your image using the FROM command 
# here we use python as our base image
FROM python:3.9.5

# create directory 'code' inside container
WORKDIR /code

# add a path for python to look for modules
ENV PYTHONPATH=/code/src

# install cron (used to schedule jobs to run periodically at fixed time intervals)
RUN apt-get update
RUN apt-get install cron -y

# install python dependencies
ADD ./containers/pipelinerunner/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy local repo (everything in bitcoinDashboard) to container directory '/code'
COPY ./ /code/

# ref: https://stackoverflow.com/questions/37458287/how-to-run-a-cron-job-inside-a-docker-container

# copy crontab (file that contains schedule of cron entries to be run) to container
COPY /cron/crontab /etc/cron.d/cjob
 
# give crontab execution rights
RUN chmod 0644 /etc/cron.d/cjob

# submit crontab
RUN crontab /etc/cron.d/cjob

# create log file
RUN touch /var/log/cron.log

# execute crontab on container startup
CMD cron && tail -f /var/log/cron.log