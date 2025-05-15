# Medical Certificate Issuance Support System

A Python-based expert system and simulation platform for managing medical certificate issuance in a clinical setting.

## Features

- User-friendly GUI for patient data entry and certificate management
- Expert system for automated decision support
- Clinic operation simulation for resource planning
- SQLite database for data persistence
- Logging system for audit trails
- Report generation capabilities

## Requirements

- Python 3.7+
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```bash
python main.py
```

The system provides:
- Patient information entry
- Automated certificate issuance recommendations
- Clinic simulation tools
- Statistical reporting

## Components

1. **Main Application** (`main.py`)
   - GUI interface
   - Database management
   - Form processing

2. **Expert System** (`expert_system.py`)
   - Rule-based decision making
   - Symptom severity assessment
   - Certificate issuance recommendations

3. **Simulation Engine** (`simulation.py`)
   - Clinic operation simulation
   - Resource utilization analysis
   - Performance metrics

## Database Schema

The system uses SQLite with the following main table:

```sql
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id TEXT NOT NULL,
    date_of_birth DATE,
    symptoms TEXT,
    diagnosis TEXT,
    certificate_issued BOOLEAN,
    date_issued DATETIME
)
```

## Logging

The system maintains logs in `medical_certificate.log` for:
- Certificate issuance events
- Expert system decisions
- Simulation runs
- Error tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 