import simpy
import random
import logging
from datetime import datetime, timedelta
from expert_system import analyze_case
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ClinicConfig:
    """Configuration for clinic simulation"""
    OPENING_TIME: str = "08:30"
    CLOSING_TIME: str = "17:00"
    MAX_NURSES: int = 3
    MAX_DOCTORS: int = 1
    MAX_STAFF: int = 1
    NURSE_PROCESS_TIME: int = 10  # minutes
    DOCTOR_PROCESS_TIME: int = 15  # minutes
    STAFF_PROCESS_TIME: int = 5   # minutes

class Student:
    """Represents a student requesting a medical certificate"""
    def __init__(self, id: int, arrival_time: float):
        self.id = id
        self.arrival_time = arrival_time
        # 80% have excuse letters, 90% of those have valid IDs
        self.has_excuse_letter = random.random() > 0.2
        self.has_valid_id = random.random() > 0.1 if self.has_excuse_letter else False
        self.case_details = self._generate_case()
        self.process_times = {
            'wait_start': 0,
            'nurse_start': 0,
            'doctor_start': 0,
            'completion': 0
        }

    def _generate_case(self) -> Dict[str, Any]:
        """Generate a random case for the student"""
        try:
            symptoms = self._generate_symptoms()
            return {
                'student_id': f"S{self.id:04d}",
                'has_excuse_letter': self.has_excuse_letter,
                'valid_id': self.has_valid_id,
                'symptoms': symptoms,
                'illness_type': 'complex' if len(symptoms) > 2 else 'simple',
                'timestamp': datetime.now(),
                'parent_guardian_verified': self.has_valid_id
            }
        except Exception as e:
            logging.error(f"Error generating case: {str(e)}")
            return {
                'student_id': f"S{self.id:04d}",
                'has_excuse_letter': False,
                'valid_id': False,
                'symptoms': ['unknown'],
                'illness_type': 'unknown',
                'timestamp': datetime.now(),
                'parent_guardian_verified': False
            }

    def _generate_symptoms(self) -> List[str]:
        """Generate a list of symptoms with weighted probabilities"""
        simple_symptoms = [
            'cold', 'flu', 'cough', 'headache', 
            'fever', 'stomach ache', 'sore throat'
        ]
        complex_symptoms = [
            'recurring fever', 'severe injury', 'chronic pain',
            'mental health issues', 'surgery recovery', 'infectious disease'
        ]
        
        # 70% chance of simple symptoms
        if random.random() < 0.7:
            num_symptoms = random.randint(1, 3)
            return random.sample(simple_symptoms, num_symptoms)
        else:
            # Complex case: mix of simple and complex symptoms
            num_simple = random.randint(0, 2)
            num_complex = random.randint(1, 2)
            symptoms = random.sample(simple_symptoms, num_simple)
            symptoms.extend(random.sample(complex_symptoms, num_complex))
            return symptoms

