import express from 'express';
import dotenv from 'dotenv';
import routes from './routes.js';
import { logRequests } from './middleware.js';

dotenv.config();

const app = express();
app.use(express.json());
app.use(logRequests);

const { PORT } = process.env;
const port = PORT || 3000;

app.use(routes);

app.listen(port, () => {
    console.log(`Server is listening on port: ${port}`);
});