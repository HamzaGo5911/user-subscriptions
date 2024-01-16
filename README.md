## Setup Environment For user-subscriptions:

#### 1.In order to use User-Subscription repository, you need to
   * Install [Python](https://www.python.org/) and [Docker](https://docs.docker.com/engine/install/) on your local system

#### To check the logs of a running Docker container, you can use the following command
            docker logs -f Container ID

# user-subscription

This Flask application allows users to register and choose from multiple features for subscription. Upon selecting a feature and subscribing, the user receives a confirmation email sent to the registered email address. In case the user does not select any features for subscription, they will also receive an email notification. 
This email will be sent to the address used during the registration process on the app

## Getting Started

To get started with this DBMigration, follow these steps:
1. Clone this repository

            git clone https://github.com/HamzaGo5911/user-subscriptions.git

2. Start docker-compose.yml file

             sudo docker-compose up --build
Or

              docker-compose up -d --f

# Testing the API 

To view the logs for the 'api' service:

            sudo docker-compose logs app

To view the logs for the 'mysql' service:

         sudo docker-compose logs mysql
