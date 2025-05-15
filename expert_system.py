import logging
from typing import Dict, List, Any
from datetime import datetime

class Blackboard:
    """Shared knowledge space for the expert system"""
    def __init__(self):
        self.facts = {
            'student_id': None,
            'has_excuse_letter': False,
            'symptoms': [],
            'illness_type': None,
            'timestamp': None,
            'valid_id': False,
            'parent_guardian_verified': False
        }
        self.intermediate_decisions = {
            'nurse_assessment': None,
            'doctor_review': None,
            'final_decision': None
        }
        self.case_history = []

class ExpertSource:
    def __init__(self, name):
        self.name = name
        self.confidence_threshold = 0.7

    def can_handle(self, facts):
        raise NotImplementedError("Expert source must implement can_handle")

    def evaluate(self, facts):
        raise NotImplementedError("Expert source must implement evaluate")

class NurseExpert(ExpertSource):
    def __init__(self):
        super().__init__("Nurse")
        self.simple_cases = {
            'cold', 'flu', 'cough', 'headache', 
            'fever', 'stomach_ache', 'sore throat'
        }

    def can_handle(self, facts):
        return facts['has_excuse_letter'] and facts['student_id']

    def evaluate(self, facts):
        # Rule 1: No excuse letter or invalid ID
        if not facts['has_excuse_letter'] or not facts['valid_id']:
            return {
                'decision': 'reject',
                'reason': 'No valid excuse letter or ID',
                'complexity': 'simple'
            }
        
        # Rule 2: Simple illness with valid documentation
        illness_complexity = self._determine_complexity(facts['symptoms'])
        if illness_complexity == 'simple':
            return {
                'decision': 'approve',
                'reason': 'Simple case with valid documentation',
                'complexity': 'simple'
            }
        
        # Rule 3: Complex case needs doctor review
        return {
            'decision': 'refer',
            'reason': 'Complex case needs doctor review',
            'complexity': 'complex'
        }

    def _determine_complexity(self, symptoms):
        if any(symptom.lower() in self.simple_cases for symptom in symptoms):
            return 'simple'
        return 'complex'

class DoctorExpert(ExpertSource):
    def __init__(self):
        super().__init__("Doctor")
        self.complex_conditions = {
            'recurring fever', 'severe injury', 'chronic pain',
            'mental health', 'surgery recovery', 'infectious disease'
        }

    def can_handle(self, facts):
        return facts['has_excuse_letter'] and facts['illness_type'] == 'complex'

    def evaluate(self, facts):
        # Rule 4: Doctor's evaluation for complex cases
        if not self._validate_documentation(facts):
            return {
                'decision': 'reject',
                'reason': 'Insufficient documentation for complex case'
            }

        severity = self._assess_severity(facts['symptoms'])
        if severity >= self.confidence_threshold:
            return {
                'decision': 'approve',
                'reason': 'Complex case validated and approved',
                'severity': severity
            }
        return {
            'decision': 'reject',
            'reason': 'Condition does not warrant certificate'
        }

    def _validate_documentation(self, facts):
        return (facts['has_excuse_letter'] and 
                facts['valid_id'] and 
                len(facts['symptoms']) > 0)

    def _assess_severity(self, symptoms):
        severe_symptoms = sum(1 for s in symptoms 
                            if any(c in s.lower() for c in self.complex_conditions))
        return severe_symptoms / max(1, len(symptoms))

class ClinicStaffExpert(ExpertSource):
    def __init__(self):
        super().__init__("Clinic Staff")
        self.required_fields = {
            'student_id', 'symptoms', 'timestamp',
            'has_excuse_letter', 'valid_id'
        }

    def can_handle(self, facts):
        return all(field in facts for field in self.required_fields)

    def evaluate(self, facts):
        # Rule 5: Record keeping for approved cases
        if not self._validate_fields(facts):
            return {
                'decision': 'reject',
                'reason': 'Missing required information for record'
            }
        
        return {
            'decision': 'record',
            'reason': 'Case recorded in system',
            'record_id': self._generate_record_id(facts),
            'record_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _validate_fields(self, facts):
        return all(facts.get(field) for field in self.required_fields)

    def _generate_record_id(self, facts):
        return f"MC-{facts['student_id']}-{facts['timestamp'].strftime('%Y%m%d%H%M')}"

class ControlShell:
    def __init__(self):
        self.blackboard = Blackboard()
        self.experts = {
            'nurse': NurseExpert(),
            'doctor': DoctorExpert(),
            'staff': ClinicStaffExpert()
        }

    def process_case(self, case_data):
        """Process a medical certificate case through the expert system."""
        try:
            # Initialize blackboard with case data
            self.blackboard.facts.update(case_data)
            
            # Add default valid_id if not provided (for compatibility)
            if 'valid_id' not in self.blackboard.facts:
                self.blackboard.facts['valid_id'] = True
            
            # Step 1: Nurse Assessment
            nurse_decision = self.experts['nurse'].evaluate(self.blackboard.facts)
            self.blackboard.intermediate_decisions['nurse_assessment'] = nurse_decision

            if nurse_decision['decision'] == 'reject':
                self.blackboard.intermediate_decisions['final_decision'] = nurse_decision
                return nurse_decision

            # Step 2: Doctor Review (if needed)
            if nurse_decision['decision'] == 'refer' or nurse_decision.get('complexity') == 'complex':
                doctor_decision = self.experts['doctor'].evaluate(self.blackboard.facts)
                self.blackboard.intermediate_decisions['doctor_review'] = doctor_decision
                if doctor_decision['decision'] == 'reject':
                    self.blackboard.intermediate_decisions['final_decision'] = doctor_decision
                    return doctor_decision

            # Step 3: Clinic Staff Recording
            staff_decision = self.experts['staff'].evaluate(self.blackboard.facts)
            if staff_decision['decision'] == 'record':
                final_decision = {
                    'decision': 'approve',
                    'record_id': staff_decision['record_id'],
                    'approved_by': 'nurse' if nurse_decision['complexity'] == 'simple' else 'doctor'
                }
            else:
                final_decision = staff_decision

            self.blackboard.intermediate_decisions['final_decision'] = final_decision
            self.blackboard.case_history.append({
                'facts': self.blackboard.facts.copy(),
                'decisions': self.blackboard.intermediate_decisions.copy()
            })
            
            return final_decision
            
        except Exception as e:
            logging.error(f"Error in expert system: {str(e)}")
            return {
                'decision': 'reject',
                'reason': f'System error: {str(e)}',
                'complexity': 'unknown'
            }

def analyze_case(case_data):
    """Main interface for the expert system."""
    try:
        control = ControlShell()
        return control.process_case(case_data)
    except Exception as e:
        logging.error(f"Expert system error: {str(e)}")
        return {
            'decision': 'reject',
            'reason': f'System error: {str(e)}',
            'complexity': 'unknown'
        } 