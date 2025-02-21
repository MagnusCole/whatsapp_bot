import { WhatsAppPlatform } from './services/messaging/WhatsAppPlatform.js';
import { WebSocketService } from './services/websocket/WebSocketServer.js';
import { Logger } from './services/logger/Logger.js';
import { config } from 'dotenv';
import { join } from 'path';
import { Message, MessageEventType, ConnectionStatus } from './services/messaging/MessagingPlatform.js';

// Cargar variables de entorno
config();

// Configuración
const WS_PORT = parseInt(process.env.WS_PORT || '8080', 10);
const AUTH_PATH = join(process.cwd(), 'auth');

// Función para esperar la autenticación con timeout
async function waitForAuthentication(whatsapp: WhatsAppPlatform): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    const timeout = setTimeout(() => {
      whatsapp.removeListener(MessageEventType.CONNECTION_UPDATE, onUpdate);
      reject(new Error('Timeout waiting for WhatsApp authentication'));
    }, 30000); // 30 seconds timeout

    const onUpdate = (update: any) => {
      if (update.status === ConnectionStatus.AUTHENTICATED) {
        clearTimeout(timeout);
        whatsapp.removeListener(MessageEventType.CONNECTION_UPDATE, onUpdate);
        resolve();
      }
    };

    whatsapp.on(MessageEventType.CONNECTION_UPDATE, onUpdate);
  });
}

async function main() {
  try {
    Logger.initialize();
    Logger.info('Starting WhatsApp Bot Middleware...');

    // Initialize WhatsApp platform
    const whatsapp = new WhatsAppPlatform(AUTH_PATH);

    // Listen for connection updates
    whatsapp.onConnectionUpdate((update: any) => {
      Logger.info('WhatsApp connection update:', {
        status: whatsapp.getStatus(),
        update
      });
    });

    await whatsapp.connect();

    // Wait for authentication if not authenticated
    if (whatsapp.getStatus() !== ConnectionStatus.AUTHENTICATED) {
      Logger.info('Waiting for WhatsApp authentication...');
      await waitForAuthentication(whatsapp);
    }
    Logger.info('WhatsApp platform connected and authenticated successfully');

    // Initialize WebSocket server
    const wsServer = new WebSocketService(WS_PORT);
    Logger.info(`WebSocket server started on port ${WS_PORT}`);

    // Handle WebSocket messages and forward to WhatsApp
    wsServer.on(MessageEventType.RECEIVED, async (message: Message) => {
      try {
        const currentStatus = whatsapp.getStatus();
        Logger.info('Processing received message:', {
          messageId: message.id,
          to: message.to,
          content: message.content,
          currentStatus
        });

        if (currentStatus !== ConnectionStatus.AUTHENTICATED) {
          throw new Error(`Cannot send message. WhatsApp status: ${currentStatus}`);
        }

        Logger.info('Sending message to WhatsApp...');
        const response = await whatsapp.sendMessage(
          message.to,
          message.content,
          message.metadata
        );
        Logger.info('Message sent successfully to WhatsApp:', response);
      } catch (error) {
        Logger.error('Failed to forward message to WhatsApp:', {
          error,
          message,
          currentStatus: whatsapp.getStatus()
        });
      }
    });

    // Forward WhatsApp responses back to WebSocket clients
    whatsapp.on(MessageEventType.SENT, (message: Message) => {
      wsServer.sendMessage(message.to, message.content, message.metadata);
    });

    // Handle graceful shutdown
    const cleanup = async () => {
      Logger.info('Shutting down middleware...');
      await whatsapp.disconnect();
      wsServer.close();
      process.exit(0);
    };

    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);

    Logger.info(`WhatsApp Bot Middleware running on port ${WS_PORT}`);
  } catch (error) {
    Logger.error('Failed to start middleware:', error);
    process.exit(1);
  }
}

main();
