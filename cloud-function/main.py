import functions_framework
import json
import os
import base64
from datetime import datetime
from google.cloud import logging as cloud_logging
import requests

# Initialize Cloud Logging
logging_client = cloud_logging.Client()
logger = logging_client.logger('hamalert-receiver')

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO')  # Format: username/repo-name
GITHUB_API_URL = f'https://api.github.com/repos/{GITHUB_REPO}/contents/spots.json'

MAX_SPOTS = 50  # Keep the last 50 spots

@functions_framework.http
def hamalert_webhook(request):
    """
    Receives HamAlert webhook notifications and stores them in GitHub.
    """
    
    # Log the incoming request for debugging
    logger.log_struct({
        'message': 'Received HamAlert webhook',
        'method': request.method,
        'headers': dict(request.headers),
        'timestamp': datetime.utcnow().isoformat()
    })
    
    if request.method != 'POST':
        return ('Method not allowed', 405)
    
    try:
        # Get the spot data from the request
        # HamAlert sends data as URL-encoded form parameters
        spot_data = request.form.to_dict()
        
        # Add timestamp for when we received it
        spot_data['received_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Log the spot data
        logger.log_struct({
            'message': 'Spot data received',
            'spot': spot_data
        })
        
        # Update spots.json on GitHub
        update_github_spots(spot_data)
        
        return ('OK', 200)
        
    except Exception as e:
        logger.log_struct({
            'message': 'Error processing webhook',
            'error': str(e)
        }, severity='ERROR')
        return (f'Error: {str(e)}', 500)


def update_github_spots(new_spot):
    """
    Update the spots.json file on GitHub with the new spot.
    Keeps the most recent MAX_SPOTS spots.
    """
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Try to get existing file
        response = requests.get(GITHUB_API_URL, headers=headers)
        
        if response.status_code == 200:
            # File exists, decode and parse it
            file_data = response.json()
            content = base64.b64decode(file_data['content']).decode('utf-8')
            spots = json.loads(content)
            sha = file_data['sha']
        else:
            # File doesn't exist yet, start fresh
            spots = []
            sha = None
        
        # Add new spot at the beginning
        spots.insert(0, new_spot)
        
        # Keep only the most recent spots
        spots = spots[:MAX_SPOTS]
        
        # Prepare updated content
        updated_content = json.dumps(spots, indent=2)
        encoded_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')
        
        # Prepare commit data
        commit_data = {
            'message': f'Add spot: {new_spot.get("callsign", "unknown")} on {new_spot.get("frequency", "?")} MHz',
            'content': encoded_content,
            'branch': 'main'
        }
        
        if sha:
            commit_data['sha'] = sha
        
        # Update file on GitHub
        update_response = requests.put(GITHUB_API_URL, headers=headers, json=commit_data)
        
        if update_response.status_code in [200, 201]:
            logger.log_struct({
                'message': 'Successfully updated spots.json',
                'spots_count': len(spots)
            })
        else:
            logger.log_struct({
                'message': 'Failed to update GitHub',
                'status_code': update_response.status_code,
                'response': update_response.text
            }, severity='ERROR')
            
    except Exception as e:
        logger.log_struct({
            'message': 'Error updating GitHub',
            'error': str(e)
        }, severity='ERROR')
        raise
