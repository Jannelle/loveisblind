function saveTeamLists() {
    var teamLists = document.getElementsByClassName('teamList');
    var teamsData = {};

    // First, validate all the teams
    errors = []
    for (var i = 0; i < teamLists.length; i++) {
        var teamName = teamLists[i].getAttribute('id');
        // If any errors, show a message and quit the function
        errors.push(validateTeam(teamName, teamLists[i]))
    }
    
    if (errors.some(element => element !== null)) {
        var errorMessage = errors.join("\r\n"); // Concatenate errors into one string
        showErrorMessage(errorMessage);
        return
    };
    // IF all teams are valid, save the data
    for (var i = 0; i < teamLists.length; i++) {
        var teamName = teamLists[i].getAttribute('id');
        var castmembers = Array.from(teamLists[i].options).reduce((acc, option) => {
            var key = option.dataset.role === 'man' || option.dataset.role === 'woman' ? 'good_members' : 'bad_members';
            if (!acc[key]) {
                acc[key] = [];
            }
            acc[key].push(option.value);
            return acc;
        }, {});
        teamsData[teamName] = castmembers;
    }

    // Include the "episode" variable in the JSON data
    var requestData = {
        episode: episode,
        teams: teamsData
    };

    // Send the data to the backend using AJAX
    fetch('/save_teams', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            showConfirmationMessage('Data saved successfully!');
        })
        .catch((error) => {
            console.error('Error:', error);
            showErrorMessage('Error saving data. Please try again.');
        }
    );
}
    

// 2/19 - we're now allowing multiple members of each role
function validateTeam(teamName, teamList) {
    // Create an object to store options for each origin_list
    var optionsByRole = {};
    // Iterate over the options and group them by origin_list
    Array.from(teamList.options).forEach(option => {
        var role = option.dataset.role;
        if (!optionsByRole[role]) {
            optionsByRole[role] = [];
        }
        optionsByRole[role].push(option.value);
    });

    
    // Check for multiple options for "man", "woman", and "bear" for each origin_list
    var errors = []

    manOptions = optionsByRole['man']
    if (!manOptions) {
        errors.push(' man')
    }
    
    womanOptions = optionsByRole['woman']
    if (!womanOptions) {
        errors.push(' woman')
    } 
    
    bearOptions = optionsByRole['bear']
    if (!bearOptions) {
        errors.push(' bad news bear')
    } 
    if (errors.length > 0) {
        errors = 'Team ' + teamName + ' is missing these roles: ' + errors.join(',') + '.'
        return errors
    } else {
        return null
    }
}        