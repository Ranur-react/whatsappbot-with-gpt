import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const { GRAPH_API_TOKEN } = process.env;

export function axiosInstance({
    baseURL = 'https://graph.facebook.com/v22.0/',
    token = GRAPH_API_TOKEN,
    contentType = 'application/json',
    extraHeaders = {},
} = {}) {
    return axios.create({
        baseURL,
        headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
            'Content-Type': contentType,
            ...extraHeaders,
        },
    });
}

// Contoh penggunaan:
// const api = createAxiosInstance(); // default Facebook Graph API
// const customApi = createAxiosInstance({ baseURL: 'https://api.example.com', token: 'your-token' });