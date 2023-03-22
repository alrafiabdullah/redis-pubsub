
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#txt-form');
    const closeBtn = document.querySelector('#close-btn');
    const ulMsg = document.querySelector('#messages');
    const selectOption = document.querySelector('#room-list');
    let scrollableMsg = document.querySelector('#scrollable-message');


    let selectedRoom = selectOption.value;

    let socket = new WebSocket(`wss://redis.abdullahalrafi.trade/redis/pubsub/${selectedRoom}`);

    selectOption.addEventListener('change', (e) => {
        selectedRoom = e.target.value;
        socket.close();
        socket = new WebSocket(`wss://redis.abdullahalrafi.trade/redis/pubsub/${selectedRoom}`);

        ulMsg.innerHTML = "";

        socket.onmessage = event => {
            console.log('WebSocket message received:', typeof event.data);

            // get only hello from the message
            const data = JSON.parse(event.data);
            const li = document.createElement('li');
            li.className = "alert alert-info";
            li.innerHTML = data.message;
            ulMsg.appendChild(li);
        };

        scrollableMsg.scrollTop = scrollableMsg.scrollHeight;
    });

    socket.onopen = () => {
        // console.log('WebSocket connected');
    };
    socket.onerror = error => {
        console.error('WebSocket error:', error);
    };
    socket.onmessage = event => {
        // console.log('WebSocket message received:', event.data);
        const data = JSON.parse(event.data);
        const li = document.createElement('li');
        li.className = "alert alert-info";
        li.innerHTML = data.message;
        ulMsg.appendChild(li);

        scrollableMsg.scrollTop = scrollableMsg.scrollHeight;
    };
    socket.onclose = event => {
        // console.log('WebSocket closed with code:', event.code);
    };


    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const text = document.querySelector('#mess').value.slice(0, 50);

        const data = {
            message: text
        };


        socket.send(JSON.stringify(data));

        document.querySelector('#mess').value = "";
    });

    closeBtn.addEventListener('click', (e) => {
        socket.close();
    });

});