# WTF?

## DataGenerator

Generates data objects and stores them. Objects accesses by api
- /api/objects/:id

## Distribution

Responsible to generate tasks, and assign them to processors. For start process,
at least one processor should be subscribed

- /api/getnew
- /api/finish

## Process service

Incapsulate some business logic, like processing objects. Subscribes to events,
and wait for getting new object from Distribution.

- /api/results/:id

## Statistics

Just counts how many gotten objects, how many finished and how much time it's got
