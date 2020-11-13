FROM baseimage:latest as base

COPY poetry.lock pyproject.toml ./
# RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin
RUN poetry install

COPY processor.py .

# RUN poetry build && /venv/bin/pip install dist/*.whl

EXPOSE 80

ENV QUEUE_URL="rabbitmq:5672"

ENTRYPOINT ["poetry", "run", "python", "processor.py"]
