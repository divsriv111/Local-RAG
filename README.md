# RAG Chatbot - ASP.NET Core 9 Clean Architecture Backend

This is an enterprise-grade backend API for a RAG (Retrieval-Augmented Generation) PDF chatbot application built with ASP.NET Core 9 following Clean Architecture principles.

## 🏗️ Architecture

The solution follows **Clean Architecture** with clear separation of concerns:

### Domain Layer

- **Location**: `Domain/` project
- **Purpose**: Contains core business entities and interfaces
- **Entities**:
  - `User`: Authentication and user management
  - `Workspace`: Organizational unit for PDFs and chats
  - `ChatHistory`: Conversation threads within workspaces
  - `PDFDocument`: Uploaded PDF file metadata
  - `Message`: Individual chat messages with AI responses
- **Interfaces**:
  - `IRepository<T>`: Generic repository pattern
  - `IUnitOfWork`: Transaction management

### Application Layer

- **Location**: `Application/` project
- **Purpose**: Business logic, DTOs, and CQRS implementation
- **Features**:
  - CQRS Commands and Queries using **MediatR**
  - Data Transfer Objects (DTOs)
  - FluentValidation for input validation
- **Example Commands/Queries**:
  - `CreateWorkspaceCommand`
  - `GetAllWorkspacesQuery`
  - `GetWorkspaceByIdQuery`

### Infrastructure Layer

- **Location**: `Infrastructure/` project
- **Purpose**: Data access and external services
- **Key Components**:
  - `ApplicationDbContext`: EF Core DbContext
  - `Repository<T>`: Generic repository implementation
  - `UnitOfWork`: Transaction coordination
- **Database**: PostgreSQL with Npgsql provider
- **ORM**: Entity Framework Core 9

### API Layer

- **Location**: `API/` project
- **Purpose**: HTTP endpoints, middleware, DI configuration
- **Features**:
  - RESTful controllers
  - Swagger/OpenAPI documentation
  - CORS configuration
  - Dependency injection setup

## 📋 Prerequisites

