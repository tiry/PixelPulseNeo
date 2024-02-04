import React, { useEffect, useState } from 'react';
import ApiService from '../services/ApiService';
import { List, ListItem, TextField, IconButton, Button, ListItemText, InputLabel, Select, MenuItem } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';

function PlaylistViewer() {
    const [playlists, setPlaylists] = useState(["default"]);
    const [selectedPlaylist, setselectPlaylist] = useState("default");
    const [schedule, setSchedule] = useState({ commands :[]});
    const [editMode, setEditMode] = useState(false);
    
    useEffect(() => {
        ApiService.getPlaylist(selectedPlaylist).then(data => {
            var commands = data.commands
            // Assign a unique ID to each item (if they don't already have one)
            const commandWithIds = commands.map((item, index) => ({
                ...item,
                id: item.id || `schedule-item-${index}` // Assuming 'id' is the unique identifier
            }));
            var scheduleWithIds = {}
            scheduleWithIds.commands = commandWithIds
            scheduleWithIds.conditions = data.conditions 
            setSchedule(scheduleWithIds);
        });
    }, [selectedPlaylist]);

    useEffect(() => {
        ApiService.getPlaylists().then(setPlaylists);
    }, []);


    const handleSelectedPlaylist = (event) => {
        //console.log(event.target.value)
        setselectPlaylist(event.target.value)
    }

    const handleAdd = () => {
        const newItem = {
            id: `new-item-${Date.now()}`, 
            command_name: 'new_command',
            duration: '10' // Assuming the field is 'duration' and not 'schedule'
        };
    
        schedule.commands.push(newItem)
        // Create a new array with the old items plus the new item
        setSchedule(schedule);
        setEditMode(true);
    };

    const handleDelete = (index) => {
        const newSchedule = [...schedule];
        newSchedule.splice(index, 1);
        setSchedule(newSchedule);
    };

    const moveItem = (index, direction) => {
        const newSchedule = [...schedule];
        const item = newSchedule.splice(index, 1)[0]; // Remove the item from the array
        newSchedule.splice(index + direction, 0, item); // Add it back in the new position
        setSchedule(newSchedule);
    };

    const handleCommandNameChange = (index, newValue) => {
        const updatedSchedule = schedule.map((item, idx) => {
            if (idx === index) {
                return { id: item.id, duration: item.duration, command_name: newValue };
            }
            return item;
        });
        console.log("updated command name")
        console.log(updatedSchedule)
        setSchedule(updatedSchedule);
    };

    const handleDurationChange = (index, newValue) => {
        const updatedSchedule = schedule.map((item, idx) => {
            if (idx === index) {
                return { id: item.id, command_name: item.command_name , duration: newValue };
            }
            return item;
        });
        setSchedule(updatedSchedule);
    };

    const handleSave = () => {
        ApiService.setSchedule(schedule)
        .then(response => {
            // Handle the successful response here
            console.log('Schedule updated successfully:', response);
            // Optionally, you can update the local state with the response if needed
            // setSchedule(response);
        })
        .catch(error => {
            // Handle any errors here
            console.error('Error updating schedule:', error);
            // Show an error message to the user if you have a UI component for that
        });
    };

    return (
        <div>
            <InputLabel id="combo-box-label">Select Playlist: </InputLabel>
            <Select
                labelId="combo-box-label"
                id="combo-box"
                value={selectedPlaylist}
                label="Item"
                onChange={handleSelectedPlaylist}
            >
                {playlists.map((item, index) => (
                    <MenuItem key={index} value={item}>
                        {item}
                    </MenuItem>
                ))}
            </Select>
            <List>
                {schedule.commands.map((item, index) => (
                    <ListItem key={item.id}>
                        {editMode ? (
                            <TextField
                                label="Command Name"
                                defaultValue={item.command_name}
                                onChange={(e) => handleCommandNameChange(index, e.target.value)}
                            />
                        ) : (
                            <ListItemText primary={item.command_name} />
                        )}
                        {editMode ? (
                            <TextField
                                label="Duration"
                                defaultValue={item.duration}
                                onChange={(e) => handleDurationChange(index, e.target.value)}
                            />
                        ) : (
                            <ListItemText secondary={`Interval: ${item.duration} seconds`} />
                        )}
                        {editMode && (
                                                     <>
                                <IconButton onClick={() => handleDelete(index)}>
                                    <DeleteIcon />
                                </IconButton>
                                <IconButton onClick={() => moveItem(index, -1)} disabled={index === 0}>
                                    <ArrowUpwardIcon />
                                </IconButton>
                                <IconButton onClick={() => moveItem(index, 1)} disabled={index === schedule.length - 1}>
                                    <ArrowDownwardIcon />
                                </IconButton>
                            </>
                            
                        )}
                    </ListItem>
                ))}
            </List>
            <Button 
                variant="contained" 
                startIcon={<AddCircleOutlineIcon />}
                onClick={handleAdd}
            >
                Add Item
            </Button>
            <Button 
                variant="contained" 
                color="primary" 
                onClick={() => setEditMode(!editMode)}
            >
                {editMode ? 'Stop Editing' : 'Edit'}
            </Button>
            <Button 
                variant="contained" 
                color="secondary" 
                onClick={handleSave}
            >
                Save Changes
            </Button>
        </div>
    );
}

export default PlaylistViewer;
