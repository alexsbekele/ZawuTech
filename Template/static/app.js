const API = "http://127.0.0.1:8000"

// --- Show/Hide Sections ---
function showLogin() {
    document.getElementById("register-section").style.display = "none"
    document.getElementById("login-section").style.display = "block"
    document.getElementById("home-section").style.display = "none"
}

function showRegister() {
    document.getElementById("register-section").style.display = "block"
    document.getElementById("login-section").style.display = "none"
    document.getElementById("home-section").style.display = "none"
}

function showHome() {
    document.getElementById("register-section").style.display = "none"
    document.getElementById("login-section").style.display = "none"
    document.getElementById("home-section").style.display = "block"
}

async function register(){
    const username = document.getElementById("reg-username").value
    const email = document.getElementById("reg-email").value
    const password = document.getElementById("reg-password").value

    const response = await fetch(`${API}/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
    })

    const data = await response.json()

    if (response.ok) {
        document.getElementById("reg-message").textContent = "Account created! Please login."
        document.getElementById("reg-message").style.color = "green"
        setTimeout(() => showLogin(), 1500)  // auto switch to login after 1.5s
    } else {
        document.getElementById("reg-message").textContent = data.detail
        document.getElementById("reg-message").style.color = "red"
    }
}

// --- Login ---

async function login() {
    const username = document.getElementById("log-username").value
    const password = document.getElementById("log-password").value

    const response = await fetch(`${API}/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })

    const data = await response.json()

    if (response.ok) {
        localStorage.setItem("token", data.access_token)
        localStorage.setItem("username", username)
        showHome()
        loadPosts()
    } else {
        document.getElementById("log-message").textContent = data.detail
        document.getElementById("log-message").style.color = "red"
    }
}

// --- Log Out----

function logout() {
    localStorage.removeItem("token")
    localStorage.removeItem("username")
    showLogin()
}

// --- to check if user is logged in on page load ---

window.onload = function() {
    const token = localStorage.getItem("token")
    if (token) {
        showHome()
        loadPosts()
    } else {
        showLogin()
    }
}


// --- Create Post ---
async function createPost() {
    const title = document.getElementById("post-title").value
    const content = document.getElementById("post-content").value
    const imageFile = document.getElementById("post-image").files[0]  // get file
    const token = localStorage.getItem("token")



    let image_url = null

    // Step 1 - if user picked an image, upload it first
    if (imageFile) {
        const formData = new FormData()
        formData.append("file", imageFile)

        const uploadResponse = await fetch(`${API}/upload/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
                // NOTE: no Content-Type here — browser sets it automatically for FormData
            },
            body: formData
        })

        const uploadData = await uploadResponse.json()
        console.log("Upload response:", uploadData)
        if (!uploadResponse.ok) {
            document.getElementById("post-message").textContent = "Image upload failed"
            document.getElementById("post-message").style.color = "red"
            return
        }

        image_url = uploadData.url  // save the returned URL
        console.log("Image URL:", image_url)
    }

    // Step 2 - create the post with or without image
    const response = await fetch(`${API}/posts/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ title, content, image_url })
    })

    const data = await response.json()

    if (response.ok) {
        document.getElementById("post-title").value = ""
        document.getElementById("post-content").value = ""
        document.getElementById("post-image").value = ""
        document.getElementById("post-message").textContent = "Post created!"
        document.getElementById("post-message").style.color = "green"
        loadPosts()
    } else if (response.status === 401) {
        logout()
    } else {
        document.getElementById("post-message").textContent = data.detail
        document.getElementById("post-message").style.color = "red"
    }
}

// --- Load Posts ---
async function loadPosts() {
    const response = await fetch(`${API}/posts/`)
    const posts = await response.json()
    console.log("Posts data:", posts)

    const container = document.getElementById("posts-container")

    if (posts.length === 0) {
        container.innerHTML = "<p>No posts yet. Be the first!</p>"
        return
    }

    container.innerHTML = posts.map(post => `
        <div class="post-card">
            <h4>${post.title}</h4>
            <p>${post.content}</p>
            ${post.image_url ? `<img src="${post.image_url}" alt="post image">` : ""}
            <small>Posted by <strong>${post.author}</strong></small>
        </div>
    `).join("")
}