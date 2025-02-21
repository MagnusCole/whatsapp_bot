/**
 * Abstract interface for messaging platform integration
 */
export interface MessagingPlatform {
    connect(): Promise<void>;
    disconnect(): Promise<void>;
    sendMessage(to: string, content: string, options?: any): Promise<any>;
    onMessage(callback: (message: any) => void): void;
    onConnectionUpdate(callback: (update: any) => void): void;
    getStatus(): string;
}

/**
 * Event types for messaging platform
 */
export enum MessageEventType {
    RECEIVED = 'message.received',
    SENT = 'message.sent',
    DELIVERED = 'message.delivered',
    READ = 'message.read',
    CONNECTION_UPDATE = 'connection.update'
}

/**
 * Base message structure
 */
export interface Message {
    id: string;
    from: string;
    to: string;
    content: string;
    timestamp: number;
    type: string;
    metadata?: any;
}

/**
 * Connection status types
 */
export enum ConnectionStatus {
    CONNECTING = 'connecting',
    CONNECTED = 'connected',
    DISCONNECTED = 'disconnected',
    AUTHENTICATED = 'authenticated',
    ERROR = 'error'
}