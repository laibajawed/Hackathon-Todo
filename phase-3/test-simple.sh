#!/bin/bash
# Simplified E2E Test - Phase 3 Todo AI Chatbot

API_URL="http://localhost:8001"
EMAIL="test-$(date +%s)@example.com"
PASSWORD="TestPass123"

echo "=== Phase 3 E2E Test ==="
echo ""

# 1. Register user
echo "1. Registering user..."
RESP=$(curl -s -X POST "$API_URL/api/auth/signup" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
USER_ID=$(echo "$RESP" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
TOKEN=$(echo "$RESP" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "✓ User registered: $USER_ID"

# 2. Add task via chat
echo "2. Adding task via chat..."
RESP=$(curl -s -X POST "$API_URL/api/chat/$USER_ID/chat" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"message":"Add buy groceries to my list"}')
echo "$RESP" | grep -q "groceries" && echo "✓ Task created" || echo "✗ Task creation failed"

# 3. List tasks
echo "3. Listing tasks..."
RESP=$(curl -s -X POST "$API_URL/api/chat/$USER_ID/chat" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"message":"Show me my tasks"}')
echo "$RESP" | grep -q "groceries" && echo "✓ Task listed" || echo "✗ List failed"

# 4. Mark complete
echo "4. Marking task complete..."
RESP=$(curl -s -X POST "$API_URL/api/chat/$USER_ID/chat" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"message":"Mark buy groceries as complete"}')
echo "$RESP" | grep -q "complete" && echo "✓ Task completed" || echo "✗ Complete failed"

# 5. Get history
echo "5. Getting conversation history..."
RESP=$(curl -s -X GET "$API_URL/api/chat/$USER_ID/chat/history" -H "Authorization: Bearer $TOKEN")
echo "$RESP" | grep -q "messages" && echo "✓ History retrieved" || echo "✗ History failed"

echo ""
echo "=== Test Complete ==="
