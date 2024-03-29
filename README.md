# AIoT-Texas-hold-em-Smart-Table

![](https://github.com/jotpalch/AIoT-Texas-hold-em-Smart-Table/assets/49465120/15804e6a-26ec-408c-b389-70d8ac17a2c2)
![](https://github.com/jotpalch/AIoT-Texas-hold-em-Smart-Table/assets/49465120/896083ee-56b6-4781-bf7b-77e7c7467dde)

[Google Slide Link (zh-tw)](https://docs.google.com/presentation/d/1eHHE75cVTDKX-oiytssVUKOchTtuO_02/edit?usp=sharing&ouid=110986964650494650772&rtpof=true&sd=true)

## Overview

This project aims to provide a simple yet effective solution for rookie Texas Hold'em players to improve their understanding of pre-flop win rates. The system includes an ESP32-based device with computer vision capabilities for card detection, a Monte Carlo algorithm for win rate calculation, and a 2-player live broadcasting real-time win rate webpage. The computer vision component is built upon the Poker Cards Computer Vision Project by Roboflow, utilizing the YOLOv5 object detection model.

## Features

1. **Card Detection using YOLOv5**: Leverage the pre-trained YOLOv5 model to detect and recognize poker cards from images or live video feed.

2. **Monte Carlo Win Rate Calculation**: Utilize a multiprocess-enabled Monte Carlo algorithm to quickly and accurately calculate pre-flop win rates based on the detected cards.

3. **ESP32-based Device**: The solution is implemented on an ESP32 microcontroller, providing a compact and easily deployable device for poker training.

4. **2-Player Live Broadcasting Webpage**: Create a real-time web interface to display the pre-flop win rates of two players, enhancing the training experience.

## Hardware Setup

1. **ESP32 Board**: Use an ESP32 development board as the core hardware for the AIoT solution.

2. **Camera Module**: Connect a compatible camera module to the ESP32 for capturing live video feed or images.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/jotpalch/AIoT-Texas-hold-em-Smart-Table.git
cd AIoT-Texas-hold-em-Smart-Table
```

### 2. YOLOv5 Integration

```bash
cd yolov5
pip install -r requirements.txt
```

Follow the YOLOv5 instructions to set up the environment and download the pre-trained model.

### 3. Flask Server Setup

```bash
cd ../Flask
pip install -r requirements.txt
```

Replace Line notify token with your own token in the main.py

### 4. Run the Application

```bash
python main.py
```

Visit [http://localhost:38999](http://localhost:38999) in your browser to access the web interface.

## Running the Application with Docker

### Pull the Docker Image
To get started, pull the latest Docker image for the AIoT Texas Hold'em Smart Table application:

```bash
docker pull ghcr.io/jotpalch/aiot-texas-hold-em-smart-table:latest
docker run --rm -d -p 38999:38999/tcp aiot-texas-hold-em-smart-table:latest 
```

## Usage

1. Flash the ESP32 with the provided firmware in the folder [/ESP32S3](https://github.com/jotpalch/AIoT-Texas-hold-em-Smart-Table/tree/98383745c9483ef6930425e589467164eaca7d5f/ESP32S3) and replace the API with your domain and change the wifi infomation in the file [main.ino](https://github.com/jotpalch/AIoT-Texas-hold-em-Smart-Table/blob/98383745c9483ef6930425e589467164eaca7d5f/ESP32S3/main.ino).

2. Connect the ESP32 to the camera module.

3. Access the live broadcasting webpage to monitor the real-time pre-flop win rates.

## Acknowledgments

- Poker Cards Computer Vision Project by Roboflow - [Link](https://universe.roboflow.com/roboflow-100/poker-cards-cxcvz)
- YOLOv5 by Ultralytics - [Link](https://github.com/ultralytics/yolov5)
- Vector-playing-cards - [Link](https://code.google.com/archive/p/vector-playing-cards/downloads)

## Performance Enhancement

We have implemented a multi-process approach to accelerate the Monte Carlo algorithm for calculating hand win rates. In the case of 200,000 simulations, we achieved a 72% reduction in computation time, decreasing from the original single-process time of 6.87 seconds to 1.90 seconds.  

- Single Process: 6.87 seconds
- Multi-Process: 1.90 seconds (72% reduction)

![Performance Enhancement](https://github.com/jotpalch/AIoT-Texas-hold-em-Smart-Table/assets/49465120/7b40c112-4c1b-49f8-a34c-62c3684bf1b8)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.