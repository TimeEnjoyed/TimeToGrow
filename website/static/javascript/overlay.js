const eventSource = new EventSource("/overlay_endpoint");
const planter = document.querySelector(".planter");
const container = document.querySelector(".container");
const plantAmt = 10

//Iterates through the amount of plants available and assigns id to match rowid in data
for (let x = 1; x <= plantAmt; x++) {
    const plantImg = document.createElement("img");
    const plant = document.createElement("div");
    plantImg.src = "images/Hole.png";
    plantImg.setAttribute("id", `plant${x}`)
    plant.setAttribute("id", x);
    plant.setAttribute("class", "plant");
    plant.appendChild(plantImg);
    planter.appendChild(plant);
}

eventSource.addEventListener("message", function (event) {
    // Parse the received JSON data
    const data = JSON.parse(event.data);
    console.log(data)

    // assigns variables to the data received to run through checks
    for (const dict_data of data) {
        const rowId = dict_data.rowid;
        const username = dict_data.username;
        const growthCycle = dict_data.growth_cycle;
        const water = dict_data.water;
        let plantId = document.getElementById(rowId);
        let nameText = document.getElementById(`user${rowId}`);
        // checks if the user has a plant on the board and if not adds their plant.
        if (nameText == null && username != null) {
            nameText = document.createElement("p");
            nameText.setAttribute("class", "username");
            nameText.setAttribute("id", `user${rowId}`);
            nameText.innerText = username;
            plantId.appendChild(nameText);
            plantImg = document.getElementById(`plant${rowId}`);
            plantImg.src = `images/Step1.png`;
        }
        // checks if name text exists and if username does not (logic currently does not work if username is null) removes the name from overlay and sets back to a hole
        else if (username == null && document.getElementById(`user${rowId}`) != null) {
            nameText.remove()
            plantImg = document.getElementById(`plant${rowId}`);
            plantImg.src = `images/Hole.png`;
        }
        // updates image for the user to the growth cycle it is on
        else if (username != null && document.getElementById(`user${rowId}`) != null && water == 1) {
            plantImg = document.getElementById(`plant${rowId}`);
            plantImg.src = `images/Step${growthCycle}.png`;
        }
    }
});