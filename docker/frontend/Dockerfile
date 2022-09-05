FROM node:16-alpine
WORKDIR /react
COPY package.json ./
RUN yarn install
COPY . .
RUN yarn build



