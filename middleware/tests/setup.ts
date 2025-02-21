import { config } from 'dotenv';
import { join } from 'path';
import { jest } from '@jest/globals';

// Load test environment variables
config({ path: join(__dirname, '../.env.test') });

// Global test timeout
jest.setTimeout(30000);