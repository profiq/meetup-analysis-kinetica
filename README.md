# Analysis of Meetup.com using Kinetica platform

Meetup.com data analysis and visualization on Kinetica platform  
  
This project is fully described in the articles which can be found online.  
We are focusing on these main topics:  

1. Running the DB and injesting the data into it using python backend
2. Doing analysis using Kinetica Reaveal and how to build dashbaord
3. Showing the data in our own JavaScript (React) app using KineticaDB API and Kickbox.js library

### Backend setup (Kinetica DB with Reveal + Python import scripts)

   1. Install [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/)
   2. Clone this repo
   3. Edit `docker-compose.yml` and fill in license key (grab one [here](https://www.kinetica.com/trial/))
   4. Run docker containers `docker-compose up -d`
   - You can check Kinetica Admin Page on `localhost:8080` with `admin` as a username and password
   - You can check Kinetica Reveal page on `localhost:8088` with `admin` as a username and password
   
### Frontend setup (JavaScript React app) 
   
   1. Make sure you have Node.js and Yarn installed
   2. Setup required packages `cd react-frontend && yarn`
   3. Start the page on `localhost:3000` by `yarn start`
   
  - [More info about frontend](/react-frontend/README.md)


#### More indepth description 

In `docker-compose.yml` file you can find two services. One is for running the DB itself. And one is for running or python code which connects to the meetup.com API and injests the data into the DB. 

##### DB backend 

In config file `kinetica-backend/docker/kinetica.dockerfile` you can see how easy is to run Kinetica DB in the docker. There is extra folder called `dashboard`. This folder has already prepared Kinetica Reveal dashboard files together with the scripts for the import. When you start the docker backend it automatically inserts this dashboard into your Reaval, which you can find on url localhost:8088. In case you are intrested how you can build such dashboard youself head over to our second article.

##### Python backend for meetup.api

In config `kinetica-backend/python-backend/python.dockerfile` you can see pretty standard Python container. Based on `requirements.txt` you can see that we import the Kinetica python API library for inserting the data which is done using the files in that folder. Each file should be commented. If you are intrested in more about this topic be sure to read our first article which describes how to import your data into the DB.


