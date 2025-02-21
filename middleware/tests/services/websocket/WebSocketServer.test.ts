import { WebSocketService } from '../../../src/services/websocket/WebSocketServer';
import { ConnectionStatus, MessageEventType } from '../../../src/services/messaging/MessagingPlatform';
import WebSocket from 'ws';

describe('WebSocketServer', () => {
    let wsServer: WebSocketService;
    const TEST_PORT = 8081;
    let client: WebSocket;

    beforeEach((done) => {
        wsServer = new WebSocketService(TEST_PORT);
        client = new WebSocket(`ws://localhost:${TEST_PORT}`);
        client.on('open', () => done());
    });

    afterEach((done) => {
        client.close();
        wsServer.close();
        done();
    });

    it('should initialize with connected status', () => {
        expect(wsServer.getStatus()).toBe(ConnectionStatus.CONNECTED);
    });

    it('should handle client connections', (done) => {
        wsServer.onConnectionUpdate((update) => {
            expect(update.status).toBe(ConnectionStatus.CONNECTED);
            done();
        });
    });

    it('should broadcast messages to connected clients', (done) => {
        const testMessage = {
            content: 'Test broadcast message',
            to: 'broadcast'
        };

        client.on('message', (data) => {
            const message = JSON.parse(data.toString());
            expect(message.data.content).toBe(testMessage.content);
            done();
        });

        wsServer.sendMessage(testMessage.to, testMessage.content);
    });

    it('should handle client disconnection', (done) => {
        wsServer.onConnectionUpdate((update) => {
            if (update.status === ConnectionStatus.DISCONNECTED) {
                done();
            }
        });
        client.close();
    });

    it('should queue messages for disconnected clients', async () => {
        client.close();
        await wsServer.sendMessage('offline-client', 'Queued message');
        expect(wsServer.getStatus()).toBe(ConnectionStatus.CONNECTED);
    });
});