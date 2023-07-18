const eventSource = new EventSource("/overlay_endpoint");
const planter = document.querySelector(".planter");
const container = document.querySelector(".container");
const plant_amt = 25

//Iterates through the amount of plants available and assigns id to match rowid in data
for (let x = 1; x <= plant_amt; x++) {
    const plant_img = document.createElement("img");
    let plant = document.createElement("div");
    plant_img.src = "images/Hole.png";
    plant_img.setAttribute("id", x);
    plant.setAttribute("class", "plant");
    plant.appendChild(plant_img);
    planter.appendChild(plant);
}

eventSource.addEventListener("message", function (event) {
    // Parse the received JSON data
    const data = JSON.parse(event.data);
    console.log(data)
    
    // assigns variables to the data received to run through checks
    for (const dict_data of data) {
        const rowid = dict_data.rowid;
        const username = dict_data.username;
        const growth_cycle = dict_data.growth_cycle;
    }
    // // Iterate over each object in the array
    // data.forEach(function (item) {
    //     // Create a new <div> element
    //     const div = document.createElement("div");

    //     // Generate a unique ID based on the 'rowid' key
    //     const divId = "div-" + item.rowid;

    //     // Set the ID attribute of the <div> element
    //     div.setAttribute("id", divId);

    //     // Set the content of the <div> element
    //     div.textContent = JSON.stringify(item);
    //     console.log(item)

    //     // Append the <div> element to the container
    //     // planter.appendChild(div);
    // });
    // Iterates over each object of dictionary and assigns a variable to the value
});

// Need to write out logic so that 