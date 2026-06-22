FROM nvidia/cuda:12.0.0-base-ubuntu22.04

# Avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    python3 \
    python3-pip \
    libuv1 \
    libssl3 \
    libhwloc15 \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip3 install rich flask requests

WORKDIR /app

# Create bin directory
RUN mkdir -p /app/bin

# Download XMRig for Linux (Generic Static build is safest for Docker)
RUN wget https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-static-x64.tar.gz -O xmrig.tar.gz && \
    tar -xf xmrig.tar.gz && \
    cp xmrig-6.21.0/xmrig bin/xmrig && \
    rm -rf xmrig.tar.gz xmrig-6.21.0

# Copy application files
COPY miner_tui.py .
COPY miner_web_unified.py .
COPY setup_termux.sh .
COPY GUIDE.md .

# Create a entrypoint script to handle the background processes
RUN echo "#!/bin/bash\npython3 miner_web_unified.py & \npython3 miner_tui.py\nwait -n\nexit \$?" > entrypoint.sh && chmod +x entrypoint.sh

# Expose ports
EXPOSE 5002 8888

ENTRYPOINT ["./entrypoint.sh"]
