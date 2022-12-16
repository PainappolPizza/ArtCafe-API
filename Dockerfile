# 
FROM python:3.11

## MAKE A FASTAPI DOCKEFILE
## https://fastapi.tiangolo.com/deployment/docker/

RUN mkdir /code

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

# navigate to /prisma and execute prisma generate
# this will generate the prisma client

COPY ./prisma ./prisma

RUN cd ./prisma && prisma generate

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8083"]