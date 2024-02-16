function populateTeams() {
    var copyFromEpisode = document.getElementById('copyFromEpisode');
    if (copyFromEpisode != undefined) {
        var selectedEpisode = copyFromEpisode.value;
    }

    if (selectedEpisode === "" || selectedEpisode == undefined) {
        selectedEpisode = episode
    };
    // Fetch teams data for the selected episode from the backend
    fetch('/get_teams?episode=' + selectedEpisode)
        .then(response => response.json())
        .then(data => {
            // Update team lists with the fetched data
            data.teams.forEach(team => {
                var teamList = document.getElementById(team.name);
                teamList.innerHTML = '';  // Clear existing options
                for (const [role, castmembers] of Object.entries(team.castmembers)) {
                    for (const castmember of castmembers) {
                        var option = document.createElement('option');
                        option.text = castmember;
                        option.value = castmember;
                        if (role == "man") {
                            option.style.backgroundColor = 'rgb(93, 212, 99)'
                        } else if (role == "woman") {
                            option.style.backgroundColor = 'rgb(236, 236, 192)'
                        } else if (role == "bear") {
                            option.style.backgroundColor = 'crimson'
                        }
                        option.dataset.role = role; // Store the role in dataset
                        teamList.add(option);
                    }
                    // Remove the castmembers from the corresponding old list
                    var oldList = document.getElementById(role);
                    for (var j = 0; j < oldList.options.length; j++) {
                        if (castmembers.includes(oldList.options[j].value)) {
                            oldList.remove(j);
                            j--; // Decrement j to account for the removed option
                        }
                    }
                }
        });
            showConfirmationMessage('Teams copied successfully!');
        })
        .catch((error) => {
            if ((copyFromEpisode != undefined) && (copyFromEpisode.value !== "")) {
                console.error('Error:', error);
                showErrorMessage('Error copying teams. Please try again.');
            }
        });
};