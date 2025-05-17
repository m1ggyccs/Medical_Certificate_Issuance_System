# 🏥 TIP Clinic Simulation Project

A simulation-based comparative analysis of patient certificate processing efficiency in the **Technological Institute of the Philippines (TIP) Clinic**, using **Agent-Based Simulation (ABS)** and **Survey-Based Simulation (SBS)**.

---

## 🎯 Objective

To evaluate and compare the performance of Agent-Based and Survey-Based models in managing clinic resources and patient flows, aiming to:

- Reduce wait times
- Increase certificate issuance success rates
- Optimize clinic staffing decisions

---

## ⚙️ Simulation Parameters

| Parameter              | Value        |
|------------------------|--------------|
| **Doctors**            | 1            |
| **Nurses**             | 3            |
| **Clinic Duration**    | 8 hours      |
| **Nurse Inquiry Time** | 5 minutes    |
| **Simple Case Time**   | 3 minutes    |
| **Complex Case Time**  | 10 minutes   |
| **Finalization Time**  | 2 minutes    |

---

## 🧪 Methodology

### Agent-Based Simulation (ABS)

Simulates individual interactions between patients and clinic staff to model realistic, dynamic behaviors.

### Survey-Based Simulation (SBS)

Utilizes statistical averages from surveys to model clinic operations with simplified assumptions.

Each scenario (Best, Average, Worst) is tested with **5 simulation runs** for both models.

---

## 📈 Key Metrics Evaluated

- **Total Patients Seen**
- **Certificates Issued**
- **Average Wait Time**
- **Certificate Success Rate**

---

## 📊 Results Summary

| Scenario   | ABS Avg Wait Time | SBS Avg Wait Time | ABS Success Rate | SBS Success Rate |
|------------|-------------------|-------------------|------------------|------------------|
| Best Case  | ~6.3 mins         | ~15.7 mins        | ~73%             | ~68%             |
| Average    | ~9.0 mins         | ~15.5 mins        | ~74%             | ~67%             |
| Worst Case | ~12.7 mins        | ~15.6 mins        | ~66%             | ~62%             |

---

## 💡 Key Insights

- **ABS consistently outperforms SBS** in terms of average wait times and certificate success rates.
- ABS provides more realistic and adaptive behavior modeling.
- SBS offers simplicity and speed but lacks dynamic interaction depth.
- Results can inform clinic staffing and policy decisions.

---

## 📁 Repository Structure

📁 Medical-Certificate-Issuance-System/
├── main.py # Entry point for running simulations
├── simulation.py # Core simulation logic for agent-based and survey-based models
├── expert_system.py # Rules for handling medical cases
├── expert_system_demo.py # Demo to showcase expert system separately
├── predefined_cases.py # Predefined patient cases for simulation
├── medical_certificate # Sample data and case templates (text format)
├── requirements # Required Python packages (txt format)
├── README.md # This documentation file
├── .gitattributes # Git configuration
└── pycache/ # Python cache folder (auto-generated)
---

## 🚀 How to Use

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/clinic-simulation-project.git
   cd clinic-simulation-project

📜 License
This project is licensed under the MIT License.

👥 Contributors
m1ggycss - mamdavid@tip.edu.ph

Course: Modeling and Simulation and Expert System

Institution: Technological Institute of the Philippines

📬 Contact
For inquiries, suggestions, or collaborations, feel free to open an issue or reach out via email.

