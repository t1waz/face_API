FROM hdgigante/python-opencv:4.9.0-debian

RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev

RUN apt-get update && apt-get upgrade -y && apt-get install -y bash

WORKDIR /app

COPY ./compose/backend/requirements.txt /app

RUN apt-get update && apt-get install -y python3.11-venv

RUN apt-get update && apt-get install -y libgl1-mesa-glx

RUN python3 -m venv /path/to/venv
ENV PATH="/path/to/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8282

COPY ./src /app

CMD ["uvicorn", "face_backend.main:app", "--host", "0.0.0.0", "--port", "8282", "--reload"]
