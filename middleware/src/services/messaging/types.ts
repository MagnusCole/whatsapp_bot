export enum ConnectionStatus {
    DISCONNECTED = 'DISCONNECTED',
    CONNECTING = 'CONNECTING',
    AUTHENTICATED = 'AUTHENTICATED',
    ERROR = 'ERROR'
}

export enum MessageEventType {
    RECEIVED = 'message.received',
    SENT = 'message.sent',
    CONNECTION_UPDATE = 'connection.update'
}

export interface Message {
    id: string;
    from: string;
    to: string;
    content: string;
    timestamp: number;
    type: string;
    metadata?: any;
}