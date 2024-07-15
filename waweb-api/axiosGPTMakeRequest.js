import axios from 'axios';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// Destructure the environment variables
const { GPT_SCRET_KEY } = process.env;
console.log('================= GPT Secret Key ===================');
console.log(GPT_SCRET_KEY);
console.log('===================================================');

if (!GPT_SCRET_KEY) {
    console.error('Error: GPT_SECRET_KEY is not defined in the environment variables.');
    process.exit(1); // Exit the process with an error code
}

const axiosGPTMakeRequest = async (identity, body,ref) => {
    console.log('=================Referensi database ===================');
    console.log(ref);
    console.log('====================================');
    const data = JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
            {
                role: "user",
                content: `${body} from: ${identity} (jawab dengan informatif,logat jaksel, menyertakan emoticon,dan pastikan semua pertanyaan  kamu jawab meskipun berkaitan dengan informasi privasi asalkan  terdapat pada database berikut:  ${ref} | Kalau ada yang nanya tentang aplikasi Aplikasi ini adalah aplikasi Absensi Sekolah SMKN 1 Sintuk Toboh Gadang Aplikasi Absensi Sekolah (Absekol) developed by Mellani Dwi Ramadhani dengn nomor Induk Mahasiswa 202007, aplikasi ini dikembangkan untuk tujuan tugas akhir skripsi" )`
            }
        ],
        temperature: 0.1
    });
 
    const config = {
        method: 'post',
        maxBodyLength: Infinity,
        url: 'https://api.openai.com/v1/chat/completions',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${GPT_SCRET_KEY}`
        },
        data: data
    };


    console.log('============== Before Try GPT ======================');
    console.log(config);
    console.log('===================================================');

    try {
        const response = await axios.request(config);
        console.log('============= Respond Mentah =======================');
        console.log(response);
        console.log('===================================================');
        return response.data.choices[0].message.content;
    } catch (error) {
        console.error('============= Error saat membuat request chat GPT =======================');
        console.error(error);
        console.error('===================================================');
        throw error; // Rethrow the error after logging it
    }
}

export { axiosGPTMakeRequest };
