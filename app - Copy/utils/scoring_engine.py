import json

class ScoringEngine:
    def __init__(self):
        pass

    def calculate_application_score(self, details_json):
        """
        Calculates score based on application form answers.
        Heuristic:
        - Work Permit: Yes (+50)
        - Visa Help: No (+20)
        - Experience: (Simple length check or keyword, here just base score)
        Let's assume base 30 + dynamic.
        """
        score = 0
        try:
            details = json.loads(details_json) if isinstance(details_json, str) else details_json
            
            # Work Permit Rule
            if details.get('work_permit') == 'Yes':
                score += 50
            
            # Visa Help Rule (Preferred: No)
            if details.get('visa_help') == 'No':
                score += 30
            elif details.get('visa_help') == 'Yes':
                score += 10 # Little simplified
                
            # Education (Bonus using rough matching if education is passed separate, 
            # but usually it's in the main row. Assuming details has it if we put it there.
            # For now, let's treat the remaining 20 points as base.)
            score += 20
            
        except Exception as e:
            print(f"Error parsing details: {e}")
            score = 50 # Default safe score
            
        return min(score, 100)

    def calculate_final_score(self, ats_score, assessment_score, app_score):
        """
        Formula:
        final = 0.4 * Resume(ATS) + 0.3 * App + 0.3 * Assessment
        """
        # Ensure values are floats
        ats = float(ats_score or 0)
        asm = float(assessment_score or 0)
        app = float(app_score or 0)
        
        final = (0.4 * ats) + (0.3 * app) + (0.3 * asm)
        return round(final, 2)
