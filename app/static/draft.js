document.addEventListener('DOMContentLoaded', function () {
    
    draftStarted = false;

    var socket = io.connect();

    // Update data in case the user refreshed but we still have cached data
    socket.on('connect', function () {
        socket.emit('get_cached_data', episode)
    });

    socket.on('episode_conflict', function (data) {
        var confirmReset = confirm("There is already a draft session happening for episode " + 
                                    data.cached_episode + '. You are trying to draft for episode ' + data.episode + '.' +
                                    ' Do you want to stop the current draft? Cancel to redirect to current draft.')
        if (confirmReset) {
            socket.emit('reset_confirmed')
        } else {
            window.location.href = "/draft/" + data.cached_episode;
        }
    });

    // ================ Starting Draft ================ //
    // Defining button
    var startDraftButton = document.getElementById('startDraftButton');
    startDraftButton.addEventListener('click', startDraft);

    // Sending start event to server
    function startDraft() {
        socket.emit('start_draft');
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

    // Only make these events if the start has been started
    var castmemberContainer = document.getElementById('castmemberContainer');
    document.querySelectorAll('.castmember img').forEach(img => {
        img.addEventListener('click', processDraftSelection);
    });

    function processDraftSelection(event) {
        if (event.target.classList.contains('castmember')) {
            var castmember = event.target.alt;
            var role = event.target.dataset.role;
            var instance = event.target.dataset.instance;
            // NOTE: As of 2/16/2024 all validations are going through as 
            // we are deciding what the team compositions should be. Plus, we
            // can always undo if someone drafts incorrectly
            socket.emit('validate_then_draft_castmember', {
                castmember: castmember,
                role: role,
                instance: instance,
                image_id: event.target.id
            });
        }
    }

    // ====== Responses to validation ====== //    
    // If invalid draft, show error message
    socket.on('invalid_draft', function(data) {
        showErrorMessage('Error! Trying to draft ' + data.castmember + ' for ' + data.role + ' but already have ' + data.other_castmember + ' in that role.')
    });

    // ====== Updating team data and displays with after drafting a castmember ====== //
    socket.on('update_draft_data', function(data) {
        
        // Add new team member to their owner's list in the UI
        var teamOwner               = data.owner;
        var teamList                = document.getElementById(teamOwner);
        var role                    = data.role;
        var image_id                = data.image_id;
        var draftedCastmemberName   = data.drafted_castmember;

        // If we didn't get here by clicking an image (e.g., if we got here by populating a previously drafted team,
        // then we can figure out the image_id by starting with 1 and then incrementing if that image
        // has already been hidden
    
        if (image_id == undefined) {
            var draftedCastmemberInstance = 3;
            do {
                draftedCastmemberInstance--
                image_id = draftedCastmemberName + '-' + role + draftedCastmemberInstance
                var draftedCastmemberImage = document.getElementById(image_id);
                console.log(draftedCastmemberInstance)
                } while (draftedCastmemberImage .style.display == 'none' && draftedCastmemberInstance > 0)
        } else {
            var draftedCastmemberInstance = image_id.slice(-1);
        var draftedCastmemberImage = document.getElementById(image_id);

        }

        // Make a new option to add to the team list
        var newOption = document.createElement('option');
            newOption.value = draftedCastmemberName;
            newOption.text  = draftedCastmemberName;
            newOption.id    = image_id + 'list_option';
            newOption.dataset.role = role;
            if (role == "man") {
                newOption.style.backgroundColor = 'rgb(93, 212, 99)'
            } else if (role == "woman") {
                newOption.style.backgroundColor = 'rgb(236, 236, 192)'
            } else if (role == "bear") {
                newOption.style.backgroundColor = 'crimson'
            }
        teamList.add(newOption);

        // Hide the castmember from being displayed in the list of available castmembers to draft
        draftedCastmemberImage.style.display = 'none';
        draftedCastmemberContainer = draftedCastmemberImage.parentElement
        draftedCastmemberContainer.style.display = 'none';

        // If this was the last instance, 
        if (draftedCastmemberInstance == 1) {
            draftedCastmemberContainer.parentElement.style.display = 'none';
        }
        
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
        
        var draftedCastmemberContainer = castmemberOptionToUnhide.parentElement;
        var draftedCastmemberGroupContainer = draftedCastmemberContainer.parentElement;
    
        draftedCastmemberContainer.style.display = 'block';
        draftedCastmemberGroupContainer.style.display = 'block';

        // Show the castmember option
        castmemberOptionToUnhide.style.display = 'flex';
        castmemberOptionToUnhide.classList.add('castmember')
    
        // Show the castmember's container if it's hidden
        draftedCastmemberContainer.style.display = 'flex';
    
    
        // Remove the castmember option from the team list
        castmemberOptionToRemove.remove();
    });
    
    socket.on('disable_undo', function() {
        undoButton.disabled = true
    })

    // Since we don't how many rounds there will be, turn this off
    // and keep the save button enabled by default
    // ================ Ending the draft ================ //
    // socket.on('end_draft', function () {
    //     // Shows draft completed message
    //     // Creates save button if it doesn't exist
    //     var saveButton = document.getElementById('saveButton')
    //     if (saveButton == undefined) {
    //         document.createElement('button');
    //         saveButton.textContent = 'Save';
    //         saveButton.id = 'saveButton';
    //         document.getElementById('startDraftDiv').appendChild(saveButton);
    
    //     // Add an event listener to the "Save" button
    //     saveButton.addEventListener('click', function () {
    //         saveTeamLists();
    //     });
    //     }
    // })
    saveButton.addEventListener('click', function () {
        saveTeamLists();
    });

    
    // ================ Resetting the draft ================ //
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
                                var castmemberDiv = document.getElementById(castmember + '-' + role)

                                // In the family drafts, we have doubles of each role which are differentiated by 
                                // having a 1 or a 2 appended to their names. If there's no non-instanced icon
                                // for that castmember, then try to find instance 1
                                if (castmemberDiv == undefined) {
                                    var castmemberDiv = document.getElementById(castmember + '-' + role + '1')
                                }
                                if (castmemberDiv.hidden == true) {
                                    var castmemberDiv = document.getElementById(castmember + '-' + role + '2')
                                }
                                castmemberDiv.hidden = true
                            }
                        }
                        showErrorMessage('Teams already drafted!');
                        startDraftButton.disabled = true
                    })
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    };

    populateTeams();
    
})