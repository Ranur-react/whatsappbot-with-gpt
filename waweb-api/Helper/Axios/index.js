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
    const instance = axios.create({
        baseURL,
        headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
            'Content-Type': contentType,
            ...extraHeaders,
        },
    });

    instance.interceptors.response.use(
        response => response,
        error => {
            if (error.response && error.response.status !== 200) {
                console.log('API Error Response:', error.response.data);
            }
            return Promise.reject(error);
        }
    );

    return instance;
}

// Contoh penggunaan:
// const api = createAxiosInstance(); // default Facebook Graph API
// const customApi = createAxiosInstance({ baseURL: 'https://api.example.com', token: 'your-token' });