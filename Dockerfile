# Use the ultralytics/yolov5 base image
FROM ultralytics/yolov5:latest

RUN mv /usr/src/app /usr/src/yolov5

# Set the working directory
WORKDIR /usr/src/Flask

# Copy the Flask server code to the container
COPY /Flask /usr/src/Flask

# Install the required Python packages
RUN pip install -r requirements.txt

# Expose the Flask server port
EXPOSE 38999

# Set the entrypoint command to start the Flask server
CMD ["python", "main.py"]