- [.NET 9 SDK](https://dotnet.microsoft.com/download/dotnet/9.0)
- [PostgreSQL 17+](https://www.postgresql.org/download/)
- [Docker](https://www.docker.com/get-started) (optional, for containerized PostgreSQL)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Local RAG"
```

### 2. Configure Database Connection

Update the connection string in `API/appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=rag_chatbot;Username=raguser;Password=changeme"
  }
}
```

### 3. Set Up PostgreSQL Database

**Option A: Using Docker**

```bash
docker run --name rag-postgres \\
  -e POSTGRES_DB=rag_chatbot \\
  -e POSTGRES_USER=raguser \\
  -e POSTGRES_PASSWORD=changeme \\
  -p 5432:5432 \\
  -d postgres:17-alpine
```

**Option B: Local PostgreSQL**

```sql
CREATE DATABASE rag_chatbot;
CREATE USER raguser WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE rag_chatbot TO raguser;
```

### 4. Apply Database Migrations

```bash
# Install EF Core tools (if not already installed)
dotnet tool install --global dotnet-ef

# Apply migrations
dotnet ef database update --project Infrastructure --startup-project API
```

### 5. Build and Run

```bash
# Restore dependencies
dotnet restore

# Build solution
dotnet build

# Run the API
dotnet run --project API
```

The API will be available at:

- **HTTP**: http://localhost:5000
- **Swagger UI**: http://localhost:5000/swagger

## 📚 Database Schema

### Entities and Relationships

```
User (1) ────────> (*) Workspace
                         │
                         ├──────> (*) ChatHistory ────────> (*) Message
                         │
                         └──────> (*) PDFDocument
```

### Entity Details

**User**

- Id (Guid, PK)
- Username (string, unique, indexed)
- Email (string, unique, indexed)
- PasswordHash (string)
- CreatedAt, UpdatedAt (DateTime)

**Workspace**

- Id (Guid, PK)
- Name (string, max 100 chars)
- UserId (Guid, FK → User, indexed)
- CreatedAt, UpdatedAt (DateTime)

**ChatHistory**

- Id (Guid, PK)
- WorkspaceId (Guid, FK → Workspace, indexed)
- Name (string, max 200 chars)
- FirstQuery (string, max 500 chars)
- CreatedAt (DateTime, indexed)
- IsArchived (bool, default: false)

**PDFDocument**

- Id (Guid, PK)
- WorkspaceId (Guid, FK → Workspace, indexed)
- FileName (string, max 255 chars)
- FilePath (string, max 500 chars)
- FileSize (long)
- UploadedAt (DateTime)
- IsSelected (bool, default: false)

**Message**

- Id (Guid, PK)
- ChatHistoryId (Guid, FK → ChatHistory, indexed)
- Content (string)
- IsUserMessage (bool)
- Timestamp (DateTime, indexed)
- References (JSONB) - stores source PDF references

## 🛠️ Technology Stack

- **Framework**: ASP.NET Core 9.0
- **Language**: C# 13
- **ORM**: Entity Framework Core 9.0
- **Database**: PostgreSQL 17+ (Npgsql driver)
- **CQRS**: MediatR 13.x
- **Validation**: FluentValidation
- **API Documentation**: Swashbuckle (Swagger/OpenAPI)
- **Design Pattern**: Clean Architecture, Repository Pattern, CQRS

## 📦 NuGet Packages

### Domain Layer

- None (pure C# POCOs)

### Application Layer

- `MediatR` - CQRS implementation
- `FluentValidation` - Input validation

### Infrastructure Layer

- `Microsoft.EntityFrameworkCore` - ORM
- `Microsoft.EntityFrameworkCore.Design` - Design-time tools
- `Npgsql.EntityFrameworkCore.PostgreSQL` - PostgreSQL provider

### API Layer

- `Swashbuckle.AspNetCore` - Swagger/OpenAPI
- `Microsoft.EntityFrameworkCore.Design` - EF migrations

## 📖 API Endpoints

### Workspaces

| Method | Endpoint               | Description                 |
| ------ | ---------------------- | --------------------------- |
| GET    | `/api/workspaces`      | Get all workspaces for user |
| GET    | `/api/workspaces/{id}` | Get workspace details       |
| POST   | `/api/workspaces`      | Create new workspace        |
| PUT    | `/api/workspaces/{id}` | Update workspace name       |
| DELETE | `/api/workspaces/{id}` | Delete workspace            |

**Query Parameters** (GET /api/workspaces):

- `search` (optional): Filter by workspace name

## 🔧 Development

### Adding a New Migration

```bash
dotnet ef migrations add MigrationName --project Infrastructure --startup-project API
```

### Reverting a Migration

```bash
dotnet ef migrations remove --project Infrastructure --startup-project API
```

### Updating Database

```bash
dotnet ef database update --project Infrastructure --startup-project API
```

### Building the Solution

```bash
# Clean build
dotnet clean
dotnet build

# Build with specific configuration
dotnet build --configuration Release
```

## 🧪 Testing

```bash
# Run all tests (when test projects are added)
dotnet test
```

## 🚢 Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t rag-chatbot-api -f API/Dockerfile .

# Run container
docker run -d \\
  -p 5000:5000 \\
  -e ConnectionStrings__DefaultConnection="Host=postgres;Port=5432;Database=rag_chatbot;Username=raguser;Password=changeme" \\
  --name rag-api \\
  rag-chatbot-api
```

### Production Considerations

1. **Environment Variables**: Use environment-specific configuration
2. **Connection Pooling**: Configure PostgreSQL connection pooling
3. **Logging**: Integrate Serilog with Elasticsearch (per requirements)
4. **HTTPS**: Configure SSL certificates for production
5. **CORS**: Restrict allowed origins in production
6. **Rate Limiting**: Add rate limiting middleware
7. **Authentication**: Implement JWT authentication (next phase)

## 📝 Project Structure

```
Local RAG/
├── Domain/
│   ├── Entities/
│   │   ├── User.cs
│   │   ├── Workspace.cs
│   │   ├── ChatHistory.cs
│   │   ├── PDFDocument.cs
│   │   └── Message.cs
│   └── Common/
│       ├── IRepository.cs
│       └── IUnitOfWork.cs
├── Application/
│   ├── DTOs/
│   │   ├── UserDtos.cs
│   │   ├── WorkspaceDtos.cs
│   │   ├── ChatHistoryDtos.cs
│   │   ├── PDFDocumentDtos.cs
│   │   └── MessageDtos.cs
│   ├── Features/
│   │   └── Workspaces/
│   │       ├── Commands/
│   │       │   ├── CreateWorkspaceCommand.cs
│   │       │   └── CreateWorkspaceCommandHandler.cs
│   │       ├── Queries/
│   │       │   ├── GetAllWorkspacesQuery.cs
│   │       │   ├── GetAllWorkspacesQueryHandler.cs
│   │       │   ├── GetWorkspaceByIdQuery.cs
│   │       │   └── GetWorkspaceByIdQueryHandler.cs
│   │       └── Validators/
│   │           └── CreateWorkspaceCommandValidator.cs
│   └── DependencyInjection.cs
├── Infrastructure/
│   ├── Data/
│   │   ├── ApplicationDbContext.cs
│   │   └── Migrations/
│   ├── Repositories/
│   │   ├── Repository.cs
│   │   └── UnitOfWork.cs
│   └── DependencyInjection.cs
├── API/
│   ├── Controllers/
│   │   └── WorkspacesController.cs
│   ├── Program.cs
│   ├── appsettings.json
│   └── appsettings.Development.json
└── RagChatbot.sln
```

## 🔒 Security

- **Password Hashing**: Use BCrypt for password storage (to be implemented)
- **JWT Tokens**: Implement secure token-based authentication (next phase)
- **Input Validation**: FluentValidation on all DTOs
- **SQL Injection**: Protected via EF Core parameterized queries
- **CORS**: Configure allowed origins appropriately

## 🎯 Next Steps

1. **Authentication**: Implement JWT Bearer authentication
2. **User Management**: Add registration, login, and profile endpoints
3. **Chat Features**: Implement chat history and message endpoints
4. **PDF Upload**: Add file upload with validation
5. **LLM Integration**: Connect to Python LLM service
6. **Logging**: Integrate Serilog with Elasticsearch
7. **Unit Tests**: Add comprehensive test coverage
8. **Integration Tests**: Test complete workflows

## 📄 License

MIT License

## 👥 Contributors

- Your Name / Team

---

**Built with ❤️ using ASP.NET Core 9 and Clean Architecture**
