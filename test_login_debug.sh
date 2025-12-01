#!/bin/bash

# Test script to debug first-load login issue
# This script tests the complete login flow

echo "🔐 Password Health Tracker - Login Debug Test"
echo "=============================================="
echo ""

# Check if backend URL is provided
BACKEND_URL="${1:-https://password-tracker-backend-681629792414.us-central1.run.app}"
FRONTEND_URL="${2:-http://localhost:3000}"

echo "Using Backend URL: $BACKEND_URL"
echo "Using Frontend URL: $FRONTEND_URL"
echo ""

# Test 1: Check if backend is accessible
echo "📋 Test 1: Checking if backend is accessible..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/health")
if [ "$HEALTH" = "200" ]; then
    echo "✅ Backend is accessible (HTTP $HEALTH)"
else
    echo "❌ Backend returned HTTP $HEALTH"
fi
echo ""

# Test 2: Check if config.json is accessible from frontend
echo "📋 Test 2: Checking if config.json is accessible..."
CONFIG=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/config.json")
if [ "$CONFIG" = "200" ]; then
    echo "✅ config.json is accessible (HTTP $CONFIG)"
else
    echo "❌ config.json returned HTTP $CONFIG"
fi
echo ""

# Test 3: Test CORS preflight request
echo "📋 Test 3: Testing CORS preflight for login..."
CORS=$(curl -s -X OPTIONS \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -o /dev/null -w "%{http_code}" \
  "$BACKEND_URL/api/auth/login")
if [ "$CORS" = "204" ] || [ "$CORS" = "200" ]; then
    echo "✅ CORS preflight successful (HTTP $CORS)"
else
    echo "❌ CORS preflight returned HTTP $CORS"
fi
echo ""

# Test 4: Test login with invalid credentials
echo "📋 Test 4: Testing login endpoint with invalid credentials..."
LOGIN=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"InvalidPass1!"}' \
  "$BACKEND_URL/api/auth/login")

if echo "$LOGIN" | grep -q "error"; then
    echo "✅ Login endpoint is responding: $(echo $LOGIN | jq -r '.error')"
else
    echo "✅ Login endpoint responded with: $(echo $LOGIN | jq -r '.message')"
fi
echo ""

echo "🔐 Debug tests complete!"
echo ""
echo "Next steps:"
echo "1. Check browser console (F12) for detailed logs"
echo "2. Check Network tab for request/response details"
echo "3. Check backend logs: docker logs <container_id>"
echo "4. If CORS preflight failed, CORS may not be configured correctly"
echo "5. If login endpoint failed, check authentication logic"
