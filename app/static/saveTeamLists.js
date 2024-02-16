function saveTeamLists() {
        var teamLists = document.getElementsByClassName('teamList');
        var teamsData = {};
        var errors = [];

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
        if (errors.length > 0) {
            var errorMessage = errors.join("\r\n"); // Concatenate errors into one string
            showErrorMessage(errorMessage);
            return
        };

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
            });
    }