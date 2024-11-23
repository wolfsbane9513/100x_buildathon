import subprocess
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ModelStatus:
    @staticmethod
    def check_model_status(model_name: str) -> Dict[str, Any]:
        """Check status and details of a specific model."""
        try:
            # Get model details
            show_result = subprocess.run(
                ['ollama', 'show', model_name],
                capture_output=True,
                text=True
            )
            
            # Get model size and modified date
            list_result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True
            )
            
            status = {
                'available': show_result.returncode == 0,
                'details': {},
                'size': None,
                'modified': None
            }
            
            # Parse show output
            if show_result.returncode == 0:
                lines = show_result.stdout.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        status['details'][key.strip()] = value.strip()
            
            # Parse list output for size and modified date
            if list_result.returncode == 0:
                lines = list_result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if parts and parts[0] == model_name:
                        if len(parts) > 2:
                            status['size'] = parts[2]
                        if len(parts) > 3:
                            status['modified'] = ' '.join(parts[3:])
            
            return status
            
        except Exception as e:
            logger.error(f"Error checking model status: {str(e)}")
            return {'available': False, 'error': str(e)}

    @staticmethod
    def list_models() -> Dict[str, Dict[str, Any]]:
        """List all available Ollama models with details."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True
            )
            
            models = {}
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 4:
                        model_name = parts[0]
                        models[model_name] = {
                            'id': parts[1],
                            'size': parts[2],
                            'modified': ' '.join(parts[3:]),
                            'status': ModelStatus.check_model_status(model_name)
                        }
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return {}