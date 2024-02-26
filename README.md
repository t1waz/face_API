# FACE DETECTOR

detect faces and stream results simple way !


### ENDPOINTS

Run app and go to /docs OR:
- POST /image                           -> create face job
- GET /jobs/{job_id}                    -> get date about job
- GET /jobs/{job_id}/processed-image    -> get processed image
- WS /ws                                -> connect to live stream of processed image urls


### SETUP

    $ cp example.envs .envs
    $ docker compose build

### RUN

app -> localhost:8282/

    $ docker compose up

### TESTS

    $ docker compose run face_backend pytest --asyncio-mode=auto


### MAIN FLOW

1. post request with image to process
2. backend create "face job", persist origin file, do all logic/validation with "face_job"
3. backend create "face job" event as request for detection via producer.
4. consumer/consumers consume event - request for face detection. 
 -  Consumer use face detector, and handle "face job" status/metadata,
5. In case of face detection, consumer push data about detection to job ws stream
6. Current open websockets iterate over job ws stream do get latest data about detection


```
       1                             2                              3                                               
                +------------+                 +------------+                 +----------------------------+        
    /image      |            |   create job    |            |    push event   |                            |        
--------------> |  face API  | --------------> |  producer  | --------------> |        JOB STREAM          |        
     POST       |            |                 |            |                 |                            |        
                +------------+                 +------------+                 +----------------------------+        
                +------------+                                                ^             ^              ^        
                |  websocket |                                                |             |              |        
                +------+-----+                                                |             |              |        
                       |                                                  4   | consume     | consume      | consume
                       |                                                      |             |              |        
                       |                                                      |             |              |        
                       |                                                                                            
                       |                                               +------------+ +------------+ +------------+ 
                       |                                               |            | |            | |            | 
                       |                                               |  producer  | |  producer  | |  producer  | 
                       |                                               |            | |            | |            | 
                       |                                               +------------+ +------------+ +------------+ 
                       |                                               +------------+ +------------+ +------------+ 
                       |                                               |  detector  | |  detector  | |  detector  | 
                       |                                               +------------+ +------------+ +------------+ 
                       |                                                                                            
                       |                                                      |             |              |        
                       |                                                      |             |              |        
                       |                                                  5   | push        | push         | push   
                       |                                                      |             |              |        
                       |                                                      |             |              |        
                       |                          6                           v             v              v        
                       |                                                      +----------------------------+        
                       |               iter read by push messages             |                            |        
                       +----------------------------------------------------->|        JOB WS STREAM       |        
                                                                              |                            |        
                                                                              +----------------------------+ 

```


### STORAGE

- postgres for job data
- dir storage "bucket like" for storing files and serve files


### STACK

- fastAPI as web server
- async python for event handling (producer/consumer/handler)
- nginx to serve files as "static" + simple reverse proxy
- redis for backend for stream handler + pub/sub architecture 
- docker compose cuz it's simple and fast


### TODO

- create package for utils
- make more unit tests
- create pyproject.toml + all stuff with pre-commit etc etc
- make real separate webserver/consumer Dockerfiles
- clear dockerfiles
- move to poetry + clear requirements
- clear TODO comments