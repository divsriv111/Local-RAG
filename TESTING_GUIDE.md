# Testing Guide - RAG Chatbot API

## 🧪 Testing the Workspaces API

### Prerequisites

1. **Start PostgreSQL Database**:
```bash
docker run --name rag-postgres \
  -e POSTGRES_DB=rag_chatbot \
  -e POSTGRES_USER=raguser \
  -e POSTGRES_PASSWORD=changeme \
  -p 5432:5432 \
  -d postgres:17-alpine
```

2. **Apply Database Migrations**:
```bash
export PATH="$PATH:/Users/divyanshusrivastava/.dotnet/tools"
cd "/Users/divyanshusrivastava/Local RAG"
dotnet ef database update --project Infrastructure --startup-project API
```

3. **Run the API**:
```bash
cd "/Users/divyanshusrivastava/Local RAG"
dotnet run --project API
```

4. **Access Swagger UI**:
   - Open: http://localhost:5000/swagger

---

## 📋 API Test Scenarios

### 1. Create a Workspace

**Request**:
```http
POST http://localhost:5000/api/workspaces
Content-Type: application/json

{
  "name": "My First Workspace"
}
```

**cURL**:
```bash
curl -X POST "http://localhost:5000/api/workspaces" \
  -H "Content-Type: application/json" \
  -d '{"name": "My First Workspace"}'
```

**Expected Response** (201 Created):
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "My First Workspace",
  "userId": "...",
  "createdAt": "2025-11-11T01:00:00Z",
  "updatedAt": "2025-11-11T01:00:00Z"
}
```

---

### 2. Get All Workspaces

**Request**:
```http
GET http://localhost:5000/api/workspaces
```

**cURL**:
```bash
curl -X GET "http://localhost:5000/api/workspaces"
```

**Expected Response** (200 OK):
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "My First Workspace",
    "userId": "...",
    "createdAt": "2025-11-11T01:00:00Z",
    "updatedAt": "2025-11-11T01:00:00Z"
  }
]
```

---

### 3. Get All Workspaces with Search

**Request**:
```http
GET http://localhost:5000/api/workspaces?search=First
```

**cURL**:
```bash
curl -X GET "http://localhost:5000/api/workspaces?search=First"
```

**Expected Response** (200 OK):
- Returns only workspaces matching "First" in name (case-insensitive)

---

### 4. Get Workspace by ID

**Request**:
```http
GET http://localhost:5000/api/workspaces/{id}
```

**cURL** (replace `{id}` with actual ID from create response):
```bash
curl -X GET "http://localhost:5000/api/workspaces/3fa85f64-5717-4562-b3fc-2c963f66afa6"
```

**Expected Response** (200 OK):
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "My First Workspace",
  "userId": "...",
  "createdAt": "2025-11-11T01:00:00Z",
  "updatedAt": "2025-11-11T01:00:00Z",
  "chatHistories": [],
  "pdfDocuments": []
}
```

---

### 5. Update Workspace (Stub - Not Fully Implemented)

**Request**:
```http
PUT http://localhost:5000/api/workspaces/{id}
Content-Type: application/json

{
  "name": "Updated Workspace Name"
}
```

**Expected Response** (204 No Content):
- Currently returns NoContent without updating

---

### 6. Delete Workspace (Stub - Not Fully Implemented)

**Request**:
```http
DELETE http://localhost:5000/api/workspaces/{id}
```

**Expected Response** (204 No Content):
- Currently returns NoContent without deleting

---

## 🔍 Testing with Swagger UI

1. Navigate to http://localhost:5000/swagger
2. Expand `/api/workspaces` endpoints
3. Click "Try it out" on any endpoint
4. Fill in parameters/body
5. Click "Execute"
6. View response

---

## 🧰 Testing with Postman

### Import Collection

Create a new Postman collection with these requests:

**1. Create Workspace**
- Method: POST
- URL: `http://localhost:5000/api/workspaces`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "name": "{{$randomProductName}}"
}
```

**2. Get All Workspaces**
- Method: GET
- URL: `http://localhost:5000/api/workspaces`

**3. Get Workspace by ID**
- Method: GET
- URL: `http://localhost:5000/api/workspaces/{{workspaceId}}`
- (Save ID from create response to environment variable)

**4. Search Workspaces**
- Method: GET
- URL: `http://localhost:5000/api/workspaces?search=test`

---

## 🐛 Troubleshooting

### Database Connection Issues

**Error**: "Could not connect to database"

**Solution**:
1. Verify PostgreSQL is running:
```bash
docker ps | grep rag-postgres
```

2. Check connection string in `API/appsettings.json`
3. Test connection:
```bash
docker exec -it rag-postgres psql -U raguser -d rag_chatbot
```

### Migration Issues

**Error**: "No such table"

**Solution**:
```bash
dotnet ef database update --project Infrastructure --startup-project API
```

### Port Already in Use

**Error**: "Address already in use"

**Solution**:
1. Kill process on port 5000:
```bash
lsof -ti:5000 | xargs kill -9
```

2. Or change port in `API/Properties/launchSettings.json`

---

## ✅ Validation Testing

### Test Invalid Input

**Request**:
```http
POST http://localhost:5000/api/workspaces
Content-Type: application/json

{
  "name": ""
}
```

**Expected Response** (400 Bad Request):
- Validation error for empty workspace name

**Request**:
```http
POST http://localhost:5000/api/workspaces
Content-Type: application/json

{
  "name": "This workspace name is intentionally very very very very very very very very very very very very very long to exceed the maximum allowed length of 100 characters"
}
```

**Expected Response** (400 Bad Request):
- Validation error for name exceeding 100 characters

---

## 📊 Database Verification

### Check Data Directly in PostgreSQL

**Connect to database**:
```bash
docker exec -it rag-postgres psql -U raguser -d rag_chatbot
```

**View workspaces**:
```sql
SELECT * FROM "Workspaces";
```

**View all tables**:
```sql
\dt
```

**Check table structure**:
```sql
\d "Workspaces"
```

**Exit**:
```sql
\q
```

---

## 🚀 Load Testing (Optional)

### Using Apache Bench

**Create workspace** (100 requests, 10 concurrent):
```bash
ab -n 100 -c 10 -p workspace.json -T application/json \
  http://localhost:5000/api/workspaces
```

Where `workspace.json` contains:
```json
{"name":"Load Test Workspace"}
```

### Using k6

**Install k6**:
```bash
brew install k6
```

**Create test script** (`load-test.js`):
```javascript
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  const payload = JSON.stringify({
    name: 'Test Workspace ' + Date.now(),
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let res = http.post('http://localhost:5000/api/workspaces', payload, params);
  
  check(res, {
    'status is 201': (r) => r.status === 201,
  });
}
```

**Run test**:
```bash
k6 run load-test.js
```

---

## 📝 Test Checklist

- [ ] PostgreSQL database is running
- [ ] Migrations are applied
- [ ] API starts successfully
- [ ] Swagger UI is accessible
- [ ] Can create a workspace
- [ ] Can retrieve all workspaces
- [ ] Can retrieve workspace by ID
- [ ] Can search workspaces
- [ ] Validation works (empty name rejected)
- [ ] Validation works (long name rejected)
- [ ] Data persists in database
- [ ] 404 returned for non-existent workspace

---

## 🎯 Next Testing Phase

Once authentication is implemented:
- [ ] Test user registration
- [ ] Test user login
- [ ] Test JWT token validation
- [ ] Test workspace ownership (can't access other user's workspaces)
- [ ] Test token expiration
- [ ] Test refresh token flow

---

**Happy Testing! 🎉**
