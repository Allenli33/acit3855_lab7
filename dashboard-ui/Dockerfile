# Use an official Node runtime as a parent image, based on Alpine Linux for its smaller footprint
FROM node:13.12.0-alpine

# Set the working directory inside the container to /app
WORKDIR /app

# Add `/app/node_modules/.bin` to the $PATH environment variable to run executables from Node modules
ENV PATH /app/node_modules/.bin:$PATH

# Copy the package.json and package-lock.json files into the working directory
COPY package.json ./
COPY package-lock.json ./

# Install all the dependencies defined in package.json
RUN npm install

# If you need to build your React app, you would use react-scripts here
# But installing it globally is typically not necessary and can lead to a larger image size
# If react-scripts is specified in package.json, the above npm install will install it locally
# RUN npm install react-scripts@3.4.1 -g

# Copy the rest of your application's code into the working directory
COPY . ./

# Your package.json should define "start" in the scripts section to start your application
CMD ["npm", "start"]
