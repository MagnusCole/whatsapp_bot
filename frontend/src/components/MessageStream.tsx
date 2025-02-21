import React, { useEffect, useState, useCallback } from 'react';
import { YourType } from '../types';

interface MessageStreamProps {
    clientId: string;
    onMessage?: (message: Message) => void;
    fallbackUrl?: string;
}

export const MessageStream: React.FC<MessageStreamProps> = ({ clientId, onMessage, fallbackUrl }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
    const [ws, setWs] = useState<WebSocket | null>(null);

    const connectWebSocket = useCallback(() => {
        const wsUrl = `ws://localhost:8000/ws/${clientId}`;
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            setWsStatus('connected');
            console.log('WebSocket connected');
        };

        socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            setMessages(prev => [...prev, message]);
            onMessage?.(message);
        };

        socket.onclose = () => {
            setWsStatus('disconnected');
            console.log('WebSocket disconnected, attempting to reconnect...');
            // Attempt to reconnect after 5 seconds
            setTimeout(connectWebSocket, 5000);

            // If fallback URL is provided, register for webhook updates
            if (fallbackUrl) {
                registerWebhook();
            }
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            socket.close();
        };

        setWs(socket);
    }, [clientId, onMessage, fallbackUrl]);

    const registerWebhook = async () => {
        if (!fallbackUrl) return;

        try {
            const response = await fetch(`http://localhost:8000/webhook/register/${clientId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ webhook_url: fallbackUrl }),
            });

            if (!response.ok) {
                throw new Error('Failed to register webhook');
            }

            console.log('Webhook registered successfully');
        } catch (error) {
            console.error('Error registering webhook:', error);
        }
    };

    const sendMessage = useCallback((content: string) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ content }));
        } else {
            console.error('WebSocket is not connected');
        }
    }, [ws]);

    useEffect(() => {
        connectWebSocket();

        return () => {
            if (ws) {
                ws.close();
            }
        };
    }, [connectWebSocket]);

    return (
        <div className="message-stream">
            <div className="status-bar">
                Connection Status: {wsStatus}
            </div>
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className="message">
                        <span className="timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                        <span className="content">{msg.content}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};