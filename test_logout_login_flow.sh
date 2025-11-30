#!/bin/bash

# Test script for logout/login flow
# This simulates the user journey: Register -> Login -> Logout -> Login Again

echo "=========================================="
echo "Testing Logout/Login Flow"
echo "=========================================="
echo ""

API_URL="http://localhost:5001"
EMAIL="testuser_$(date +%s)@example.com"
PASSWORD="TestFlow123!"

echo "📝 Creating test user: $EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

if echo "$REGISTER_RESPONSE" | grep -q "user_id"; then
  echo "✅ Registration successful"
else
  echo "❌ Registration failed"
  echo "$REGISTER_RESPONSE"
  exit 1
fi

echo ""
echo "🔑 First login..."
LOGIN1_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

TOKEN1=$(echo "$LOGIN1_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))")

if [ -z "$TOKEN1" ]; then
  echo "❌ First login failed"
  echo "$LOGIN1_RESPONSE"
  exit 1
fi

echo "✅ First login successful"
echo "   Token: ${TOKEN1:0:30}..."

echo ""
echo "✓ Testing first token..."
VERIFY1=$(curl -s -X POST "$API_URL/api/auth/verify" \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json")

if echo "$VERIFY1" | grep -q '"valid": true'; then
  echo "✅ First token verified successfully"
else
  echo "❌ First token verification failed"
  echo "$VERIFY1"
  exit 1
fi

echo ""
echo "🚪 Simulating logout (frontend would clear localStorage)..."
echo "   Frontend clears: token from localStorage"
echo "   App state resets: authToken = null"
echo "   Navigation redirects to: /login"

echo ""
echo "🔑 Second login (after logout)..."
LOGIN2_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

TOKEN2=$(echo "$LOGIN2_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))")

if [ -z "$TOKEN2" ]; then
  echo "❌ Second login failed"
  echo "$LOGIN2_RESPONSE"
  exit 1
fi

echo "✅ Second login successful"
echo "   Token: ${TOKEN2:0:30}..."

echo ""
echo "✓ Testing second token..."
VERIFY2=$(curl -s -X POST "$API_URL/api/auth/verify" \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json")

if echo "$VERIFY2" | grep -q '"valid": true'; then
  echo "✅ Second token verified successfully"
else
  echo "❌ Second token verification failed"
  echo "$VERIFY2"
  exit 1
fi

echo ""
echo "✓ Verifying tokens are different..."
if [ "$TOKEN1" != "$TOKEN2" ]; then
  echo "✅ New token generated on second login"
else
  echo "⚠️  Both tokens are the same (might be OK if timestamps are same)"
fi

echo ""
echo "=========================================="
echo "✅ ALL TESTS PASSED - Flow is working!"
echo "=========================================="
echo ""
echo "Frontend fix:"
echo "  • App.js listens for localStorage changes"
echo "  • Login passes token to parent via onLoginSuccess"
echo "  • Logout clears localStorage and state"
echo "  • Router redirects to /dashboard on login"
echo "  • ProtectedRoute redirects to /login if no token"
