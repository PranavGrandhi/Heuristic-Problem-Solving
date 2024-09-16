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
    WAITING: "Waiting for players...",
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
let player_name, opponent_name;
let current_player = 1;
let player_cards = [];
let opponent_cards = [];
let played_cards = []; 



// for debugging visuals
// init_game_data(1, 100);

/* FUNCTIONS */
socket.onopen = function (event) {
    document.getElementById("game-message").textContent = GAME_MESSAGE.WAITING;
    game_state = GAME_STATE.WAITING;
};

socket.onmessage = function (event) {
    console.log(event.data);
    let pdata = event.data.split(" ");
    if (game_state == GAME_STATE.WAITING) { // called once initially
        player_name = pdata[0];
        opponent_name = pdata[1];
        init_game_data(Number(pdata[2]), Number(pdata[3]));
        // document.getElementById("game-message").textContent = player_name + " vs " + opponent_name;
    } else if (game_state == GAME_STATE.IDLING) {
        receive_state(Number(pdata[0]), Number(pdata[1]));
    }
};

function init_game_data(max_stones, max_cards) {
    number_of_stones = max_stones;
    number_of_cards = max_cards;
    player_cards = Array.from({ length: number_of_cards }, (_, index) => index + 1);
    opponent_cards = Array.from({ length: number_of_cards }, (_, index) => index + 1);
    initialize_game_container(true);
    document.getElementById("game-message").textContent = GAME_MESSAGE.NONE;
    game_state = GAME_STATE.IDLING;
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

    // Apply the correct card class for general styling
    card.classList.add(is_players_card ? "player-card" : "opponent-card");

    // Apply the specific class for player1 or player2 styling
    if (is_players_card) {
        card.classList.add(is_players_turn ? "player1-card" : "player2-card");
        card.id = CARD_ID_PREFIX.PLAYER + card_number;
        card.innerHTML = 
            `<span class="player-top-left-value">${card_number}</span>` +
            `<span class="player-center-value">${card_number}</span>` +
            `<span class="player-bottom-right-value">${card_number}</span>`;
    } else {
        card.classList.add(!is_players_turn ? "player1-card" : "player2-card");
        card.id = CARD_ID_PREFIX.OPPONENT + card_number;
        card.innerHTML =
            `<span class="opponent-top-left-value">${card_number}</span>` +
            `<span class="opponent-center-value">${card_number}</span>` +
            `<span class="opponent-bottom-right-value">${card_number}</span>`;
    }

    if (is_players_card) {
        document.getElementById("player-container").appendChild(card);
    } else {
        document.getElementById("opponent-container").appendChild(card);
    }
}

function receive_state(new_number_of_stones, time_left) {
    if (time_left == 0) {
        document.getElementById("game-message").textContent = (current_player == 1 ? p2_name : p1_name) + " wins by default!";
        return;
    }
    
    const card_number = number_of_stones - new_number_of_stones;
    number_of_stones = new_number_of_stones;
    
    if (current_player == 2) {
        use_card(card_number, false);    
        update_pickaxe_state(true, true);
        update_pickaxe_state(false, true);
    
        if (new_number_of_stones > 0) {
            render_stones();
        } else {
            update_pickaxe_state(true, false);
            end_display(!number_of_stones);
            game_state = GAME_STATE.DONE;
        }
    }
    else {
        use_card(card_number, true);
        update_pickaxe_state(true, false);
        update_pickaxe_state(false, false);
        
        if (number_of_stones > 0) {
            render_stones();
        } 
        else {
            update_pickaxe_state(false, true);
            end_display(number_of_stones);
        }
    }
    current_player = 3 - current_player;
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

function use_card(card_number, is_players_card) {
    played_cards.push({ number: card_number, player: is_players_card ? "player" : "opponent" });
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
    const player_pickaxe = document.getElementById("player-container").querySelector(".pickaxe");
    const opponent_pickaxe = document.getElementById("opponent-container").querySelector(".pickaxe");
    if (number_of_stones == 0) {
        let str =
            `<div class=\"verbose-container\" style=\"margin-left: 100px; margin-top: 10px;\">
                <p>` + player_name + ` wins!</p>
            </div>`;
        document.getElementById("stone-container").innerHTML = str;
        
        player_pickaxe.src = IMAGES.WINNER;
        opponent_pickaxe.src = IMAGES.LOSER;
    }
    else {
        let str =
            `<div class=\"verbose-container\" style=\"margin-left: 100px; margin-top: 10px;\">
                <p>` + opponent_name + ` wins!</p>
            </div>`;
        document.getElementById("stone-container").innerHTML = str;
        opponent_pickaxe.src = IMAGES.WINNER;
        player_pickaxe.src = IMAGES.LOSER;
    }
    player_pickaxe.classList.remove("pickaxe-hide");
    opponent_pickaxe.classList.remove("pickaxe-hide");
}