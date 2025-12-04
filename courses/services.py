# courses/services.py
import subprocess
import tempfile
import os
import json
import uuid
from django.utils import timezone

class CodeExecutor:
    def __init__(self, timeout=10):
        self.timeout = timeout
    
    def execute_python(self, code, test_cases):
        """Execute Python code with test cases"""
        results = []
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Wrap the user code in a test harness
            test_code = f"""
{code}

# Test cases
test_results = []
try:
{self._generate_python_tests(test_cases)}
    print(json.dumps({{"status": "success", "results": test_results}}))
except Exception as e:
    print(json.dumps({{"status": "error", "message": str(e), "results": test_results}}))
"""
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Execute the code
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout.strip())
                return output
            else:
                return {
                    "status": "error",
                    "message": result.stderr,
                    "results": []
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": "Code execution timed out",
                "results": []
            }
        except json.JSONDecodeError:
            return {
                "status": "error", 
                "message": "Invalid output format",
                "results": []
            }
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def _generate_python_tests(self, test_cases):
        """Generate Python test cases from JSON"""
        test_code = ""
        for i, test_case in enumerate(test_cases):
            input_data = test_case.get('input', '')
            expected_output = test_case.get('expected_output', '')
            
            # Simple test case generation - you can extend this based on your needs
            test_code += f'    try:\n'
            test_code += f'        result = solution({input_data})\n'
            test_code += f'        test_results.append({{"test_case": {i + 1}, "input": "{input_data}", "expected": "{expected_output}", "actual": str(result), "passed": str(result) == "{expected_output}"}})\n'
            test_code += f'    except Exception as e:\n'
            test_code += f'        test_results.append({{"test_case": {i + 1}, "input": "{input_data}", "expected": "{expected_output}", "actual": f"Error: {{e}}", "passed": False}})\n'
        
        return test_code
    
    def execute_javascript(self, code, test_cases):
        """Execute JavaScript code with test cases"""
        # Similar implementation for JavaScript
        # You can use Node.js for server-side execution
        pass
    
    def evaluate_code(self, code, language, test_cases):
        """Evaluate code based on language"""
        if language == 'python':
            return self.execute_python(code, test_cases)
        elif language == 'javascript':
            return self.execute_javascript(code, test_cases)
        else:
            return {"status": "error", "message": f"Unsupported language: {language}"}