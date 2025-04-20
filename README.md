# RDBAlert
An Advanced tool to Extract Personally Identifiable Information (PII) of Ransomware leaks, specifically monitored through the crawler available at [breach.house](https://breach.house).

## Introduction

This tool is specifically designed to process ransomware leaks and extract sensitive or PII data using advanced OCR methods, face detection using YOLOv11 with a multimodal language model (MLLM) analysis. Its goal is to quickly identify exposed personal information following a leak.

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
Clone this repository:

```bash
git clone <repository_URL>
cd <repository_directory> ```bash

Install required dependencies:
