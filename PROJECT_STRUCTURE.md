# Detailed Project Structure

```
├── backend/                    # Python FastAPI backend service
│   ├── src/                   # Source code
│   │   ├── api/              # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── messages.py   # Message handling endpoints
│   │   │   └── webhooks.py   # Webhook endpoints
│   │   ├── core/             # Core application code
│   │   │   ├── __init__.py
│   │   │   ├── config.py     # Configuration management
│   │   │   ├── security.py   # Security utilities
│   │   │   └── logging.py    # Logging configuration
│   │   ├── models/           # Database models
│   │   │   ├── __init__.py
│   │   │   ├── message.py    # Message model
│   │   │   └── user.py       # User model
│   │   ├── services/         # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── message.py    # Message processing
│   │   │   └── user.py       # User management
│   │   └── main.py           # Application entry point
│   ├── tests/                # Unit and integration tests
│   │   ├── __init__.py
│   │   ├── test_api/        # API tests
│   │   ├── test_services/   # Service tests
│   │   └── conftest.py      # Test configuration
│   ├── requirements.txt      # Python dependencies
│   └── README.md            # Backend documentation
│
├── middleware/               # Node.js WhatsApp integration service
│   ├── src/                 # Source code
│   │   ├── config/         # Configuration files
│   │   │   ├── index.ts    # Config exports
│   │   │   └── whatsapp.ts # WhatsApp specific config
│   │   ├── services/       # Service implementations
│   │   │   ├── whatsapp.ts # WhatsApp service
│   │   │   └── websocket.ts # WebSocket server
│   │   ├── types/          # TypeScript type definitions
│   │   ├── utils/          # Utility functions
│   │   └── index.ts        # Entry point
│   ├── tests/              # Test files
│   ├── package.json        # Node.js dependencies
│   └── README.md          # Middleware documentation
│
├── frontend/               # React admin interface
│   ├── src/               # Source code
│   │   ├── components/    # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   ├── store/        # State management
│   │   ├── styles/       # CSS/SCSS files
│   │   └── App.tsx       # Root component
│   ├── public/           # Static files
│   ├── package.json      # Node.js dependencies
│   └── README.md        # Frontend documentation
│
├── database/             # Database management
│   ├── migrations/      # Database migrations
│   ├── schema.ts        # Drizzle schema definitions
│   └── config.ts        # Database configuration
│
├── config/              # Global configuration
│   ├── development.env  # Development environment
│   ├── production.env   # Production environment
│   └── test.env        # Test environment
│
├── logs/               # Application logs
│   ├── error.log      # Error logs
│   └── access.log     # Access logs
│
├── docker/            # Docker configuration
│   ├── backend/       # Backend Dockerfile
│   ├── middleware/    # Middleware Dockerfile
│   └── frontend/      # Frontend Dockerfile
│
├── .gitignore        # Git ignore rules
├── docker-compose.yml # Service orchestration
└── README.md         # Project documentation
```

## Directory Descriptions

### Backend (/backend)
Contains the Python FastAPI backend service responsible for core business logic, API endpoints, and data management.

- **/src/api**: REST API endpoints and route handlers
- **/src/core**: Core application functionality and configurations
- **/src/models**: Database models and schemas
- **/src/services**: Business logic implementation

### Middleware (/middleware)
Houses the Node.js service that integrates with WhatsApp using Baileys and handles message routing.

- **/src/config**: Configuration management
- **/src/services**: WhatsApp and WebSocket implementations
- **/src/types**: TypeScript type definitions

### Frontend (/frontend)
Contains the React-based admin interface for bot management and monitoring.

- **/src/components**: Reusable UI components
- **/src/pages**: Page-level components
- **/src/services**: API integration services
- **/src/store**: State management (Redux/Context)

### Database (/database)
Manages database schema, migrations, and configuration using Drizzle ORM.

- **/migrations**: Database migration files
- **schema.ts**: Drizzle ORM schema definitions

### Config (/config)
Stores environment-specific configuration files.

### Logs (/logs)
Centralized logging directory for application logs.

### Docker (/docker)
Contains Dockerfile configurations for each service.

## Key Files

- **docker-compose.yml**: Defines and orchestrates all services
- **.gitignore**: Specifies which files Git should ignore
- **README.md**: Project documentation and setup instructions