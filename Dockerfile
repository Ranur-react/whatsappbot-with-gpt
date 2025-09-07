# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_ENV=production

# Install necessary packages for network resolution
RUN apk add --no-cache \
    curl \
    ca-certificates \
    bind-tools \
    iputils \
    && update-ca-certificates

# Create app directory
WORKDIR /usr/src/app

# Copy package files
COPY /waweb-api/package*.json ./

# Configure npm for better network handling
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set fetch-retries 5

# Install dependencies
RUN npm install --production

# Bundle app source
COPY /waweb-api/. .

# Set Node.js options for better DNS resolution
ENV NODE_OPTIONS="--dns-result-order=ipv4first --max-old-space-size=1024"

# Expose port
EXPOSE 3000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || curl -f http://localhost:3000 || exit 1

# Create startup script with proper Alpine syntax
RUN echo '#!/bin/sh' > /start.sh && \
    echo '# Add public DNS servers' >> /start.sh && \
    echo 'echo "nameserver 8.8.8.8" >> /etc/resolv.conf' >> /start.sh && \
    echo 'echo "nameserver 1.1.1.1" >> /etc/resolv.conf' >> /start.sh && \rver 1.1.1.1" >> /etc/resolv.conf' >> /start.sh && \
    echo 'echo "nameserver 208.67.222.222" >> /etc/resolv.conf' >> /start.sh && \c/resolv.conf' >> /start.sh && \
    echo '# Start application' >> /start.sh && \    echo '# Start application' >> /start.sh && \
    echo 'exec npm start' >> /start.sh && \m start' >> /start.sh && \
    chmod +x /start.sh    chmod +x /start.sh



CMD ["/start.sh"]
CMD ["/start.sh"]
