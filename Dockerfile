#Python image
FROM python:3.8-slim-buster

#working directory to /app
WORKDIR /app

#copy current directory into the container at /app
COPY . /app

#upgrade pip
RUN pip install --upgrade pip

#install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#Set the default command to run when starting container
CMD ["python", "project3a.py"]
