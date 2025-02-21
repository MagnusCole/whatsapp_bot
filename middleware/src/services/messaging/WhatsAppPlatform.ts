import { makeWASocket, DisconnectReason, useMultiFileAuthState } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import { EventEmitter } from 'events';
import { MessagingPlatform, Message, ConnectionStatus, MessageEventType } from './MessagingPlatform.js';
import { Logger } from '../logger/Logger.js';

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Wait until the connection stabilizes to AUTHENTICATED or timeout is reached
async function waitForReady(client: any, timeout: number = 10000): Promise<void> {
  // Log client properties for debugging
  console.log('📊 Client properties:', {
    availableProperties: Object.keys(client),
    eventsAvailable: Object.keys(client.ev?.on ? client.ev : {}),
    user: client.user,
    authState: client.authState,
    store: client.store
  });

  const waitForConnection = new Promise((resolve, reject) => {
    const checkConnection = async (update: any) => {
      // Log detailed connection state
      const connectionState = {
        hasUser: !!client.user,
        isConnected: !!client.user && update.connection === 'open',
        connection: update.connection,
        socketInfo: {
          isOnline: !!client.user,
          qrGenerated: !!update.qr,
          isNewLogin: !!update.isNewLogin
        }
      };

      console.log('🔄 Connection state update:', connectionState);
      console.log('📡 Raw update event:', update);

      if (connectionState.isConnected) {
        client.ev.off('connection.update', checkConnection);
        resolve(true);
      }

      // Detect permanent disconnection
      if (update.connection === 'close' && !update.isNewLogin) {
        client.ev.off('connection.update', checkConnection);
        reject(new Error(`Connection closed: ${update.lastDisconnect?.error?.message || 'Unknown error'}`));
      }
    };

    client.ev.on('connection.update', checkConnection);

    // Initial check with current state
    checkConnection({ 
      connection: client.user ? 'open' : 'connecting',
      isNewLogin: false
    });

    setTimeout(() => {
      client.ev.off('connection.update', checkConnection);
      reject(new Error('Connection verification timeout'));
    }, timeout);
  });

  try {
    await waitForConnection;
    console.log('✅ Connection verified successfully');
  } catch (error) {
    console.error('❌ Connection verification failed:', error);
    throw error;
  }
}

export class WhatsAppPlatform extends EventEmitter implements MessagingPlatform {
  private client: any;
  private status: ConnectionStatus = ConnectionStatus.DISCONNECTED;
  private authPath: string;
  private isReconnecting: boolean = false;
  private reconnectAttempts: number = 0;
  private readonly MAX_RECONNECT_ATTEMPTS = 3;
  private readonly RECONNECT_DELAY = 5000;

  constructor(authPath: string = './auth') {
    super();
    this.authPath = authPath;
  }

  async connect(): Promise<void> {
    try {
      Logger.info('Starting WhatsApp connection...');
      
      if (this.isReconnecting) {
        Logger.info('Reconnection already in progress, skipping...');
        return;
      }

      await this.disconnect();
      this.status = ConnectionStatus.CONNECTING;
      
      const { state, saveCreds } = await useMultiFileAuthState(this.authPath);
      
      this.client = makeWASocket({
        auth: state,
        printQRInTerminal: true,
        browser: ["WhatsApp Bot", "Chrome", "1.0.0"],
        connectTimeoutMs: 60000,
        retryRequestDelayMs: 2000,
        markOnlineOnConnect: false,
        syncFullHistory: false
      });

      this.client.ev.on('connection.update', async (update: any) => {
        const { connection, lastDisconnect } = update;
        Logger.info('Connection update:', { connection, status: this.status });

        if (connection === 'close') {
          const statusCode = (lastDisconnect?.error as Boom)?.output?.statusCode;
          const shouldReconnect = this.shouldAttemptReconnect(statusCode);
          
          if (shouldReconnect) {
            await this.handleReconnection();
          } else {
            this.status = ConnectionStatus.DISCONNECTED;
            this.isReconnecting = false;
            this.reconnectAttempts = 0;
          }
        }
        else if (connection === 'open') {
          Logger.info('WhatsApp connection authenticated');
          this.status = ConnectionStatus.AUTHENTICATED;
          this.isReconnecting = false;
          this.reconnectAttempts = 0;
        }

        this.emit(MessageEventType.CONNECTION_UPDATE, {
          status: this.status,
          update,
        });
      });

      this.client.ev.on('creds.update', saveCreds);
      this.setupMessageHandler();

    } catch (error) {
      this.status = ConnectionStatus.ERROR;
      Logger.error('Connection error:', error);
      throw error;
    }
  }

