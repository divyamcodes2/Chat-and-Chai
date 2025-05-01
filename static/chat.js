// Create a new socket.io instance, establishing a connection to the server
let socket = io();

// Set the current room to "General"
let currentRoom = "General";

// Get the username from an HTML element with the id "username"
let username = document.getElementById("username").textContent;

// Initialize an object to store messages for each room
let roomMessages = {};

// Socket event listeners
socket.on("connect", () => {
  joinRoom("General");
  highlightActiveRoom("General");
});

socket.on("message", (data) => {
  // Display public message in chat
  addMessage(
    data.username,
    data.msg,
    data.username === username ? "own" : "other"
  );
});

socket.on("private_message", (data) => {
  // Display private message in chat
  addMessage(data.from, `[Private] ${data.msg}`, "private");
});

socket.on("status", (data) => {
  // Display system status message
  addMessage("System", data.msg, "system");
});

socket.on("active_users", (data) => {
  // Update list of active users
  const userList = document.getElementById("active-users");
  userList.innerHTML = data.users
    .map(
      (user) => `
            <div class="user-item" onclick="insertPrivateMessage('${user}')">
                ${user} ${user === username ? "(you)" : ""}
            </div>
        `
    )
    .join("");
});

// Message handling
function addMessage(sender, message, type) {
  // Check if the current room has a messages array in the roomMessages object
  if (!roomMessages[currentRoom]) {
    // If not, create a new array for the current room
    roomMessages[currentRoom] = [];
  }

  // Add the new message to the current room's messages array
  roomMessages[currentRoom].push({ sender, message, type });

  // Get the chat element from the HTML
  const chat = document.getElementById("chat");

  // Create a new div element to hold the message
  const messageDiv = document.createElement("div");

  // Set the class of the message div to "message" and the type (e.g. "own", "other", "private")
  messageDiv.className = `message ${type}`;

  // Set the text content of the message div to the sender's name and the message
  messageDiv.textContent = `${sender}: ${message}`;

  // Add the message div to the chat element
  chat.appendChild(messageDiv);

  // Scroll the chat element to the bottom to show the new message
  chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById("message");
  const message = input.value.trim();

  if (!message) return; // If there are no messages then we will not proceed further

  if (message.startsWith("@")) {
    // Send private message

    // Extract target and message parts by splitting message string after first character
    const [target, ...msgParts] = message.substring(1).split(" ");
    const privateMsg = msgParts.join(" "); // Join parts into one message string

    if (privateMsg) {
      // Send private message to target user via socket
      socket.emit("message", {
        msg: privateMsg, // Message content
        type: "private", // Message type (private)
        target: target, // Target user
      });
    }
  } else {
    // Send room message
    socket.emit("message", {
      msg: message,
      room: currentRoom,
    });
  }

  input.value = ""; // Clear the input field
  input.focus(); // Focus the input field
}

function joinRoom(room) {
  // Leave the current room
  socket.emit("leave", { room: currentRoom });

  currentRoom = room;

  // Join the new room
  socket.emit("join", { room });

  highlightActiveRoom(room); // Highlight the new active room

  const chat = document.getElementById("chat");

  chat.innerHTML = ""; // Clear chat history

  // Restore previous messages for the room
  if (roomMessages[room]) {
    roomMessages[room].forEach((msg) => {
      addMessage(msg.sender, msg.message, msg.type); // Call addMessage with sender, message, and type
    });
  }
}

function insertPrivateMessage(user) {
  // Pre-fill message input with @username for private messaging
  document.getElementById("message").value = `@${user} `;
  document.getElementById("message").focus(); // Focus the input field so user can start typing
}

function handleKeyPress(event) {
  // Check if "Enter" is pressed without Shift
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault(); // Prevent default newline or form submission
    sendMessage(); // Trigger message sending
  }
}

// Initialize chat when page loads
let chat;
document.addEventListener("DOMContentLoaded", () => {
  // DOMContentLoaded is fired when the initial HTML is loaded and parsed
  chat = new ChatApp();

  // Request browser notification permissions
  if ("Notification" in window) {
    Notification.requestPermission();
  }
});

// Handle room highlighting
function highlightActiveRoom(room) {
  // Loop through all room items and remove highlight
  document.querySelectorAll(".room-item").forEach((item) => {
    item.classList.remove("active-room");

    // Highlight the selected room
    if (item.textContent.trim() === room) {
      item.classList.add("active-room");
    }
  });
}
