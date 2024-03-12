
# MICE Data Capture

The efficient integration of real-time medical device data is a promising approach to improve patient care. This repository presents a PoC for integrating real-time medical device data into clinical environments. Using the HL7 FHIR standards and IEEE 11073 Service-Oriented Device Connectivity (SDC), the repository and the corresponding (upcoming) publication contain a conceptual framework and a proof-of-concept implementation for real-time data integration within the Medical Data Integration Center (MeDIC) at UKSH.
## Description

This project is a Flask-based web application designed to consume, process, and display live data streams from Kafka topics. It utilizes XML parsing to extract ECG lead data, which is then dynamically plotted on a web interface. The application supports real-time data processing and visualization, making it suitable for monitoring and analysis in real-time environments.

## Features

- Real-time data streaming and processing from Kafka topics.
- Dynamic plotting of ECG leads data on a web interface.
- Support for multiple data channels and metrics.
- Real-time curve plotting and data visualization.

## Getting Started

### Dependencies

- Python 3.x


### Installing

1. Clone the repository to your local machine.
   ```
   git clone https://github.com/IMIS-MIKI/mice-data-capture
   ```
2. Install the required Python packages.
   ```
   conda env create -f environment.yml
   ```

### Running the Application

1. Start the Flask application.
   ```
   python app.py
   ```
2. Access the web interface at `http://localhost:5000`.

## Usage

Navigate to the home page to see the list of available ECG leads and data topics. Select a specific lead to view the real-time plotting of ECG data. You can also access detailed plots for individual data channels.
