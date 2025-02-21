import winston from 'winston';

/**
 * Logger configuration and setup
 */
export class Logger {
    private static instance: winston.Logger;

    /**
     * Initialize the logger with custom configuration
     */
    public static initialize() {
        if (!Logger.instance) {
            Logger.instance = winston.createLogger({
                level: process.env.LOG_LEVEL || 'info',
                format: winston.format.combine(
                    winston.format.timestamp(),
                    winston.format.json()
                ),
                transports: [
                    new winston.transports.Console({
                        format: winston.format.combine(
                            winston.format.colorize(),
                            winston.format.simple()
                        )
                    }),
                    new winston.transports.File({ 
                        filename: 'error.log', 
                        level: 'error' 
                    }),
                    new winston.transports.File({ 
                        filename: 'combined.log' 
                    })
                ]
            });
        }
        return Logger.instance;
    }

    /**
     * Get the logger instance
     */
    public static getInstance(): winston.Logger {
        if (!Logger.instance) {
            Logger.initialize();
        }
        return Logger.instance;
    }

    /**
     * Log an info message
     */
    public static info(message: string, meta?: any) {
        Logger.getInstance().info(message, meta);
    }

    /**
     * Log an error message
     */
    public static error(message: string, meta?: any) {
        Logger.getInstance().error(message, meta);
    }

    /**
     * Log a warning message
     */
    public static warn(message: string, meta?: any) {
        Logger.getInstance().warn(message, meta);
    }

    /**
     * Log a debug message
     */
    public static debug(message: string, meta?: any) {
        Logger.getInstance().debug(message, meta);
    }
}