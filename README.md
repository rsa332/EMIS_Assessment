git#FHIR Data Processing Pipeline
This project is a containerized ETL pipeline that extracts, transforms, and loads (ETL) FHIR (Fast Healthcare Interoperability Resources) data into a PostgreSQL database. It dynamically extracts Patient, Encounter, and Condition resources and transforms them into a structured format for analysis.

## Installation

### Prerequisites

Ensure you have the following installed:

1. **Docker** (for containerization)
2. **PostgreSQL** (for database setup, if running locally outside of Docker)
3. **Python 3.x** (for running the pipeline locally)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/EMIS_Assessment.git
   cd EMIS_Assessment
2. **Set up your environment:**
   ```bash
   pip install -r requirements.txt
3. **Set up PostgreSQL (optional):**
   If you’re running PostgreSQL locally, ensure the database is set up with the appropriate configurations. Alternatively, you can use Docker to run PostgreSQL using docker-compose.
4. **Create a .env file:**
   Create a .env file in the root directory with the content as shown in scripts/.env.example. This file will hold the environment variables for connecting to your PostgreSQL database. Example contents:
   DB_HOST=db
   DB_PORT=5432
   DB_NAME=fhir_db
   DB_USER=postgres
   DB_PASSWORD=rishav
5. **Run Docker Containers (optional):**
   If you want to use Docker to run PostgreSQL and the pipeline. It will start the containers as specified in docker-compose.yml. It will set up both the database and the pipeline in separate containers.
   ```bash
   docker-compose up -d --build
6. **Run the pipeline locally:**
   After activating virtual environment and installing the packages you can run python scripts/main.py
7. **Verify Data in PostgreSQL:**
   Once the pipeline is executed, you can connect to the PostgreSQL database or use pgADMIN to verify the data:
   You can execute the below if you are using docker ((Replace user_name and db name as per your requirement))
   ```bash
   docker exec -it fhir_db psql -U postgres -d fhir_db
8. **Query the Data:**
   SELECT * FROM patient;
   SELECT * FROM condition;
   SELECT * FROM encounter;

## How to Use the Results
Once the data is loaded into the PostgreSQL database, it can be queried for analysis, visualization, and reporting. Use SQL queries or connect your analytics tools (e.g., Power BI, Tableau) to the database for reporting.

##Architecture
The solution consists of the following components:

###Data Extraction:
FHIR data is read from JSON files available in data folder and extracted as df based on resource type like patient, encounter, condition etc.

###Data Transformation:
The transformation is done in the transform.py script, which processes the data into a clean tabular format.

###Data Loading:
The processed data is then loaded into the PostgreSQL database using database_handler.py. 

###Containerization (optional):
The solution can be containerized using Docker to isolate dependencies and ensure portability. A PostgreSQL container is available to simplify the setup.

##Testing
The project includes unit and integration tests for individual components to ensure the correct functionality of key modules. You can run the tests using pytest tests/.
