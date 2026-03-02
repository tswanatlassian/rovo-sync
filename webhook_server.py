#!/usr/bin/env python3
"""
Webhook Server for Real-Time Updates
Receives webhooks from Jira and triggers immediate sync

Deploy this to:
- Vercel (serverless)
- AWS Lambda
- Self-hosted server
- Any cloud platform with HTTPS endpoint
"""

import os
import json
import hmac
import hashlib
import logging
from flask import Flask, request, jsonify

from rovo_sync_orchestrator import webhook_handler, Config, setup_logging

# Initialize Flask app
app = Flask(__name__)
logger = setup_logging()

# Load config
try:
    config = Config()
except Exception as e:
    logger.error(f"Config error: {str(e)}")
    config = None

# ============================================================================
# WEBHOOK VERIFICATION
# ============================================================================

def verify_jira_webhook(request_data: bytes, signature: str) -> bool:
    """
    Verify Jira webhook signature
    
    Jira sends X-Hub-Signature header with HMAC-SHA256
    """
    if not config or not config.webhook_secret:
        logger.warning("No webhook secret configured - skipping verification")
        return True
    
    expected_signature = hmac.new(
        config.webhook_secret.encode(),
        request_data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, f"sha256={expected_signature}")

# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Rovo Sync Webhook Server",
        "version": "1.0.0"
    }), 200

@app.route('/webhook/jira', methods=['POST'])
def jira_webhook():
    """
    Jira webhook endpoint
    
    Receives webhooks for:
    - Issue updated (status change, comments, etc.)
    - Issue created
    - Issue deleted
    """
    logger.info("Jira webhook received")
    
    # Verify signature
    signature = request.headers.get('X-Hub-Signature')
    if signature and not verify_jira_webhook(request.data, signature):
        logger.warning("Invalid webhook signature")
        return jsonify({"error": "Invalid signature"}), 403
    
    # Parse webhook data
    try:
        event_data = request.json
        event_type = event_data.get('webhookEvent')
        
        logger.info(f"Event type: {event_type}")
        
        # Filter for events we care about
        if event_type in ['jira:issue_updated', 'jira:issue_created']:
            issue_key = event_data.get('issue', {}).get('key')
            changelog = event_data.get('changelog', {})
            
            # Check if this is a critical change
            is_critical = _is_critical_change(changelog)
            
            if is_critical:
                logger.info(f"Critical change detected for {issue_key}")
                # Process webhook
                result = webhook_handler(event_data)
                return jsonify(result), 200
            else:
                logger.info(f"Non-critical change for {issue_key} - will sync on next poll")
                return jsonify({"status": "queued"}), 200
        
        else:
            logger.info(f"Ignoring event type: {event_type}")
            return jsonify({"status": "ignored"}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

def _is_critical_change(changelog: dict) -> bool:
    """
    Determine if this is a critical change requiring immediate sync
    
    Critical changes:
    - Status changed to/from Blocked
    - Status changed to Done
    - New comment added (might contain decisions)
    """
    items = changelog.get('items', [])
    
    for item in items:
        field = item.get('field')
        from_string = item.get('fromString', '')
        to_string = item.get('toString', '')
        
        # Status changes
        if field == 'status':
            # Blocked or Done are critical
            if 'Blocked' in [from_string, to_string] or 'Done' in to_string:
                return True
        
        # Comments are potentially critical (decisions)
        if field == 'comment':
            return True
    
    return False

@app.route('/webhook/confluence', methods=['POST'])
def confluence_webhook():
    """
    Confluence webhook endpoint (optional)
    
    Could receive webhooks when planning pages are updated
    """
    logger.info("Confluence webhook received")
    
    try:
        event_data = request.json
        event_type = event_data.get('type')
        
        logger.info(f"Confluence event: {event_type}")
        
        # Could trigger sync if planning page is manually updated
        return jsonify({"status": "received"}), 200
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
