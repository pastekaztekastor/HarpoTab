#!/bin/bash
# Test SSE simple

# Upload
echo "Uploading file..."
LOCATION=$(curl -s -v -X POST -F "file=@Test_EndToEnd1.jpg" -F "harmonica_type=diatonic" -F "harmonica_key=C" http://localhost:5000/convert 2>&1 | grep "Location:" | awk '{print $3}')
echo "Location: $LOCATION"

# Extract session ID
SESSION_ID=$(echo "$LOCATION" | grep -oP 'session_id=\K[^&]+')
echo "Session ID: $SESSION_ID"

# Test SSE
echo "Testing SSE..."
timeout 10 curl -N "http://localhost:5000/progress/$SESSION_ID" 2>&1 | head -20

echo ""
echo "Checking logs..."
tail -20 /tmp/flask.log | grep -E "(SSE|Error|Status)"
