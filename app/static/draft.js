document.addEventListener('DOMContentLoaded', function () {
    var teams = {}
    draftOrder = []
    var currentIndex = 0
    var turnIndicator = document.getElementById('turnIndicator');    
    rounds = 0

    function startDraft() {
        rounds += 1
        // Randomize player order and display the draft order
        // Update turn indicator to indicate whose turn it is
        // Make an AJAX request to fetch players data
        fetch('/get_players')
        .then(response => response.json())
        .then(data => {
            // Process the data returned from the server
            var player_names = data.players;
            player_names.forEach(function(player) {
                teams[player] = {
                    'man': null,
                    'woman': null,
                    'bear': null,
                };
            });
            draftOrder = shuffle(player_names);  // Do something with the players data

            var draftOrderDisplay = document.getElementById('draftOrder');
            draftOrderDisplay.textContent = 'Draft Order: ' + draftOrder.join(' > ');
            updateTurnIndicator(rounds, draftOrder[currentIndex])
        })
        .catch(error => {
            console.error('Error fetching players:', error);
        });

    }

    // Function to shuffle an array (Fisher-Yates algorithm)
    function shuffle(array) {
        for (var i = array.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }
    
    function draftTeamMember(newTeamMemberObject) {
        // Add selected participant to the current team
        // Remove that participant from being displayed
        // Go to next person in draft
        participantName = newTeamMemberObject.textContent
        role = newTeamMemberObject.dataset.role

        var currentPlayer = draftOrder[currentIndex];
        var teamData = [];
    
        // Validate each team
        if (teams[currentPlayer][role] !== null) {
            var otherRoleName = teams[currentPlayer][role];
            showErrorMessage('Error! Trying to draft ' + participantName + ' but already have ' + otherRoleName + ' for role ' + role);
            return;
        };

        // Add participant to team dictionary
        teams[currentPlayer][role] = participantName;

        // Increment current index. If at the end of the list, reverse the list
        // and start over (snake draft)
        currentIndex += 1;
        if (currentIndex === Object.keys(teams).length) {
            draftOrder.reverse();
            currentIndex = 0;
            rounds += 1;
        }
        
        newTeamMemberObject.style.display = 'none';
    
        // Add new team member to their player's list
        var teamList = document.querySelector('.teamList[data-team="' + currentPlayer + '"]');
        var newOption = document.createElement('option');
        newOption.value = participantName;
        newOption.text = participantName + ' ' + role;
        newOption.dataset.role = role;
        teamList.add(newOption);

        if (rounds > 3) {
            endDraft()
        } else {
            updateTurnIndicator(rounds, draftOrder[currentIndex])
        }
    };

    // Function to handle  ing the last selection
    function undoSelection() {
        // Undo the last player selection
        // Update team display
        // Update turn indicator
    }

    // Event listener for the "Start Draft" button
    var startDraftButton = document.getElementById('startDraftButton');
    startDraftButton.addEventListener('click', startDraft);

    // Event delegation for team member selection
    var participantContainer = document.getElementById('participantContainer');
    participantContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('participant')) {
            draftTeamMember(event.target);
        }
    });

    // Event listener for the "Undo" button
    var undoButton = document.getElementById('undoButton');
    undoButton.addEventListener('click', undoSelection);

    // Function to show an error message
    function showErrorMessage(message) {
        // Display the error message (you can customize this part)
        var errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';

        // Hide the message after a few seconds (you can adjust the timeout)
        setTimeout(function () {
            errorDiv.style.display = 'none';
        }, 8000); // Hide after 3 seconds
    }

    function updateTurnIndicator(roundNumber, currentPlayerName) {
        turnIndicator.textContent = 'Round ' + roundNumber + '!\n' + currentPlayerName
    }

    function endDraft () {
        // Shows draft completed message
        // Creates save button
        var saveButton = document.createElement('button');
        saveButton.textContent = 'Save';
        saveButton.id = 'saveButton';
        document.getElementById('startDraftDiv').appendChild(saveButton);
       
        // Add an event listener to the "Save" button
        saveButton.addEventListener('click', function () {
            saveTeamLists();
        });
    }

    
    function showConfirmationMessage(message) {
        // Display the confirmation message (you can customize this part)
        var confirmationDiv = document.getElementById('confirmationMessage');
        confirmationDiv.textContent = message;
        confirmationDiv.style.display = 'block';
    
        // Hide the message after a few seconds (you can adjust the timeout)
        setTimeout(function () {
            confirmationDiv.style.display = 'none';
        }, 3000); // Hide after 3 seconds
    };

    function saveTeamLists() {
        var teamLists = document.getElementsByClassName('teamList');
        var teamsData = [];
        var errors = [];

        for (var i = 0; i < teamLists.length; i++) {
            var ownerName = teamLists[i].getAttribute('data-team');
            var newTeamData = { 'name' : ownerName };
        
            Array.from(teamLists[i].options).forEach(option => {
                var role = option.dataset.role;
                var value = option.value;
                newTeamData[role] = value;
            });
        
            teamsData.push(newTeamData);
        }

        // Include the "episode" variable in the JSON data
        var requestData = {
            episode: episode,
            teams: teamsData
        };

        // Send the data to the backend using AJAX
        fetch('/save_drafted_team', {
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
    
})