class ClinicSimulation:
    """Main simulation class for the medical certificate system"""
    def __init__(self, env: simpy.Environment, config: ClinicConfig, callback=None):
        self.env = env
        self.config = config
        self.callback = callback
        
        # Resources
        self.nurses = simpy.Resource(env, capacity=config.MAX_NURSES)
        self.doctors = simpy.Resource(env, capacity=config.MAX_DOCTORS)
        self.staff = simpy.Resource(env, capacity=config.MAX_STAFF)
        
        # Statistics
        self.stats = {
            'total_students': 0,
            'certificates_issued': 0,
            'students_in_system': 0,
            'total_wait_time': 0,
            'nurse_utilization': 0,
            'doctor_utilization': 0,
            'nurse_decisions': {'refer': 0, 'treat': 0},
            'doctor_decisions': {'issue': 0, 'deny': 0},
            'peak_hour_visits': 0,
            'off_peak_visits': 0,
            'simple_cases': 0,
            'complex_cases': 0
        }
        
        # Peak hours definition
        self.peak_hours = [
            (10, 11.5),  # 10:00 AM - 11:30 AM
            (13.5, 17)   # 1:30 PM - 5:00 PM
        ]

    def is_peak_hour(self, time: float) -> bool:
        """Check if current time is during peak hours"""
        current_hour = (time / 60) % 24
        return any(start <= current_hour <= end for start, end in self.peak_hours)

    def get_arrival_rate(self) -> float:
        """Get student arrival rate based on time of day"""
        try:
            current_hour = (self.env.now / 60) % 24
            if self.is_peak_hour(current_hour):
                return random.uniform(5, 10)  # One student every 5-10 minutes
            return random.uniform(15, 25)     # One student every 15-25 minutes
        except Exception as e:
            logging.error(f"Error calculating arrival rate: {str(e)}")
            return 20  # Default to moderate arrival rate

    def process_student(self, student: Student):
        """Process a student through the clinic system"""
        arrival_time = self.env.now
        student.process_times['wait_start'] = arrival_time
        self.stats['students_in_system'] += 1
        
        # Track peak/off-peak visits
        if self.is_peak_hour(arrival_time / 60):
            self.stats['peak_hour_visits'] += 1
        else:
            self.stats['off_peak_visits'] += 1
        
        # Notify arrival
        self.notify_event("student", {
            'id': student.id,
            'action': 'arrived',
            'time': self.format_time(arrival_time),
            'has_excuse_letter': student.has_excuse_letter,
            'has_valid_id': student.has_valid_id
        })
        
        # Nurse Assessment
        with self.nurses.request() as nurse:
            yield nurse
            student.process_times['nurse_start'] = self.env.now
            
            # Add visualization delay
            yield self.env.timeout(1.5)
            
            # Process through expert system
            nurse_result = analyze_case(student.case_details)
            yield self.env.timeout(self.config.NURSE_PROCESS_TIME)
            
            if nurse_result['decision'] == 'reject':
                self.stats['nurse_decisions']['refer'] += 1
                self.complete_student(student, 'rejected_by_nurse', nurse_result['reason'])
                return
            
            self.stats['nurse_decisions']['treat'] += 1
            
            # Track case complexity
            if nurse_result.get('complexity') == 'complex':
                self.stats['complex_cases'] += 1
            else:
                self.stats['simple_cases'] += 1
            
            # Doctor consultation if needed
            if nurse_result.get('decision') == 'refer' or nurse_result.get('complexity') == 'complex':
                with self.doctors.request() as doctor:
                    yield doctor
                    student.process_times['doctor_start'] = self.env.now
                    
                    # Add visualization delay
                    yield self.env.timeout(1.5)
                    
                    doctor_result = analyze_case(student.case_details)
                    yield self.env.timeout(self.config.DOCTOR_PROCESS_TIME)
                    
                    if doctor_result['decision'] == 'reject':
                        self.stats['doctor_decisions']['deny'] += 1
                        self.complete_student(student, 'rejected_by_doctor', doctor_result['reason'])
                        return
                    elif doctor_result['decision'] == 'approve':
                        self.stats['doctor_decisions']['issue'] += 1
            
            # Final processing by clinic staff
            with self.staff.request() as staff:
                yield staff
                yield self.env.timeout(self.config.STAFF_PROCESS_TIME)
                
                # Add visualization delay
                yield self.env.timeout(1.5)
                
                self.stats['certificates_issued'] += 1
                self.complete_student(student, 'certificate_issued', 
                                   f"Approved by {'doctor' if nurse_result.get('complexity') == 'complex' else 'nurse'}")

    def complete_student(self, student: Student, status: str, reason: str = ""):
        """Complete student processing and update statistics"""
        student.process_times['completion'] = self.env.now
        wait_time = student.process_times['completion'] - student.process_times['wait_start']
        self.stats['total_wait_time'] += wait_time
        self.stats['students_in_system'] -= 1
        
        self.notify_event("completion", {
            'id': student.id,
            'status': status,
            'reason': reason,
            'wait_time': wait_time,
            'total_time': self.env.now - student.arrival_time
        })
        
        self.update_statistics()

    def format_time(self, minutes: float) -> str:
        """Format simulation time as HH:MM"""
        try:
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours:02d}:{mins:02d}"
        except Exception as e:
            logging.error(f"Error formatting time: {str(e)}")
            return "00:00"  # Return default time on error

    def notify_event(self, event_type: str, data: Dict[str, Any]):
        """Send event notification through callback"""
        try:
            if self.callback:
                self.callback(event_type, data)
        except Exception as e:
            logging.error(f"Error in event notification: {str(e)}")

    def update_statistics(self):
        """Update and notify current statistics"""
        if self.callback:
            avg_wait_time = (
                self.stats['total_wait_time'] / 
                max(1, self.stats['total_students'])
            )
            
            self.callback("stats", {
                'Patients in System': self.stats['students_in_system'],
                'Waiting for Nurse': 0,
                'Waiting for Doctor': 0,
                'Certificates Issued': self.stats['certificates_issued'],
                'Average Wait': avg_wait_time,
                'Success Rate': (
                    self.stats['certificates_issued'] / 
                    max(1, self.stats['total_students']) * 100
                ),
                'Patients Seen': self.stats['total_students'],
                'Peak Hour Rate': (
                    self.stats['peak_hour_visits'] /
                    max(1, self.stats['total_students']) * 100
                ),
                'Case Complexity': {
                    'Simple': self.stats['simple_cases'],
                    'Complex': self.stats['complex_cases']
                }
            })

