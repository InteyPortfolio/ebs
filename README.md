# WTF?

EDA: Event Driven Architecture, where communication between services(micro?) go
though rabbitmq or similar.

## How to start

You can start all system in 3 variants: manual, docker-compose or 
minikube/minishift/crc. Last case tested only on minikube.


For compose or minikube it's ok for services fails on first, because it's
needed rabbitmq that may not started yet.

### minishift

I use kustomize for specs.

```bash
# use images from docker hub
kustomize build kustomka/hubbed/ | kubectl apply -f -
```

after all, we can export ports:
```bash

# "curl -X POST localhost:8000/objects" and you get system starts
kubectl port-forward deployment/datagen 8000:80

# looks at statistcs (console)
kubectl logs -f deployment/statistics

# and for view rabbit management (for debugging)
kubectl port-forward deployment/rabbit 15672
```

### docker-compose

```bash
cd services/
docker-compose up -d
```

### Manual

Manually it's little boring, but simple

```bash
# any term
docker run -d -p 5672:5672 -p 8080:15672
rabbitmq:management-alpine

# term 1
cd services/datagen
poetry install && poetry shell
QUEUE_URL='localhost:5672' uvicorn datagen:app --port 8002 --reload

# term 2
cd services/distributor
poetry install && poetry shell
QUEUE_URL=localhost:5672 python distributor.py


# term 3
cd services/processor
poetry install && poetry shell
QUEUE_URL=localhost:5672 python processor.py

# term 4
cd services/statistics/
poetry install && poetry shell
QUEUE_URL=localhost:5672 python statistics.py
```

### docker-compose


Then POST to /api/objects without payload with curl/postman/etc.
And you can see logs on each term. Statistics become on 4 term.

## Bus

All communications between services go through bus as events.

## DataGenerator

Generates data objects and stores them. For generate object POST to
`/api/objects/` without data.

## Distribution

Responsible to generate tasks, and assign them to processors. For start process,
at least one processor should be subscribed.
Doesn't provide API. It's API - is a bus

## Process service

Incapsulate some business logic, like processing objects. Subscribes to events,
and wait for getting new object from Distribution.
Doesn't provide API. It's API - is a bus

## Statistics

Just counts how many gotten objects, how many finished and how much time it's
got

# How to work with bus

Datagen generage object when it's hitten with `POST /api/objects/` without data.
Generated object published to exchange 'ebs' (event-based-system) with type
'topic'. Those messages has routing key "objects".

Distributor accepts messages on queue `distributor_consume` that has routing key
`objects`. When it's get object, distributor generates 3 tasks in
`distributor_publish` queue with routing key 'task-requests'.

Processor consumes queue `process_consume` and accepts messages with routing key
`task-requests`. Each processor should connect to same queue, otherwise, all of
them will accept each task, so distribution doesn't work.

When process get task, it push message to `processor_publish`
that it starts processing and after finish, publish message that it's finish.

Statistics subscribe to exchange and accepts all messages, and calculate
statistics, and store them in DB. We can look at it with `watch -n ,5 sqlite3
stats.db "select * from statistics"` or similar.


## Communication schema

```
Datagen -> OBJECT_CREATED -> Distributor, Statistics
Distributor -> TASK_CREATED -> Processor, Statistics
Processor -> TASK_STARTED -> Statistics
Processor -> TASK_FINISHED -> Statistics
```
### Exchanges

Topic
- distribution
- statistics
- tasks

Statistics system should accepts all messages.


TODO: return task to queue - fail processing
