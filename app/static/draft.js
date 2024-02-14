document.addEventListener('DOMContentLoaded', function () {

    var socket = io.connect();

    // Update data in case the user refreshed but we still have cached data
    socket.on('connect', function (episode) {
        socket.emit('get_cached_data', episode)
    });

    // ================ Starting Draft ================ //
    // Defining button
    var startDraftButton = document.getElementById('startDraftButton');
    startDraftButton.addEventListener('click', startDraft);

    // Sending start event to server
    function startDraft() {
        socket.emit('start_draft')
    }

    // Defining how we update the draft order
    var draftOrderDisplay = document.getElementById('draftOrder');
    function updateDraftOrder(draftOrder) {
        draftOrderDisplay.textContent = 'Draft Order: ' + draftOrder.join(' > ');
        var teamsTable = document.getElementById('teamsTable');
        cells = teamsTable.getElementsByTagName('td');

        // Iterate through the draftOrder and adjust the contents of the table cells
        for (var i = 0; i < draftOrder.length; i++) {
        
            var owner = draftOrder[i];
            var cell  = cells[i];
            listbox = document.getElementById(owner);
            // cell.getElementsByClassName('teamList')[0].id = owner;
            cell.querySelector('h3').textContent = owner;
            cell.appendChild(listbox)
        }
    }

    // Defining how we update the turn indicator
    var turnIndicator = document.getElementById('turnIndicator');     
    function updateTurnIndicator(currentRound, currentOwner) {
        turnIndicator.textContent = 'Round ' + currentRound + '!\n' + currentOwner
    }

    // Update the UI with the latest data
    socket.on('update_turn_data', function (data) {
        currentRound = data.current_round;
        draftOrder   = data.draft_order;
        owner        = data.owner;
        updateDraftOrder(draftOrder);
        updateTurnIndicator(currentRound, owner);        
    });

    
    // ================ Drafting Castmembers ================ //
    // Event delegation for clicking and drafting a each castmember.
    // Clicking a cast member validates the selection. Then either drafts or shows an error
    var castmemberContainer = document.getElementById('castmemberContainer');
    castmemberContainer.addEventListener('click', processDraftSelection);
    function processDraftSelection (event) {
        
        if (event.target.classList.contains('castmember')) {
            castmember   = event.target.textContent;
            role         = event.target.dataset.role;
            socket.emit('validate_then_draft_castmember', {
                castmember    : castmember,
                role          : role,
            });
        }
    };

    // ====== Responses to validation ====== //    
    // If invalid draft, show error message
    socket.on('invalid_draft', function(data) {
        showErrorMessage('Error! Trying to draft ' + data.castmember + ' for ' + data.role + ' but already have ' + data.other_castmember + ' in that role.')
    });

    // ====== Updating team data and displays with after drating a castmember ====== //
    socket.on('update_draft_data', function(data) {
        
        // Add new team member to their owner's list in the UI
        var draftedCastmemberName   = data.drafted_castmember;
        var draftedCastmemberOption = document.getElementById(draftedCastmemberName + "-" + data.role)
        var teamOwner               = data.owner;
        var role                    = data.role;
        var teamList                = document.getElementById(teamOwner);
        
        // Make a new option to add to the team list
        var newOption = document.createElement('option');
            newOption.value = draftedCastmemberName;
            newOption.text  = draftedCastmemberName + '-' + role;
            newOption.id    = draftedCastmemberName + role + 'added';
            newOption.dataset.role = role;
        teamList.add(newOption);

        // Hide the castmember from being displayed in the list of available castmembers to draft
        draftedCastmemberOption.style.display = 'none';
        // Once a team member gets drafted, the user can undo
        undoButton.disabled = false;
    });


    
    
    // ================ Undoing a draft selection ================ //
    // ====== Tell the server to undo the last draft selection ====== //    
    var undoButton = document.getElementById('undoButton');
    undoButton.addEventListener('click', function() {
        socket.emit('undo_last_draft_selection')
    });
    // ====== Update the UI with the un-done selection ====== //    
    socket.on('draft_data_reversed', function (data) {
        var teamList = document.getElementById(data.owner);
        var castmemberOptionToUnhide = document.getElementById(data.option_to_unhide_id);
        var castmemberOptionToRemove = document.getElementById(data.option_to_remove_id);
        
        castmemberOptionToUnhide.style.display = 'block'; // Re-add the castmember to the container
        castmemberOptionToRemove.remove();
        
        updateTurnIndicator(data.current_round, data.current_owner)
        updateDraftOrder   (data.draft_order)
    })
    
    socket.on('disable_undo', function() {
        undoButton.disabled = true
    })

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

    socket.on('end_draft', function () {
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
    })
    
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
            var ownerName = teamLists[i].getAttribute('id');
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

    socket.on('reset_draft', function resetDraft(data) {
        
        var confirmReset = confirm("Are you sure you want to reset?");
        if (!confirmReset) {
            return;
        } else {
            socket.emit('reset_confirmed')
            // Iterate over each team's list
            var teamLists = document.querySelectorAll('.teamList');
            teamLists.forEach(function(teamList) {
                // Remove all options from the team's list
                while (teamList.firstChild) {
                    teamList.removeChild(teamList.firstChild);
                }
            });
        
            // Show all hidden castmembers
            var hiddenCastmembers = document.querySelectorAll('.castmember[style="display: none;"]');
            hiddenCastmembers.forEach(function(castmember) {
                castmember.style.display = 'block';
            });
            startDraft();
        }
    });

    function populateTeams() {  
        
        selectedEpisode = episode;
    
        // Fetch teams data for the selected episode from the backend
        fetch('/get_teams?episode=' + selectedEpisode)
            .then(response => response.json())
            .then(data => {
                if (data.teams) {
                // Update team lists with the fetched data
                data.teams.forEach(team => {
                    var teamList = document.getElementById(team.name);
                    teamList.innerHTML = '';  // Clear existing options
    
                    for (const [role, castmember] of Object.entries(team.castmembers)) {
                        var option   = document.createElement('option');
                        option.text  = castmember + ' ' + role;
                        option.value = castmember;
                        option.id    = castmember + role + 'added';
                        option.dataset.role = role; // Store the role in dataset
                        teamList.add(option);
    
                        // Remove the castmember from the corresponding old list
                        var oldList = document.getElementById(role);
                        var castmemberOption = document.getElementById(castmember + "-" + role);
                        castmemberOption.style.display = 'none'; // Re-add the castmember to the container
                    }
                })
                showErrorMessage('Teams already drafted!');
            }})
            .catch((error) => {
                console.error('Error:', error);
            });
    };

    populateTeams();
    
})