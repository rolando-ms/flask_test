## RESTful Services with Python/Flask

This repository contains 3 different RESTful services examples that can be deployed into the cloud:

* Database as a Service: This service can be used to store sentences in a MongoDB
* Image Classification: This service uses the InceptionV3 model to classify images given a picture URL
* Similarity text: This service compares tu given texts and gives the similarity ratio using spacy

## Using this Repository

* Clone this repository with ```git clone```.
* Build and run with docker: ```docker compose build```, ```docker compose up```
* Can be tested using postman and sending a POST request with a JSON dictionary to the corresponding address, e.g.:
  ```
  127.0.0.1:5000/classifyImg
  ```
  ```
  {
    "username": "XXXX",
    "password": "XXXX",
    "img_url": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Fox_009.jpg"
  }
  ```
 (The user and password must be already registered before using) 
