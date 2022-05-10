FROM node:17-alpine
WORKDIR /usr/src/app
COPY src/package*.json ./
RUN npm install
COPY src/search.js .
CMD ["node", "search.js"]