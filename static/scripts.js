document.getElementById("add-cafe-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    // Gather form data
    const formData = {
        name: document.getElementById("name").value,
        map_url: document.getElementById("map_url").value,
        location: document.getElementById("location").value,
        has_sockets: document.getElementById("has_sockets").checked,
        has_toilet: document.getElementById("has_toilet").checked,
        has_wifi: document.getElementById("has_wifi").checked,
        can_take_calls: document.getElementById("can_take_calls").checked,
        seats: document.getElementById("seats").value || null,
        coffee_price: document.getElementById("coffee_price").value || null
    };

    try {
        // Send POST request to API
        const response = await fetch("/api/cafes", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const result = await response.json();
            alert("Cafe added successfully!");
            console.log("Response:", result);
        } else {
            const error = await response.json();
            alert(`Error: ${error.error}`);
        }
    } catch (error) {
        console.error("Error adding cafe:", error);
        alert("An unexpected error occurred.");
    }
});
