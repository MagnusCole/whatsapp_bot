import { WebSocket } from 'ws';
import { describe, expect, test, beforeEach, afterEach, jest } from '@jest/globals';

describe('WebSocket Connection', () => {
    let ws: WebSocket;
    const TEST_SERVER_URL = 'ws://localhost:8000';

    beforeEach(() => {
        ws = new WebSocket(TEST_SERVER_URL);
    });

    afterEach(() => {
        ws.close();
    });

    test('should establish connection successfully', (done) => {
        ws.on('open', () => {
            expect(ws.readyState).toBe(WebSocket.OPEN);
            done();
        });
    });

    test('should handle message receiving', (done) => {
        const mockMessage = { type: 'test', content: 'Hello' };

        ws.on('message', (data) => {
            const message = JSON.parse(data.toString());
            expect(message).toEqual(mockMessage);
            done();
        });

        // Simulate receiving a message
        ws.emit('message', Buffer.from(JSON.stringify(mockMessage)));
    });

    test('should handle connection closure', (done) => {
        ws.on('close', () => {
            expect(ws.readyState).toBe(WebSocket.CLOSED);
            done();
        });

        ws.close();
    });

    test('should handle connection errors', (done) => {
        ws.on('error', (error) => {
            expect(error).toBeDefined();
            done();
        });

        // Simulate an error
        ws.emit('error', new Error('Test error'));
    });
});