FROM node:18-buster-slim

RUN apt-get update && apt-get install -y curl unzip

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip && ./aws/install

RUN npm install -g aws-cdk@latest

WORKDIR /var/cdk
# COPY /cdk/package.json /var/cdk/package.json
# COPY /cdk/package-lock.json /var/cdk/package-lock.json
# RUN npm install
