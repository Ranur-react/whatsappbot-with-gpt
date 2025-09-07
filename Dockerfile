# Use an official Node.js runtime as a parent image
FROM node:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY /waweb-api/package*.json ./
RUN npm install

# Bundle app source
COPY /waweb-api/. .

# Expose the Node.js app port
EXPOSE 3000

# Start the Node.js app
CMD ["npm", "start"]






# Update DNS settings# Update DNS settings
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf
RUN echo "nameserver 1.1.1.1" >> /etc/resolv.conf
