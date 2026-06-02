# Turbify Presale Performance Testing

A JMeter-based performance testing framework integrated with Jenkins CI/CD for presale checkout flow validation on the Turbify platform.

## Project Overview

This framework automates performance and load testing of the Turbify presale APIs using Apache JMeter. It simulates real-world checkout flows — including CSRF token retrieval, user creation, cart management, product pricing, and promo validation — and integrates with Jenkins for scheduled and on-demand execution.

Results are streamed in real-time to an InfluxDB backend and visualized via Grafana dashboards.

---

## Folder Structure

```
presale-performance-testing/
│
├── API/
│   └── Presale_Thread.jmx        # JMeter test plan for presale checkout flow
│
├── scripts/
│   └── analyze_results.py        # Python script to parse and analyze JMeter results
│
├── results/                       # Output directory for .jtl result files (git-ignored)
│
├── .gitignore                     # Ignores results, logs, reports, and OS files
└── README.md                      # Project documentation
```

---

## APIs Covered in Test Plan

| Sampler              | Endpoint                              | Method |
|----------------------|---------------------------------------|--------|
| token                | api/csrf/token                        | GET    |
| create               | api/user/create                       | GET    |
| user                 | api/user                              | GET    |
| getcart_id           | api/ordering/cart                     | GET    |
| user/info            | api/user/info                         | GET    |
| products             | api/products                          | GET    |
| promo/requiresValidation | api/ordering/promo/requiresValidation | GET |
| pricing              | api/products/pricing                  | GET    |

---

## Running via Jenkins

### Prerequisites
- Apache JMeter 5.6+ installed on the Jenkins agent
- Jenkins with the **Performance Plugin** installed
- Java 11+ on the agent

### Jenkins Pipeline (Declarative)

```groovy
pipeline {
    agent any
    environment {
        JMETER_HOME = '/opt/jmeter'
        TEST_PLAN   = 'API/Presale_Thread.jmx'
        RESULTS_DIR = 'results'
    }
    stages {
        stage('Run JMeter Tests') {
            steps {
                sh '''
                    mkdir -p ${RESULTS_DIR}
                    ${JMETER_HOME}/bin/jmeter -n \
                        -t ${TEST_PLAN} \
                        -l ${RESULTS_DIR}/results.jtl \
                        -e -o ${RESULTS_DIR}/report
                '''
            }
        }
        stage('Analyze Results') {
            steps {
                sh 'python3 scripts/analyze_results.py'
            }
        }
        stage('Publish Report') {
            steps {
                perfReport sourceDataFiles: 'results/*.jtl'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'results/report/**', allowEmptyArchive: true
        }
    }
}
```

### Running Locally

```bash
# Run JMeter in non-GUI mode
$JMETER_HOME/bin/jmeter -n \
  -t API/Presale_Thread.jmx \
  -l results/results.jtl \
  -e -o results/report
```

---

## JMeter & Jenkins Integration

- **JMeter** executes the `.jmx` test plan in headless (non-GUI) mode during CI runs.
- **Jenkins** triggers the test on a schedule or on pull request via the pipeline above.
- **InfluxDB Backend Listener** in the test plan streams live metrics (response time, throughput, error rate) during test execution.
- **Grafana** connects to InfluxDB to display real-time dashboards.
- **Performance Plugin** in Jenkins archives `.jtl` files and generates trend reports across builds.

---

## Configuration

Before running, update the following in `API/Presale_Thread.jmx`:

| Parameter       | Location                  | Description                        |
|-----------------|---------------------------|------------------------------------|
| CSV file path   | CSVDataSet element        | Path to test data CSV file         |
| influxdbUrl     | Backend Listener          | InfluxDB endpoint URL              |
| influxdbToken   | Backend Listener          | InfluxDB authentication token      |
| Proxy host/port | HTTP Request Defaults     | Set to your environment proxy      |

---

## Thread Group Settings

| Property        | Value  |
|-----------------|--------|
| Threads         | 10     |
| Ramp-up (sec)   | 30     |
| Duration (sec)  | 300    |
| Loop            | ∞      |
