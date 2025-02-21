import { WhatsAppPlatform } from '../../../src/services/messaging/WhatsAppPlatform';
import { ConnectionStatus, MessageEventType } from '../../../src/services/messaging/MessagingPlatform';
import { join } from 'path';

describe('WhatsAppPlatform', () => {
    let platform: WhatsAppPlatform;
    const testAuthPath = join(__dirname, '../../__fixtures__/auth');

    beforeEach(() => {
        platform = new WhatsAppPlatform(testAuthPath);
    });

    afterEach(async () => {
        await platform.disconnect();
    });

    it('should initialize with disconnected status', () => {
        expect(platform.getStatus()).toBe(ConnectionStatus.DISCONNECTED);
    });

    it('should emit connection updates', (done) => {
        platform.onConnectionUpdate((update) => {
            expect(update.status).toBe(ConnectionStatus.CONNECTING);
            done();
        });
        platform.connect();
    });

    it('should handle message events', (done) => {
        const testMessage = {
            content: 'Test message',
            to: '1234567890@s.whatsapp.net'
        };

        platform.onMessage((message) => {
            expect(message.content).toBe(testMessage.content);
            expect(message.to).toBe(testMessage.to);
            done();
        });

        // Simulate incoming message
        platform.emit(MessageEventType.RECEIVED, {
            ...testMessage,
            id: '123',
            from: 'sender',
            timestamp: Date.now(),
            type: 'text'
        });
    });
});