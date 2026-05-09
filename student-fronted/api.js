const baseURL = "http://localhost:8000";

async function request(url, options = {}) {

    const token = localStorage.getItem("token");
    const headers = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers
    };

    try {
        const response = await fetch(`${baseURL}${url}`, {
            ...options,
            headers
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("请求失败：", error);
        alert("网络请求出错，请检查后端服务是否启动");
        throw error;
    }
}


const api = {
    
    login: (data) => request("/api/login", {
        method: "POST",
        body: JSON.stringify(data)
    }),

    register: (data) => request("/api/register", {
        method: "POST",
        body: JSON.stringify(data)
    }),

    getSeats: () => request("/api/seats"),

    reserveSeat: (seatId) => request("/api/reserve", {
        method: "POST",
        body: JSON.stringify({ seat_id: seatId })
    }),

    cancelReserve: (reservationId) => request(`/api/cancel/${reservationId}`, {
        method: "DELETE"
    }),

    getMyReservations: () => request("/api/my/reservations")
};

window.api = api;