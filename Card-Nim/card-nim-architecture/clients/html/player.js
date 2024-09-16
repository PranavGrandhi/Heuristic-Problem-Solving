/* CONSTANTS */
const GAME_STATE = {
    CONNECTING: "connecting",
    WAITING: "waiting",
    PLAYING: "playing",
    IDLING: "idling",
    DONE: "done",
};
const SERVER_URL = "ws://localhost:4000/"; // change to server address
const GAME_MESSAGE = {
    CONNECTING: "Connecting to server...",
    WAITING: "Waiting for other players...",
    NONE: "",
};
const CARD_ID_PREFIX = {
    PLAYER: "player_",
    OPPONENT: "opponent_",
};
const IMAGES = {
    STONE: "images/stone.png",
    ARROW: "images/arrow.png",
    WINNER: "images/winner.png",
    LOSER: "images/loser.png",
};


/* GLOBAL VARIABLES */
let socket = new WebSocket(SERVER_URL);
let game_state = GAME_STATE.CONNECTING;
document.getElementById("game-message").textContent = GAME_MESSAGE.CONNECTING;
let number_of_stones = 0;
let number_of_cards = 0;
let player_cards = [];
let opponent_cards = [];
let played_cards = []; 
let prev_rocks = 200;
let player_number = 1


// for debugging visuals
// init_game_data(1, 100);

/* FUNCTIONS */
socket.onopen = function (event) {
    document.getElementById("game-message").textContent = GAME_MESSAGE.WAITING;
    game_state = GAME_STATE.WAITING;
};

socket.onmessage = function (event) {
    if (game_state == GAME_STATE.WAITING) { // called once initially
        let pdata = event.data.split(" ");
        init_game_data(Number(pdata[0]), Number(pdata[1]), Number(pdata[2]));
    } else if (game_state == GAME_STATE.IDLING) {
        receive_state(Number(event.data));
    }
};

function init_game_data(player_num, max_stones, max_cards) {
    number_of_stones = max_stones;
    number_of_cards = max_cards;
    player_cards = Array.from({ length: number_of_cards }, (_, index) => index + 1);
    opponent_cards = Array.from({ length: number_of_cards }, (_, index) => index + 1);
    player_number = player_num;
    initialize_game_container(player_num == 1);
    document.getElementById("game-message").textContent = GAME_MESSAGE.NONE;
    if (player_num == 2) {
        socket.send("getstate");
        game_state = GAME_STATE.IDLING;
    } else {
        game_state = GAME_STATE.PLAYING;
    }
}

function initialize_game_container(is_players_turn) {
    // add player cards
    create_pickaxe(true, is_players_turn);
    for (const card of player_cards) {
        create_card(card, true, is_players_turn);
    }
    // add opponent cards
    create_pickaxe(false, is_players_turn);
    for (const card of opponent_cards) {
        create_card(card, false, is_players_turn);
    }
    render_played_cards();
    render_stones();
}

function create_pickaxe(is_players_card, is_players_turn) {
    const pickaxe = document.createElement("img");
    pickaxe.src = IMAGES.ARROW;
    pickaxe.classList.add("pickaxe");
    if (is_players_card ^ is_players_turn) {
        pickaxe.classList.add("pickaxe-hide");
    }
    if (is_players_card) {
        document.getElementById("player-container").appendChild(pickaxe);
    }
    else {
        document.getElementById("opponent-container").appendChild(pickaxe);
    }
}

function create_card(card_number, is_players_card, is_players_turn) {
    const card = document.createElement("button");

    if (is_players_card ^ !is_players_turn) {
        card.classList.add("player1-card");
    }
    else {
        card.classList.add("player2-card");
    }

    if (is_players_card) {
        card.addEventListener('click', function () { make_move(card_number); });
    }

    if (is_players_card && is_players_turn) { card.classList.add("clickable-card"); }

    if (is_players_card) {
        card.id = CARD_ID_PREFIX.PLAYER + card_number;
        card.innerHTML = 
            `<span class = "player-top-left-value">` + card_number + `</span>` +
            `<span class = "player-center-value">` + card_number + `</span>` +
            `<span class = "player-bottom-right-value">` + card_number + `</span>`;
        card.classList.add("player-card");
        document.getElementById("player-container").appendChild(card);
    }
    else {
        card.id = CARD_ID_PREFIX.OPPONENT + card_number;
        card.innerHTML =
            `<span class = "opponent-top-left-value">` + card_number + `</span>` +
            `<span class = "opponent-center-value">` + card_number + `</span>` +
            `<span class = "opponent-bottom-right-value">` + card_number + `</span>`;
        card.classList.add("opponent-card");
        document.getElementById("opponent-container").appendChild(card);
    }
}


