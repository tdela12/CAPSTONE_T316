# Project Vantage – Capstone T316 (AutoGuru)

## 📖 Overview
Project Vantage is a solution developed as part of the QUT T316 Capstone Project with AutoGuru.  
This repository contains the backend, frontend, preprocessing pipeline, and training notebooks required to run and retrain models.  

This README provides a streamlined **quick start guide** for setup and operation.  

---

## ⚙️ Requirements

### Hardware
- Standard hardware is sufficient to run the backend and frontend locally.  
- For **model training**, stronger hardware is recommended. Training benchmarks (Ryzen 7 7700X):
  - **Log model:** ~26 mins  
  - **Capped model:** ~25 mins  
  - **Prescribed model:** ~5 mins  
  - **Repaired model:** ~66 mins  
---
### Software
Install the following before setup:
- [Python 3.12+](https://www.python.org/downloads/)  
- [pip](https://pip.pypa.io/en/stable/)  
- [Node.js 22+](https://nodejs.org/)  
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)  
- [Git](https://git-scm.com/downloads)  

Verify installation:
```
bash
python --version
pip --version
node -v
npm -v
git --version
```
---

## 📂 Cloning the Git and Data Setup
```
# Navigate to your desired directory & Clone repository
git clone https://github.com/tdela12/CAPSTONE_T316.git

cd CAPSTONE_T316

# Verify repository files
dir
```
---
## 📊 Data

### 1. Navigate to preprocessing
```
cd preprocessing
mkdir data
```

### 2. Download datasets from Google Drive:
- cpi_data.csv
- mid_data.xlsx
- registration_data.csv
- ticket_data.csv

### 3. Move datasets into ```preprocessing/data```

---
