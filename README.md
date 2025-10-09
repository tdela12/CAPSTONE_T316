<a id="readme-top"></a>




[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]




<br />
<div align="center" style="display:flex; justify-content:center; align-items:center; gap:40px; flex-wrap:wrap;">
  <!-- AutoGuru Logo -->
  <a href="https://www.autoguru.com.au">
    <img src="backend/static/logo.png" alt="AutoGuru Logo" height="90" style="width:auto; display:block;">
  </a>

  <div style="display:flex; justify-content:center; align-items:center; height:90px;">
    <img src="backend/static/X-logo.png" alt="X symbol" height="45" style="width:auto; display:block;">
  </div>

  <!-- QUT Logo -->
  <a href="https://www.qut.edu.au">
    <img src="backend/static/qut-logo-og-1200.png" alt="QUT Logo" height="90" style="width:auto; display:block;">
  </a>
</div>



<h3 align="center">Project Vantage</h3>

  <p align="left">
    This project, developed as part of the QUT T316 Capstone Project in collaboration with AutoGuru, focuses on designing and implementing a data-driven machine learning solution to enhance operational insights and automation. It combines robust data preprocessing, model development, and system integration within a structured solution architecture framework.
  </p>
  <p align="center">
    <br />
    <a href="https://github.com/tdela12/CAPSTONE_T316"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/tdela12/CAPSTONE_T316">View Demo</a>
    &middot;
    <a href="https://github.com/tdela12/CAPSTONE_T316/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/tdela12/CAPSTONE_T316/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributors">Contributors</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


This project, developed as part of the QUT T316 Capstone Project in collaboration with AutoGuru, focuses on designing and implementing a data-driven machine learning solution to enhance operational insights and automation. It combines robust data preprocessing, model development, and system integration within a structured solution architecture framework.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![React][React.js]][React-url]
* [![Python][Python.js]][Python-url]
* [![HTML][HTML.js]][HTML-url]
* [![JavaScript][JavaScript.js]][JavaScript-url]
* [![CSS][CSS.js]][CSS-url]
* [![FASTAPI][FASTAPI.js]][FASTAPI-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

Install the software listed above.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/tdela12/CAPSTONE_T316.git
   cd CAPSTONE_T316
   ```
2. Install Python dependencies (from project root):
   ```sh
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```sh
   cd frontend
   npm install
   cd ..  
   ```
4. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin tdela12/CAPSTONE_T316
   git remote -v # confirm the changes
   ```
5. For more information on the installation refer to the Quick Start Guide

<p align="right">(<a href="#readme-top">back to top</a>)</p>




## Usage

Once the project is set up, you can start both backend and frontend to test the full application.

1. Running the Backend
   ```sh
   cd backend
   uvicorn main:app --reload
   ```
   Verify Server is running by accessing swagger docs at  http://127.0.0.1:8000/docs

2. Running the Frontend
   ```sh
   cd frontend
   npm run dev 
   ```
   Interact with the front end at http://localhost:5173/ 


<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Roadmap

- [x] Initial project setup
- [x] Backend API using FastAPI
- [x] Frontend using React
- [x] Data preprocessing pipeline
- [x] Machine learning model development
- [x] Integration of ML model with frontend dashboard
- [x] Deployment instructions and documentation
- [x] Unit and integration testing
- [ ] AutoGuru internal testing of Product
- [ ] Integration with AutoGuru Platfrom
- [ ] Deployment to Production

See the [open issues](https://github.com/tdela12/CAPSTONE_T316/issues) for a full list of proposed features and known issues.


<p align="right">(<a href="#readme-top">back to top</a>)</p>




## Contributors:

<a href="https://github.com/tdela12/CAPSTONE_T316/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=tdela12/CAPSTONE_T316" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Capstone Team - projectvantagequt@gmail.com

Project Link: [https://github.com/tdela12/CAPSTONE_T316](https://github.com/tdela12/CAPSTONE_T316)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Acknowledgments

* [QUT T316 Capstone Program](https://www.qut.edu.au/study/unit?unitCode=IFB399) – For providing the course structure and support throughout the project.
* [AutoGuru](https://www.autoguru.com.au) – For collaborating on the project and providing domain knowledge and data access.
* [Open Source Libraries & Tools](https://github.com/tdela12/CAPSTONE_T316) – For making development faster and easier, including React, FastAPI, and Python libraries.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/tdela12/CAPSTONE_T316.svg?style=for-the-badge
[contributors-url]: https://github.com/tdela12/CAPSTONE_T316/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/tdela12/CAPSTONE_T316.svg?style=for-the-badge
[forks-url]: https://github.com/tdela12/CAPSTONE_T316/network/members
[stars-shield]: https://img.shields.io/github/stars/tdela12/CAPSTONE_T316.svg?style=for-the-badge
[stars-url]: https://github.com/tdela12/CAPSTONE_T316/stargazers
[issues-shield]: https://img.shields.io/github/issues/tdela12/CAPSTONE_T316.svg?style=for-the-badge
[issues-url]: https://github.com/tdela12/CAPSTONE_T316/issues
<!-- Shields.io badges. You can a comprehensive list with many more badges at: https://github.com/inttter/md-badges -->
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Python.js]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=fff
[Python-url]: https://www.python.org/
[HTML.js]: https://img.shields.io/badge/HTML-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white
[HTML-url]: https://developer.mozilla.org/en-US/docs/Web/HTML
[JavaScript.js]: https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=000
[JavaScript-url]: https://developer.mozilla.org/en-US/docs/Web/JavaScript
[CSS.js]: https://img.shields.io/badge/CSS-639?style=for-the-badge&logo=css&logoColor=fff
[CSS-url]: https://developer.mozilla.org/en-US/docs/Web/CSS
[FASTAPI.js]: https://img.shields.io/badge/FastAPI-009485.svg?style=for-the-badge&logo=fastapi&logoColor=white
[FASTAPI-url]: https://fastapi.tiangolo.com/
