// Basic types for the WhatsApp bot frontend

export interface Message {
  id: string;
  content: string;
  sender_id: string;
  receiver_id: string;
  timestamp: string;
  status: 'pending' | 'sent' | 'delivered' | 'read';
  metadata?: Record<string, any>;
}

export interface User {
  id: string;
  name: string;
  phone: string;
  status?: 'online' | 'offline' | 'away';
}

export interface Conversation {
  id: string;
  participants: User[];
  messages: Message[];
  status: 'active' | 'archived' | 'deleted';
  last_activity: string;
  metadata?: Record<string, any>;
}