const eventSource = new EventSource("/overlay_endpoint");
const planter = document.querySelector("planter");
const container = document.querySelector("container");

eventSource.addEventListener("message", function (event) {
    // Parse the received JSON data
    const data = JSON.parse(event.data);
    console.log(data)
  
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

    // Iterates over each object of dictionary and assigns a variable to the value
    for (const dict_data of data) {
        // Adds image to the body and assigns the plant class to it.
        // Currently just continues to add everyloop and places images in body not in parent classes, will continue to work on this as well as refactor it
        const plant_img = document.createElement("img");
        plant_img.src = "images/Hole.png";
        plant_img.setAttribute("class", "plant")
        document.body.appendChild(plant_img)
    }
    // });
});

// Need to write out logic so that 