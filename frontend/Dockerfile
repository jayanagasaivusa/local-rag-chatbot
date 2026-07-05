# Use official Node.js image
FROM node:20-alpine

# Set the working folder inside the container
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Open port 5173 for Vite
EXPOSE 5173

# Start the React development server and expose it to the host
CMD ["npm", "run", "dev", "--", "--host"]