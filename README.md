# RDBAlert
An Advanced tool to Extract Personally Identifiable Information (PII) of Ransomware leaks, specifically monitored through the crawler available at [breach.house](https://breach.house).
<p align="center">
  <img src="ruta/a/logo.jpeg" alt="Logo del proyecto" width="200"/>
</p>


## Introduction

This tool is specifically designed to process ransomware leaks and extract sensitive or PII data using advanced OCR methods, faces/Id cards/CV/Passports/Driver-license detection using YOLOv11 with a multimodal language model (MLLM) analysis. Its goal is to quickly identify exposed personal information following a leak.If you want to easily verify whether you or your organization have been victims of a leak, visit our public platform:
👉 [Have I been Ransomed?](https://haveibeenransom.com)

## Prerequisites

Before running the tool, ensure you have the following dependencies installed and correctly configured:

### 1. Elasticsearch

You must have an Elasticsearch server running locally.

-   **Installation**: [Elasticsearch Installation Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)

### 2. LibreOffice

Used for automatic document conversion.

-   **Installation**: [LibreOffice Official Site](https://www.libreoffice.org/download/download/)

### 3. YOLOv11 with WiderFaces

Used for face detection in images extracted from converted documents.

-   **Repository**: [YOLOv11 GitHub](https://github.com/ultralytics/ultralytics)
-   **Trained Datasheet**: [WIDERFACES](http://shuoyang1213.me/WIDERFACE/)

### 4. MLLM MiniCPM on Docker

Required for advanced multimodal document analysis.

-   **Repository**: [MiniCPM GitHub](https://github.com/OpenBMB/MiniCPM)

Make sure these services are running and properly configured before proceeding.

## Installation

Clone this repository:

```bash
git clone [<repository_URL>](https://github.com/juanmill4/RansomDBAlert.git)
cd RansomDBAlert/core
```

Install required dependencies:
```bash
pip3 install -r requirements.txt
```
## Usage

Download the ransomware leak you want to analyze and place it in a specific directory.

Run the main script using:
```bash
python process_all.py <directory_containing_leak>
```
This command will start the complete processing workflow, including:

- Automatic metadata extraction
- Document conversion and analysis
- Text and image extraction
- Id cards/Passports detection
- Indexing all gathered information into Elasticsearch

## Support

For support or additional questions about the use or setup of the tool, contact us at:

-   **Email**: [juanma@darkeye.io](mailto:juanma@darkeye.io)
