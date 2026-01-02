# Use LTS Node (stable ABI for native modules like canvas)
FROM node:25-slim

# Create app directory
WORKDIR /app

# Install OS-level native dependencies required by canvas
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libjpeg-dev \
    libgif-dev \
    librsvg2-dev \
    libexpat1 \
    python3 \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# # Copy dependency manifests first (better Docker caching)
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy application source code
COPY . /app/

# Expose the port your server listens on
EXPOSE 3000

# Start the Node server
CMD ["node", "index.js"]