def run_simulation(duration_hours=8, num_doctors=1, num_nurses=3, event_callback=None, config=None):
    """Run the clinic simulation"""
    try:
        # Initialize simulation
        env = simpy.Environment()
        if config is None:
            config = ClinicConfig(
                MAX_DOCTORS=num_doctors,
                MAX_NURSES=num_nurses
            )
        clinic = ClinicSimulation(env, config, event_callback)
        
        def student_generator(env, clinic):
            student_id = 0
            while True:
                # Get next arrival time based on current hour
                yield env.timeout(clinic.get_arrival_rate())
                student_id += 1
                clinic.stats['total_students'] += 1
                
                # Create and process new student
                student = Student(student_id, env.now)
                env.process(clinic.process_student(student))
        
        # Start student generation
        env.process(student_generator(env, clinic))
        
        # Run simulation
        env.run(until=duration_hours * 60)
        
        # Prepare final statistics
        final_stats = {
            'total_patients': clinic.stats['total_students'],
            'patients_seen': clinic.stats['total_students'],
            'certificates_issued': clinic.stats['certificates_issued'],
            'average_wait_time': (
                clinic.stats['total_wait_time'] / 
                max(1, clinic.stats['total_students'])
            ),
            'certificate_issuance_rate': (
                clinic.stats['certificates_issued'] / 
                max(1, clinic.stats['total_students']) * 100
            ),
            'simulation_duration_hours': duration_hours,
            'num_doctors': num_doctors,
            'num_nurses': num_nurses,
            'nurse_decisions': clinic.stats['nurse_decisions'],
            'doctor_decisions': clinic.stats['doctor_decisions'],
            'simple_cases': clinic.stats['simple_cases'],
            'complex_cases': clinic.stats['complex_cases'],
            'peak_hour_visits': clinic.stats['peak_hour_visits'],
            'off_peak_visits': clinic.stats['off_peak_visits']
        }
        
        return final_stats
        
    except Exception as e:
        print(f"Simulation error: {str(e)}")
        return {
            'error': str(e),
            'total_patients': 0,
            'patients_seen': 0,
            'certificates_issued': 0,
            'average_wait_time': 0,
            'certificate_issuance_rate': 0,
            'simulation_duration_hours': duration_hours,
            'num_doctors': num_doctors,
            'num_nurses': num_nurses,
            'nurse_decisions': {'refer': 0, 'treat': 0},
            'doctor_decisions': {'issue': 0, 'deny': 0},
            'simple_cases': 0,
            'complex_cases': 0,
            'peak_hour_visits': 0,
            'off_peak_visits': 0
        } 