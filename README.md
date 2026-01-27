# Foresight-ML: Corporate Financial Distress Early-Warning System

**Foresight-ML** is an end-to-end MLOps initiative designed to predict corporate financial distress before it becomes irreversible. By leveraging historical financial data and machine learning, this system offers a dynamic alternative to static, lagging financial indicators.

---

## 1. Project Description

The current landscape of corporate financial health monitoring suffers from inefficiencies that lead to "surprise" bankruptcies and delayed interventions. This project addresses two core problems:

* **Latency in Detection:** Financial distress is typically identified only after official quarterly reports (10-Q/10-K) are released. By the time a report is analyzed, the company may have been in distress for months.
* **Static & Outdated Thresholds:** Traditional methods rely on rigid rules (e.g., "Debt-to-Equity > 2.0"). These fail to adapt to changing macroeconomic conditions, such as shifting interest rate environments or industry-specific nuances.

**Foresight-ML** solves this by treating financial distress as a time-series classification problem, updating risk scores in near real-time as new market data becomes available.

---

## 2. Dataset Sources

This project utilizes a combination of fundamental and market data. The raw data is versioned and managed using **DVC (Data Version Control)** to ensure reproducibility.

* **Primary Source:** Historical financial ratios and market data (e.g., stock prices, volatility) from public exchanges.
* **Data Management:**
    * Raw data is stored in remote object storage (S3/GCP bucket).
    * `dvc.yaml` defines the data pipeline stages (ingest, clean, split).
    * To access the data locally, you must have AWS/GCP credentials configured and run `dvc pull`.

---

## 3. Setup Instructions

Follow these steps to set up the development environment.

### Prerequisites
* Python 3.9+
* Docker & Terraform (for infrastructure)
* Git & DVC

### Installation
1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/sankalphegde/Foresight-ML.git](https://github.com/sankalphegde/Foresight-ML.git)
    cd Foresight-ML
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize Code Quality Hooks:**
    This project uses `pre-commit` to ensure code standards.
    ```bash
    pre-commit install
    ```

4.  **Pull Data:**
    Download the latest versioned dataset and model artifacts.
    ```bash
    dvc pull
    ```

5.  **Infrastructure Setup (Optional):**
    To provision the cloud resources defined in `infra/terraform`:
    ```bash
    cd infra/terraform
    terraform init
    terraform apply
    ```

---

## 4. Example Usage

You can interact with the system via the command line or by running the pipeline stages defined in the `Makefile`.

### Training the Model
To run the full training pipeline (preprocessing -> feature engineering -> training):
```bash
dvc repro

5. Output Interpretation
The model outputs a Distress Probability Score (DPS) ranging from 0.00 to 1.00.

Safe Zone (0.00 - 0.40): The company exhibits healthy financial patterns consistent with long-term stability.

Watchlist (0.41 - 0.70): Early signs of strain detected (e.g., declining liquidity combined with rising volatility). Recommended for manual analyst review.

High Risk (0.71 - 1.00): High probability of financial distress or bankruptcy within the next 12 months. Immediate intervention or hedging is advised.

6. Metrics & Objectives
We optimize the model based on the following key performance indicators (KPIs):

Primary Metric: Recall (Sensitivity)

Reasoning: In financial distress prediction, a False Negative (missing a bankruptcy) is much more costly than a False Positive (flagging a healthy company for review).

Secondary Metric: F1-Score

Ensures precision isn't entirely sacrificed for recall.

Business Objective: Detect distress signals at least 3 months prior to official default announcements.

7. Failure Analysis
To ensure reliability, the system monitors for:

Data Drift: Tracks input distributions (e.g., if global market volatility spikes, the model may need retraining).

Concept Drift: Monitors if the relationship between financial ratios and bankruptcy changes over time (e.g., post-COVID economics).

Fallback Strategy: If the model's confidence score is low (< 0.60), the system defaults to a rule-based "Watchlist" status and alerts a human analyst.

8. Deployment Infrastructure
Containerization: The application is fully Dockerized. The src/ code and requirements.txt are packaged into a lightweight image for consistency across environments.

Orchestration:

CI/CD: GitHub Actions handles automated testing (pytest) and linting.

Cloud: Infrastructure is provisioned using Terraform.

Data Storage:

Raw Data: Stored in S3/GCP Buckets (managed via DVC).

Feature Store: Processed features are versioned to ensure point-in-time correctness.
