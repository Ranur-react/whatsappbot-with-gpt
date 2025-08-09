import {axiosGPTMakeRequest} from './axiosGPTMakeRequest.js';

const respondBuilderText = async (body, state = {}, receiver) => {
    const responses = {
        "info": {
            text: "Silakan pilih informasi layanan dengan mengetik angka nomor opsi layanan:\n1. Informasi Login\n2. Informasi Lokasi Absensi\n3. Informasi Nomor Whatsapp Guru\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: "infoMenu"
        },
        "Chat Dengan AI": {
            text: "Silakan pilih topik layanan Live Chat AI Assistance dengan mengetik angka nomor opsi layanan:\n1. Tanya Asisten soal kehadiran kamu \n2. Tanya Asisten soal data-data kamu \n3. Random Chat dengan AI\n\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: "gpt"
        },
        "gpt_1": {
            text: "Silahkan, Apakah ada yang bisa aku bantu  soal kehadiran kamu \n\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: "gpt_1"
        },
        "gpt_2": {
            text: "Silahkan, Apakah ada yang bisa aku bantu soal data-data absensi kamu\n\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: "gpt_2"
        },
        "gpt_3": {
            text: "Silahkan katakan apapun, Apakah ada yang bisa aku bantu ? \n\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: "gpt_2"
        },
        "infoMenu_2": {
            text: "Pengambilan absen wajib paling jauh di depan gerbang sekolah untuk dapat dianggap sebagai masuk dan berada di area sekolah.\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: "infoMenu"
        },
        "infoMenu_3": {
            text: "Berikut nomor kontak guru yang bertanggung jawab dan memonitor aplikasi Absensi:\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: "infoMenu"
        },
        "Tentang Kami": {
            text: "Absekol (Aplikasi Absensi Sekolah) dikembangkan oleh mahasiswa STMIK Jayanusa dengan nomor BP.202007\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: state.currentState
        },
        default: {
            text: "Perintah tidak dikenali. Silakan coba lagi.\n\nKetik 'Home' untuk kembali ke menu utama.",
            nextState: state.currentState
        }
    };
    let key = `${state.currentState ? state.currentState + "_" : ""}${body}`.trim() || body;
    //jika memilih salah satu menu gpt
    console.log('=============Current State=======================');
    console.log(state.currentState);
    console.log('====================================');
    console.log('=============Body Chat User=======================');
    console.log(body);
    console.log('====================================');
    if (state.currentState == "gpt_1" || state.currentState == "gpt_2"){
        key = `${state.currentState}_respond`;


        const user = await CallDataUser(receiver);
        console.log('===========Call Data User Respond=========================');
        console.log(user);
        console.log('====================================');

        const respondGpt = await axiosGPTMakeRequest(receiver, body, JSON.stringify(user))
        console.log('==================Respond chat GPT==================');
        console.log(respondGpt);
        console.log('====================================');
        responses["gpt_1_respond"] = {
            text: `${respondGpt}  \n\n_Ketik 'Home' untuk kembali ke menu utama._`,
            nextState: "gpt_1"
        };
        responses["gpt_2_respond"] = {
            text: `${respondGpt} " + "\n\n_Ketik 'Home' untuk kembali ke menu utama._`,
            nextState: "gpt_2"
        };
        responses["gpt_3_respond"] = {
            text: `${respondGpt} " + "\n\n_Ketik 'Home' untuk kembali ke menu utama._`,
            nextState: "gpt_3"
        };

    } 
    // else if (state.currentState == "gpt_2") {
    //     key = state.currentState;
    //     responses["gpt_2"] = {
    //         text: "{{Respond dari  AI Topik 2 V2}}" + "\n\nKetik 'Home' untuk kembali ke menu utama.",
    //         nextState: "gpt"
    //     };
    // }
    //jika menu gpt tidak ada yang
    else{
        if (receiver) {
            try {
                console.log('===========Receiver=========================');
                console.log(receiver);
                console.log('====================================');
                const user = await CallDataUser(receiver);
                console.log('===========Call Data User Respond=========================');
                console.log(user);
                console.log('====================================');
                if (user != null) {
                    const { username, email, Role: { roleName } } = user;
                    responses["infoMenu_1"] = {
                        text: `Akun Anda terdaftar pada aplikasi Absekol dengan detail berikut:\nUsername: ${username}\nEmail: ${email}\nRole: ${roleName}\n\nKetik 'Home' untuk kembali ke menu utama.`,
                        nextState: "infoMenu"
                    };
                } else {
                    responses["infoMenu_1"] = {
                        text: `Akun Anda belum terdaftar pada aplikasi Absekol.\n\nKetik 'Home' untuk kembali ke menu utama.`,
                        nextState: "infoMenu"
                    };
                }

            } catch (error) {
                console.error("Error fetching user data:", error);
                responses["infoMenu_1"] = {
                    text: "Maaf, terjadi kesalahan saat mengambil data pengguna. Silakan coba lagi nanti.\n\nKetik 'Home' untuk kembali ke menu utama.",
                    nextState: "infoMenu"
                };
            }
        } else {
            responses["infoMenu_1"] = {
                text: "Maaf, terjadi kesalahan saat mengambil data pengguna. Silakan coba lagi nanti.\n\nKetik 'Home' untuk kembali ke menu utama.",
                nextState: "infoMenu"
            };
        }

    }
    
    console.log('=============Key=======================');
    console.log(key);
    console.log('====================================');
    console.log('============Respond Chat Info========================');
    console.log(`below text body respond from  ${receiver}:`);
    console.log(body);
    console.log('====================================');

    return responses[key] || responses.default;
};

const CallDataUser = async (receiver) => {
    const requestOptions = {
        method: "GET",
        redirect: "follow"
    };

    try {
        const response = await fetch("https://absekol-api.numpang.my.id/api/users/nowa/" + receiver, requestOptions);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error fetching user data:", error);
        throw error;
    }
};


export default respondBuilderText;
