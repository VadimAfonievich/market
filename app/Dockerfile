FROM python:3.8

#RUN apt-get update && apt-get install -y supervisor
#RUN mkdir -p /var/log/supervisor
# Make docker-compose wait for container dependencies be ready
# Solution 1: use dockerize tool -----------------------------
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Solution 2: use docker-compose-wait tool -------------------
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

WORKDIR /app
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x ./scripts/docker-entrypoint.sh
#CMD ["python", "market.py"]



#COPY ./etc/supervisor/*.conf /etc/supervisor/conf.d/

#COPY ./celery/worker_start.sh /start-celeryworker
#RUN sed -i 's/\r$//g' /start-celeryworker
#RUN chmod +x /scripts/run.sh


#COPY ./celery/beat_start.sh /start-celerybeat
#RUN sed -i 's/\r$//g' /start-celerybeat
#RUN chmod +x /start-celerybeat

#CMD ["/usr/bin/supervisord"]
#CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "run:app"]
#CMD ["celery", "-A",  "web.tasks.celery", "worker",  "--concurrency=1"]
#CMD ["celery", "-A",  "web.tasks.celery", "beat", "-S", "celerybeatmongo.schedulers.MongoScheduler", "-l", "INFO"]

#CMD ["bash", "./scripts/run.sh"]
#CMD ["python3.7", "tester.py"]
