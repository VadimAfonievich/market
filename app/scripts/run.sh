#!/bin/bash

##celery -A web.tasks.celery worker --concurrency=1 &
##celery -A  web.tasks.celery beat -S celerybeatmongo.schedulers.MongoScheduler -l INFO &
#gunicorn -b 0.0.0.0:8000 main:app
#gunicorn run:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
##gunicorn run:app --workers 4 --bind 0.0.0.0:8000
#python test.py
#python prod.py

#while true;do sleep 1;done;
python market.py


#CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "run:app"]
#CMD ["celery", "-A",  "web.tasks.celery", "worker",  "--concurrency=1"]
#CMD ["celery", "-A",  "web.tasks.celery", "beat", "-S", "celerybeatmongo.schedulers.MongoScheduler", "-l", "INFO"]