FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installed separately (not pinned in requirements.txt) so a rebuild can pick up
# the newest yt-dlp release independently of the rest of the dependencies.
RUN pip install --no-cache-dir -U yt-dlp

COPY bot/ ./bot/

RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /data/downloads \
    && chown -R appuser:appuser /data /app

USER appuser

ENV DOWNLOAD_DIR=/data/downloads

CMD ["python", "-m", "bot.main"]
