import { WebSocketServer as WSServer, WebSocket } from 'ws';
import { EventEmitter } from 'events';
import { Logger } from '../logger/Logger.js';
import { MessagingPlatform, Message, ConnectionStatus, MessageEventType } from '../messaging/MessagingPlatform.js';

export interface QueuedMessage {
  data: any;
  attempts: number;
  timestamp: number;
}

export interface WebSocketClient extends WebSocket {
  id?: string;
  messageQueue: QueuedMessage[];
  reconnectAttempts: number;
  isAlive: boolean;
  closeCode?: number;
}

export class WebSocketService extends EventEmitter implements MessagingPlatform {
  private wss: WSServer;
  private clients: Map<string, WebSocketClient>;
  private status: ConnectionStatus;
  private readonly MAX_RECONNECT_ATTEMPTS = 5;
  private readonly RECONNECT_INTERVAL = 5000;
  private readonly MAX_QUEUE_SIZE = 100;
  private readonly PING_INTERVAL = 30000;

  constructor(port: number) {
    super();
    this.clients = new Map();
    this.status = ConnectionStatus.DISCONNECTED;
    
    this.wss = new WSServer({ 
      port,
      clientTracking: true,
      perMessageDeflate: false
    });

    this.wss.on('connection', this.handleConnection.bind(this));
    this.status = ConnectionStatus.CONNECTED;
    Logger.info(`WebSocket server started on port ${port}`);

    // Setup periodic ping for all clients
    setInterval(() => {
      this.clients.forEach(this.pingClient.bind(this));
    }, this.PING_INTERVAL);
  }

  private pingClient(client: WebSocketClient): void {
    if (!client.isAlive) {
      Logger.info(`Client ${client.id} not responding, terminating connection`);
      return client.terminate();
    }
    
    client.isAlive = false;
    client.ping();
  }

  private handleConnection(ws: WebSocketClient): void {
    const clientId = Math.random().toString(36).substring(7);
    ws.id = clientId;
    ws.messageQueue = [];
    ws.reconnectAttempts = 0;
    ws.isAlive = true;
    this.clients.set(clientId, ws);

    Logger.info(`New WebSocket client connected: ${clientId}`);

    ws.on('pong', () => {
      ws.isAlive = true;
    });

    ws.on('message', (data: string | Buffer | ArrayBuffer | Buffer[]) => {
      this.handleMessage(ws, data);
    });

    ws.on('close', (code: number) => {
      ws.closeCode = code;
      this.handleDisconnection(ws);
    });

    ws.on('error', (error: Error) => {
      this.handleError(ws, error);
    });

    this.emit(MessageEventType.CONNECTION_UPDATE, { 
      status: this.status, 
      clientId,
      type: 'connection'
    });
  }

  private handleMessage(ws: WebSocketClient, data: string | Buffer | ArrayBuffer | Buffer[]): void {
    try {
      const parsed = JSON.parse(data.toString());
      Logger.info(`Message received from client ${ws.id}`);

      const message: Message = {
        id: Math.random().toString(36).substring(7),
        from: ws.id || 'unknown',
        to: parsed.to || 'broadcast',
        content: parsed.content || '',
        timestamp: Date.now(),
        type: parsed.type || 'text',
        metadata: parsed,
      };

      this.emit(MessageEventType.RECEIVED, message);
    } catch (error) {
      Logger.error(`Error parsing WebSocket message: ${error}`);
    }
  }

  private handleDisconnection(ws: WebSocketClient): void {
    if (!ws.id) return;
    Logger.info(`Client disconnected: ${ws.id}`);

    // Only attempt reconnection for unexpected closures
    if (ws.closeCode !== 1000 && ws.closeCode !== 1001) {
      if (ws.reconnectAttempts < this.MAX_RECONNECT_ATTEMPTS) {
        ws.reconnectAttempts++;
        Logger.info(`Reconnection attempt ${ws.reconnectAttempts} for client ${ws.id}`);
        setTimeout(() => this.attemptReconnection(ws), this.RECONNECT_INTERVAL);
      } else {
        Logger.warn(`Max reconnection attempts reached for client ${ws.id}`);
        this.clients.delete(ws.id);
        this.emit(MessageEventType.CONNECTION_UPDATE, { 
          status: ConnectionStatus.DISCONNECTED, 
          clientId: ws.id,
          type: 'disconnection'
        });
      }
    } else {
      this.clients.delete(ws.id);
      Logger.info(`Client ${ws.id} closed connection normally`);
    }
  }

  private handleError(ws: WebSocketClient, error: Error): void {
    Logger.error(`WebSocket error for client ${ws.id}:`, error);
  }

  private attemptReconnection(ws: WebSocketClient): void {
    if (!ws.id) return;
    try {
      if (ws.readyState === WebSocket.CLOSED) {
        Logger.info(`Attempting reconnection for client ${ws.id}`);
        this.emit(MessageEventType.CONNECTION_UPDATE, {
          status: ConnectionStatus.CONNECTING,
          clientId: ws.id,
          type: 'reconnecting'
        });
      }
    } catch (error) {
      Logger.error(`Reconnection attempt failed for client ${ws.id}:`, error);
    }
  }

  private async sendWithRetry(client: WebSocketClient, message: string, maxRetries: number = 3): Promise<void> {
    let attempts = 0;
    const trySend = async (): Promise<void> => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message, (err) => {
          if (err) {
            Logger.error(`Failed to send message to client ${client.id}:`, err);
          }
        });
      } else if (attempts < maxRetries) {
        attempts++;
        await new Promise(resolve => setTimeout(resolve, 1000));
        await trySend();
      } else {
        throw new Error(`Failed to send message after ${maxRetries} attempts`);
      }
    };
    await trySend();
  }

  private queueMessage(client: WebSocketClient, data: any): void {
    if (client.messageQueue.length >= this.MAX_QUEUE_SIZE) {
      client.messageQueue.shift();
    }
    client.messageQueue.push({
      data,
      attempts: 0,
      timestamp: Date.now()
    });
  }

  private broadcast(data: any): void {
    const messageStr = JSON.stringify(data);
    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        this.sendWithRetry(client, messageStr).catch(err => {
          Logger.error(`Broadcast failed for client ${client.id}:`, err);
          this.queueMessage(client, data);
        });
      } else {
        this.queueMessage(client, data);
      }
    });
  }

  async connect(): Promise<void> {
    this.status = ConnectionStatus.CONNECTED;
    this.emit(MessageEventType.CONNECTION_UPDATE, { status: this.status });
  }

  async disconnect(): Promise<void> {
    this.status = ConnectionStatus.DISCONNECTED;
    this.clients.forEach(client => client.close(1000, 'Server shutdown'));
    this.clients.clear();
    this.emit(MessageEventType.CONNECTION_UPDATE, { status: this.status });
  }

  async sendMessage(to: string, content: string, options: any = {}): Promise<any> {
    const message: Message = {
      id: Math.random().toString(36).substring(7),
      from: 'server',
      to,
      content,
      timestamp: Date.now(),
      type: 'text',
      metadata: options
    };

    this.broadcast({ type: 'message', data: message });
    return message;
  }

  onMessage(callback: (message: Message) => void): void {
    this.on(MessageEventType.RECEIVED, callback);
  }

  onConnectionUpdate(callback: (update: any) => void): void {
    this.on(MessageEventType.CONNECTION_UPDATE, callback);
  }

  getStatus(): string {
    return this.status;
  }

  public close(): void {
    this.wss.close(() => {
      Logger.info('WebSocket server closed');
    });
  }
}
