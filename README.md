# Meetup.com Map

Meetup.com data analysis and visualization on Kinetica platform

### Backend setup

   1. Install <a href="https://docs.docker.com/install/">docker</a> and <a href="https://docs.docker.com/compose/install/">docker-compose</a> 
   2. Clone this repo `git clone git@gitlab.profiq.com:tech-research/kinetica/meetup-map.git`
   3. Edit `docker-compose.yml` and fill in license key
   4. Run docker containers `docker-compose up -d`
   - You can check Kinetica Admin Page on `localhost:8080` with `admin` as a username and password
   - You can check Kinetica Reveal page on `localhost:8088`
   
### Frontend setup
   
   1. Make sure you have Node.js and Yarn installed
   2. Setup required packages `cd react-frontend && yarn`
   3. Start the page on `localhost:3000` by `yarn start`
   
  - [More info about frontend](/react-frontend/README.md)