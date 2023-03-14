import { createServer } from 'http';
import { logger } from './logger';

const server = createServer((_req, res) => {
	logger.trace("Received a request on keep_alive");
	res.writeHead(200);
	res.end("Alive");
});

export const replitStart = () => {
	server.listen(8080);
};

export const replitStop = () => {
	server.close();
};