function make_move(card_number) {

    // check if valid click
    if (game_state != GAME_STATE.PLAYING) { 
        return; 
    }

    if (card_number >= number_of_stones) {
        gamestate = GAME_STATE.DONE;
    }
    socket.send("sendmove " + card_number);

    number_of_stones -= card_number;
    use_card(card_number, true);
    update_pickaxe_state(true, false);
    for (const card of player_cards) {
        update_card_play_state(card, true, false);
    }
    update_pickaxe_state(false, false);
    for (const card of opponent_cards) {
        update_card_play_state(card, false, false);
    }
    
    if (number_of_stones > 0) {
        game_state = GAME_STATE.IDLING;
        window.setTimeout(socket.send("getstate"), 20);
        render_stones();
    } 
    else {
        update_pickaxe_state(false, true);
        for (const card of opponent_cards) {
            update_card_play_state(card, false, true);
        }
        end_display(number_of_stones);
    }
}

function receive_state(new_number_of_stones) {
    const card_number = number_of_stones - new_number_of_stones;
    number_of_stones = new_number_of_stones;

    use_card(card_number, false);    
    update_pickaxe_state(true, true);
    for (const card of player_cards) {
        update_card_play_state(card, true, true);
    }
    update_pickaxe_state(false, true);
    for (const card of opponent_cards) {
        update_card_play_state(card, false, true);
    }

    if (new_number_of_stones > 0) {
        game_state = GAME_STATE.PLAYING;
        render_stones();
    } else {
        update_pickaxe_state(true, false);
        for (const card of player_cards) {
            update_card_play_state(card, true, false);
        }
        end_display(!number_of_stones);
        game_state = GAME_STATE.DONE;
    }
}

function update_pickaxe_state(is_players_card, is_players_turn) {
    const pickaxe = is_players_card 
        ? document.getElementById("player-container").querySelector(".pickaxe") 
        : document.getElementById("opponent-container").querySelector(".pickaxe");
    if (is_players_card ^ is_players_turn) {
        pickaxe.classList.add("pickaxe-hide");
    }
    else {
        pickaxe.classList.remove("pickaxe-hide");
    }
}

function update_card_play_state(card_number, is_players_card, is_players_turn) {
    const div = is_players_card 
        ? document.getElementById(CARD_ID_PREFIX.PLAYER + card_number) 
        : document.getElementById(CARD_ID_PREFIX.OPPONENT + card_number);
    if (is_players_card && is_players_turn) {
        div.classList.add("clickable-card");
    }
    else {
        div.classList.remove("clickable-card");
    }
}

function use_card(card_number, is_players_card) {
    if (player_number == 1){
        played_cards.push({ number: card_number, player: is_players_card ? "player" : "opponent" });
    }
    else if (player_number == 2){
        played_cards.push({ number: card_number, player: is_players_card ? "opponent" : "player" });
    }
    render_played_cards(); // Re-render played cards

    if (is_players_card) {
        document.getElementById(CARD_ID_PREFIX.PLAYER + card_number).outerHTML = "";
        player_cards = player_cards.filter(function (n) { return n != card_number; });
    } else {
        document.getElementById(CARD_ID_PREFIX.OPPONENT + card_number).outerHTML = "";
        opponent_cards = opponent_cards.filter(function (n) { return n != card_number; });
    }
}

function render_played_cards() {

    const container = document.getElementById("played-cards-container");
    container.innerHTML = ''; // Clear previous content

    for (const card of played_cards) {
        const card_number = card.number;
        const player_type = card.player; // "player" or "opponent"

        const playedCard = document.createElement("button");
        playedCard.classList.add("played-card");

        // Apply the specific class for player1 or player2 styling
        playedCard.classList.add(player_type === "player" ? "player1-card" : "player2-card");

        playedCard.innerHTML =
            `<span class="player-top-left-value">${card_number}</span>` +
            `<span class="player-center-value">${card_number}</span>` +
            `<span class="player-bottom-right-value">${card_number}</span>`;
        
        container.appendChild(playedCard);

    }
}

function render_stones() {
    let str = "";
    if (number_of_stones > 0) {
        str +=
            `<img src="` + IMAGES.STONE + `" class="stone_image" alt="[Stone Image]">
            <p class="stone-count">x ` + number_of_stones + `</p>`;
    }
    
    str += "</div></div>";
    
    document.getElementById("stone-container").innerHTML = str;
}

function end_display(number_of_stones) {
    if (number_of_stones == 0) {
        document.getElementById("game-message").textContent = "You Win!";
        let str =
            `<img src="` + IMAGES.WINNER + `" class="stone_image" alt="[Diamond Image]">
            <p class="stone-count"></p>`;

        str += "</div></div>";
        document.getElementById("stone-container").innerHTML = str;
        
    } else {
        document.getElementById("game-message").textContent = "You Lose";
        let str =
            `<img src="` + IMAGES.LOSER + `" class="stone_image" alt="[Creeper Image]">
            <p class="stone-count"></p>`;
        
        str += "</div></div>";
        document.getElementById("stone-container").innerHTML = str;
    }
}