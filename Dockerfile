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

# Create startup script using cat for better control
RUN cat > /start.sh << 'EOF'
#!/bin/sh
# Add public DNS servers
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf
echo "nameserver 208.67.222.222" >> /etc/resolv.conf

# Show DNS configuration
echo "=== DNS Configuration ==="
cat /etc/resolv.conf

# Start application
echo "=== Starting Application ==="
exec npm start
EOF

# Make script executable
RUN chmod +x /start.sh

# Start with custom script
CMD ["/start.sh"]
