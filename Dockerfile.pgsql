FROM mdillon/postgis:latest
RUN apt-get update -y --fix-missing
EXPOSE 5432
