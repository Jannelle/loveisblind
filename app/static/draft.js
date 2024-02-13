document.addEventListener('DOMContentLoaded', function () {

    var socket = io.connect();
    
    var teams = {}
    draftOrder = []
    var currentIndex = 0
    var turnIndicator = document.getElementById('turnIndicator');    
    rounds = 0
    var draftOrderDisplay = document.getElementById('draftOrder');
    var undoButton = document.getElementById('undoButton');
    
    function startDraft() {
        if (rounds !== 0) {
            resetDraft()
            return;
        }
        
        rounds++

        // Randomize owner order and display the draft order
        // Update turn indicator to indicate whose turn it is
        // Make an AJAX request to fetch owners data
        fetch('/get_owners')
        .then(response => response.json())
        .then(data => {
            // Process the data returned from the server
            var owner_names = data.owners;
            owner_names.forEach(function(owner) {
                teams[owner] = {
                    'man': null,
                    'woman': null,
                    'bear': null,
                };
            });
            draftOrder = shuffle(owner_names);  // Do something with the owners data
            draftOrderDisplay.textContent = 'Draft Order: ' + draftOrder.join(' > ');
            updateTurnIndicator(rounds, draftOrder[currentIndex])
        })
        .catch(error => {
            console.error('Error fetching owners:', error);
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

        // This prevents this function from running before StartDraft has been clicked
        if (rounds === 0) {
            return;
        }

        undoButton.disabled = false;

        // Add selected participant to the current team
        // Remove that participant from being displayed
        // Go to next person in draft
        participantName = newTeamMemberObject.textContent;
        role = newTeamMemberObject.dataset.role;
        newTeamMemberObject.style.display = 'none';

        var currentowner = draftOrder[currentIndex];
        var teamData = [];
    
        // Validate each team
        if (teams[currentowner][role] !== null) {
            var otherRoleName = teams[currentowner][role];
            showErrorMessage('Error! Trying to draft ' + participantName + ' but already have ' + otherRoleName + ' for role ' + role);
            return;
        };

        // Add participant to team dictionary
        teams[currentowner][role] = participantName;

        // Increment current index. If at the end of the list, reverse the list
        // and start over (snake draft)
        currentIndex++;
        if (currentIndex === Object.keys(teams).length) {
            draftOrder.reverse();
            draftOrderDisplay.textContent = 'Draft Order: ' + draftOrder.join(' > ');
            currentIndex = 0;
            rounds += 1;
        }

        // Add new team member to their owner's list
        var teamList = document.querySelector('.teamList[data-team="' + currentowner + '"]');
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
        if (rounds <= 0) {
            return;
        }

        // Decrease currentIndex
        currentIndex--;

        // If a new round was just started
        if (currentIndex < 0) {
            rounds--;
            draftOrder.reverse();
            draftOrderDisplay.textContent = 'Draft Order: ' + draftOrder.join(' > ');
            currentIndex = draftOrder.length - 1;
        }

        lastownerName = draftOrder[currentIndex]

        // Remove the last person they added
        var teamList = document.querySelector('.teamList[data-team="' + lastownerName + '"]');
        var lastTeamMember = teamList.lastElementChild;
        

        var participantContainer = document.getElementById('participantContainer');
        var participant = participantContainer.querySelector('.participant[data-name="' + lastTeamMember.value + '"][data-role="' + lastTeamMember.dataset.role + '"]');
        participant.style.display = 'block'; // Re-add the participant to the container
        
        teams[lastownerName][lastTeamMember.dataset.role] = null;
        lastTeamMember.remove();

        updateTurnIndicator(rounds, lastownerName)

        // If we've reached the beginning of the draft
        if (rounds === 1 && currentIndex === 0) {
            undoButton.disabled = true;
            rounds = 1;
            return;
        }
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

    function updateTurnIndicator(roundNumber, currentownerName) {
        turnIndicator.textContent = 'Round ' + roundNumber + '!\n' + currentownerName
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
        console.log(episode);
        // Include the "episode" variable in the JSON data
        var requestData = {
            episode: episode,
            teams: teamsData
        };
        console.log(requestData);

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

    function resetDraft() {
        // Iterate over each team's list
        var teamLists = document.querySelectorAll('.teamList');
        teamLists.forEach(function(teamList) {
            // Remove all options from the team's list
            while (teamList.firstChild) {
                teamList.removeChild(teamList.firstChild);
            }
        });
    
        // Show all hidden participants
        var hiddenParticipants = document.querySelectorAll('.participant[style="display: none;"]');
        hiddenParticipants.forEach(function(participant) {
            participant.style.display = 'block';
        });
    
        // Reset teams object
        for (var owner in teams) {
            teams[owner] = {
                'man': null,
                'woman': null,
                'bear': null,
            };
        }
    
        // Reset rounds, currentIndex, and draftOrder
        rounds = 0;
        currentIndex = 0;
        draftOrder = [];
    
        startDraft();
    }

    function populateTeams() {
        
        selectedEpisode = episode;
        
    
        // Fetch teams data for the selected episode from the backend
        fetch('/get_teams?episode=' + selectedEpisode)
            .then(response => response.json())
            .then(data => {
                // Update team lists with the fetched data
                data.teams.forEach(team => {
                    var teamList = document.querySelector('.teamList[data-team="' + team.name + '"]');
                    teamList.innerHTML = '';  // Clear existing options
    
                    for (const [role, participant] of Object.entries(team.participants)) {
                        var option = document.createElement('option');
                        option.text = participant + ' ' + role;
                        option.value = participant;
                        option.dataset.role = role; // Store the role in dataset
                        teamList.add(option);
    
                        // Remove the participant from the corresponding old list
                        var oldList = document.getElementById(role);
                        var participantContainer = document.getElementById('participantContainer');
                        var participantOption = participantContainer.querySelector('.participant[data-name="' + participant + '"][data-role="' + role + '"]');
                        participantOption.style.display = 'none'; // Re-add the participant to the container
                }
            });
                showErrorMessage('Teams already drafted!');
                // showConfirmationMessage('Teams copied successfully!');  
            })
            .catch((error) => {
                console.error('Error:', error);
                
            });
    };

    
    populateTeams();
})