  private async handleReconnection(): Promise<void> {
    if (this.reconnectAttempts >= this.MAX_RECONNECT_ATTEMPTS) {
      Logger.warn('Max reconnection attempts reached, stopping reconnection');
      this.status = ConnectionStatus.ERROR;
      return;
    }

    this.isReconnecting = true;
    this.reconnectAttempts++;
    
    Logger.info(`Attempting reconnection ${this.reconnectAttempts}/${this.MAX_RECONNECT_ATTEMPTS}`);
    await delay(this.RECONNECT_DELAY);
    await this.connect();
  }

  private shouldAttemptReconnect(statusCode?: number): boolean {
    // Don't reconnect if logged out or if connection was closed intentionally
    if (statusCode === DisconnectReason.loggedOut) return false;
    if (this.status === ConnectionStatus.DISCONNECTED) return false;
    if (this.isReconnecting && this.reconnectAttempts >= this.MAX_RECONNECT_ATTEMPTS) return false;
    
    return true;
  }

  private setupMessageHandler(): void {
    this.client.ev.on('messages.upsert', (m: any) => {
      const msg = m.messages[0];
      if (!msg.key.fromMe) {
        const message: Message = {
          id: msg.key.id,
          from: msg.key.remoteJid,
          to: msg.key.remoteJid,
          content: msg.message?.conversation || msg.message?.extendedTextMessage?.text || '',
          timestamp: msg.messageTimestamp,
          type: 'text',
          metadata: msg,
        };
        this.emit(MessageEventType.RECEIVED, message);
      }
    });
  }

  async disconnect(): Promise<void> {
    if (this.client) {
      this.client.end();
      this.status = ConnectionStatus.DISCONNECTED;
    }
  }

  async sendMessage(to: string, content: string, options: any = {}): Promise<any> {
    if (!this.client || this.status !== ConnectionStatus.AUTHENTICATED) {
      throw new Error(`WhatsApp client is not connected. Status: ${this.status}`);
    }
  
    try {
      // Verificar conexión antes de enviar
      console.log('🔄 Verifying connection before sending message...');
      await waitForReady(this.client, 10000);
  
      // Agregar un delay aleatorio para simular comportamiento humano
      await delay(Math.random() * 2000 + 500);
  
      // Formatear correctamente el número
      const formattedNumber = to.includes('@s.whatsapp.net')
        ? to
        : `${to.replace(/[^\d]/g, '')}@s.whatsapp.net`;
  
      console.log('📤 Attempting to send message to:', formattedNumber);
      const messageContent = { text: content };
  
      const msg = await this.client.sendMessage(formattedNumber, messageContent);
      console.log('✅ Message sent response:', msg);
  
      if (!msg) {
        throw new Error('Failed to send message: No response from WhatsApp');
      }
  
      const message: Message = {
        id: msg.key.id,
        from: msg.key.remoteJid || '',
        to: formattedNumber,
        content,
        timestamp: Date.now(),
        type: 'text',
        metadata: msg,
      };
  
      this.emit(MessageEventType.SENT, message);
      return message;
    } catch (error) {
      console.error('❌ Error sending message:', {
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        status: this.status,
        clientState: this.client?.state,
      });
      throw error;
    }
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
}
