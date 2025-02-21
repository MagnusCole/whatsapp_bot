import { WebSocketService } from '../../src/services/websocket/WebSocketServer';
import { WhatsAppPlatform } from '../../src/services/messaging/WhatsAppPlatform';
import { Logger } from '../../src/services/logger/Logger';
import WebSocket from 'ws';
import { join } from 'path';

describe('Concurrency Tests', () => {
    const TEST_PORT = 8082;
    const NUM_CLIENTS = 100;
    const TEST_AUTH_PATH = join(__dirname, '../__fixtures__/auth');
    let wsServer: WebSocketService;
    let whatsapp: WhatsAppPlatform;
    let clients: WebSocket[] = [];

    beforeAll(async () => {
        Logger.initialize();
        wsServer = new WebSocketService(TEST_PORT);
        whatsapp = new WhatsAppPlatform(TEST_AUTH_PATH);
    });

    afterAll(async () => {
        clients.forEach(client => client.close());
        await whatsapp.disconnect();
        wsServer.close();
    });

    it('should handle multiple simultaneous connections', async () => {
        const connectClient = () => {
            return new Promise<WebSocket>((resolve) => {
                const client = new WebSocket(`ws://localhost:${TEST_PORT}`);
                client.on('open', () => resolve(client));
                clients.push(client);
            });
        };

        const connections = Array(NUM_CLIENTS).fill(null).map(() => connectClient());
        await Promise.all(connections);
        expect(clients.length).toBe(NUM_CLIENTS);
    }, 30000);

    it('should handle multiple simultaneous messages', async () => {
        const messages = clients.map((client, index) => {
            return new Promise<void>((resolve) => {
                client.on('message', (data) => {
                    const message = JSON.parse(data.toString());
                    expect(message.data.content).toBe(`Test message ${index}`);
                    resolve();
                });
            });
        });

        // Send messages simultaneously
        await Promise.all(clients.map((_, index) => 
            wsServer.sendMessage('broadcast', `Test message ${index}`)
        ));

        await Promise.all(messages);
    }, 30000);

    it('should maintain performance under load', async () => {
        const start = Date.now();
        
        const messagePromises = clients.map((client, index) => {
            return new Promise<void>((resolve) => {
                client.on('message', () => resolve());
            });
        });

        // Rapid-fire messages
        for (let i = 0; i < NUM_CLIENTS; i++) {
            wsServer.sendMessage('broadcast', `Performance test message ${i}`);
        }

        await Promise.all(messagePromises);
        const duration = Date.now() - start;
        
        Logger.info(`Processed ${NUM_CLIENTS} messages in ${duration}ms`);
        expect(duration).toBeLessThan(5000); // Should process all messages within 5 seconds
    }, 30000);
});