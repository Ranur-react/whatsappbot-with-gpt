
const respondBuilderText = (body, state = {}) => {
    const responses = {
        "info": {
            text: "Silakan pilih informasi layanan dengan mengetik angka nomor opsi layanan:\n1. Informasi Login\n2. Informasi Lokiasi Absensi\n3. Informasi Nomor Whatsapp Guru",
            nextState: "infoMenu"
        },
        "infoMenu_1": {
            text: "Akun anda terdaftar pada aplikasi Absekol dengan deatil berikut:\n Username : ${username} \nEmail: {useremail}\nPassword\nRole: {RoleName}",
            nextState: "infoMenu"
        },
        "infoMenu_2": {
            text: "Pengambilan absen  wajib [aling jauh didepan gerbang sekolah untuk dapat dianggap sebagai masuk dan berada di area sekolah",
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


    const key = `${state.currentState ? state.currentState + "_" : ""}${body}`.trim() || body;
    console.log('=================[body]===================');
    console.log(body);
    console.log('====================================');
    console.log('=================[Key]===================');
    console.log(key);
    console.log('====================================');
    return responses[key] || responses.default;
};
const CallDataUser=async()=>{
    const requestOptions = {
        method: "GET",
        redirect: "follow"
    };

    fetch("https://absekol-api.numpang.my.id/api/users/nowa/6283182415730", requestOptions)
        .then((response) => response.text())
        .then((result) => console.log(result))
        .catch((error) => console.error(error));
}
export default respondBuilderText;