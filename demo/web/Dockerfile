FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5373
CMD ["npm", "run", "dev", "--", "--host"]