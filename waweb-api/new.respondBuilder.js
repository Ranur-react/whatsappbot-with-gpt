import axios from 'axios';

const respondBuilderText = async (body, state = {}, userId) => {
    let responses = {
        "info": {
            text: "Silakan pilih informasi layanan dengan mengetik angka nomor opsi layanan:\n1. Informasi Login\n2. Informasi Lokasi Absensi\n3. Informasi Nomor Whatsapp Guru",
            nextState: "infoMenu"
        },
        "infoMenu_2": {
            text: "Pengambilan absen wajib paling jauh di depan gerbang sekolah untuk dapat dianggap sebagai masuk dan berada di area sekolah.",
            nextState: "infoMenu"
        },
        "infoMenu_3": {
            text: "Berikut nomor kontak guru yang bertanggung jawab dan memonitor aplikasi Absensi: ",
            nextState: "infoMenu"
        },
        "Tentang Kami": {
            text: "Absekol (Aplikasi Absensi Sekolah) dikembangkan oleh mahasiswa STMIK Jayanusa dengan nomor BP.202007",
            nextState: state.currentState
        },
        default: {
            text: "Perintah tidak dikenali. Silakan coba lagi.",
            nextState: state.currentState
        }
    };
    console.log('=================Decalre Data default===================');
    console.log(responses);
    console.log('====================================');

    const key = `${state.currentState ? state.currentState + "_" : ""}${body}`.trim() || body;
    console.log('==============Current Key XX======================');
    console.log(key);
    console.log('====================================');
    // Dynamic user data fetching
    if (key === 'infoMenu_1') {
        try {


            // let config = {
            //     method: 'get',
            //     maxBodyLength: Infinity,
            //     url: 'https://absekol-api.numpang.my.id/api/users/nowa/',
            //     headers: {}
            // };

            // axios.request(config)
            //     .then((response) => {
            //         console.log(JSON.stringify(response.data));
            //     })
            //     .catch((error) => {
            //         console.log(error);
            //     });

            const userResponse = await axios.get('https://absekol-api.numpang.my.id/api/users/nowa/' + userId); // Replace with your API endpoint
            const userdata = userResponse.data;
            if (userdata != null) {
                responses["infoMenu_1"] = {
                    text: `Akun Anda terdaftar pada aplikasi Absekol dengan detail berikut:\nUsername: ${username}\nEmail: ${useremail}\nPassword: ${password}\nRole: ${RoleName}`,
                    nextState: "infoMenu"
                };
            } else {
                responses["infoMenu_1"] = {
                    text: "Maaf, terjadi kesalahan saat mengambil data pengguna. Silakan coba lagi nanti.",
                    nextState: "infoMenu"
                };
            }

        } catch (error) {
            console.error("Error fetching user data:", error);
            responses["infoMenu_1"] = {
                text: "Maaf, terjadi kesalahan saat mengambil data pengguna. Silakan coba lagi nanti.",
                nextState: "infoMenu"
            };
        }
        console.log('================Respind get Menu Info Login====================');
        console.log(responses["infoMenu_1"]);
        console.log('====================================');
    }
    responses["infoMenu_1"] = {
        text: "test",
        nextState: "infoMenu"
    };

    return responses[key] || responses.default;
};

export default respondBuilderText;
