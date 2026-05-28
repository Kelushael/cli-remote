FROM python:3.12-alpine
WORKDIR /app
RUN pip install --no-cache-dir aiohttp
COPY . /app
EXPOSE 8765
CMD ["python", "server.py"]
