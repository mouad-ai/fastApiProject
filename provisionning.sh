#!/bin/bash

projectName= "fastApiProject"
sudo apt-get update -y

sudo apt-get install python3-venv -y

mkdir helloworld

cd helloworld

python3 -m venv venv

source venv/bin/activate


pip install Flask -y

sudo apt-get install git
sudo apt-get install bash
sudo apt-get install unzip

git clone https://github.com/mouad-ai/fastApiProject.git
unzip $projectName.zip
pip install gunicorn




