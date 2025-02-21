# Lightweight Messaging Bot Boilerplate

A modular and scalable messaging bot platform that supports multiple messaging services, with initial support for WhatsApp.

## Version
Current Version: 1.0.0
- Initial release with WhatsApp integration
- WebSocket server implementation
- Basic message routing

## Architecture

The project follows a microservices architecture with the following components:

### Backend (Python)
- Message processing and business logic
- Data storage and retrieval
- API endpoints for service integration

### Middleware (Node.js)
- WhatsApp integration using Baileys
- Message routing and transformation
- WebSocket server for real-time communication

### Database
- PostgreSQL with SQLAlchemy
- Efficient data persistence
- Scalable schema design

## Project Structure

```
├── backend/           # Python backend service
│   ├── src/
│   ├── tests/
│   └── requirements.txt
├── middleware/        # Node.js middleware service
│   ├── src/
│   ├── tests/
│   └── package.json
├── docker/           # Docker configuration
└── docker-compose.yml # Service orchestration
```

# WhatsApp Bot Middleware

A modular and scalable messaging platform middleware with support for WhatsApp and WebSocket communications.

## Features

- 🚀 Modular architecture
- 💬 Real-time messaging with WebSocket
- 📱 WhatsApp integration
- ⚡ High performance and reliability
- 🔄 Automatic reconnection handling
- 📦 Message queuing
- 📊 Connection monitoring

## Getting Started

### Prerequisites

- Node.js 16+
- Python 3.8+
- PostgreSQL (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whatsapp-bot.git
cd whatsapp-bot
```
2. Install dependencies for each service
3. Configure environment variables
4. Start services using Docker Compose

## Development

Each service can be developed and tested independently:

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m src.main
```

### Middleware
```bash
cd middleware
npm install
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT