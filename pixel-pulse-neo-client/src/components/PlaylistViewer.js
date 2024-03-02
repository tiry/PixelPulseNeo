import React, { useEffect, useState, Fragment } from 'react';
import ApiService from '../services/ApiService';
import { List, ListItem, TextField, IconButton, Button, ListItemText, InputLabel, Select, MenuItem, Typography, Grid } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';

function PlaylistViewer() {
    const [playlists, setPlaylists] = useState(["default"]);
    const [selectedPlaylist, setselectPlaylist] = useState("default");
    const [schedule, setSchedule] = useState({ commands :[], conditions:[]});
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

    const handleSelectedCondition = (index, value) => {
        console.log(index, value);
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        newSchedule.conditions[index]=value
        setSchedule(newSchedule);       
    }
    const handleAdd = () => {
        const newItem = {
            id: `new-item-${Date.now()}`, 
            command_name: 'new_command',
            duration: '10' 
        };
    
        schedule.commands.push(newItem)
        setSchedule(schedule);
        setEditMode(true);
    };

    const handleDelete = (index) => {
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        newSchedule.commands.splice(index, 1)
        setSchedule(newSchedule);
    };

    const moveItem = (index, direction) => {
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        const item = newSchedule.commands.splice(index, 1)[0]; // Remove the item from the array
        newSchedule.commands.splice(index + direction, 0, item); // Add it back in the new position
        setSchedule(newSchedule);
    };

    const handleCommandNameChange = (index, newValue) => {
        const updatedSchedule = { "commands": [], "conditions": schedule.conditions}
        updatedSchedule.commands = schedule.commands.map((item, idx) => {
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
        const updatedSchedule = { "commands": [], "conditions": schedule.conditions}
        updatedSchedule.commands = schedule.commands.map((item, idx) => {
            if (idx === index) {
                return { id: item.id, command_name: item.command_name , duration: newValue };
            }
            return item;
        });
        setSchedule(updatedSchedule);
    };

    const handleSave = () => {
        ApiService.setSchedule(schedule, selectedPlaylist)
        .then(response => {
            // Handle the successful response here
            console.log('Schedule updated successfully:', response);
            setEditMode(false);
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
        <div style={{padding: 10}}>
            <Grid container spacing={2}>
                <Grid item xs={12}>    
                    <Typography variant="h4" component="h4"> Edit Playlist: </Typography>
                </Grid>
                <Grid item xs={3} md={2} lg={2}>    
                    <InputLabel id="combo-box-label">Select Playlist: </InputLabel>
                </Grid>
                <Grid item xs={9} md={9} lg={6}>         
                    <Select
                        labelId="combo-box-label"
                        id="combo-box"
                        value={selectedPlaylist}
                        label="Item"
                        onChange={handleSelectedPlaylist}
                        fullWidth
                    >
                        {playlists.map((item, index) => (
                            <MenuItem key={index} value={item}>
                                {item}
                            </MenuItem>
                        ))}
                    </Select>
                    </Grid>

                    <Grid item xs={12}>    
                        <Typography variant="h5" component="h5"> Commands: </Typography>
                    </Grid>
            
                {schedule.commands.map((item, index) => (
                    <Fragment>
                    <Grid item xs={4}>
                        {editMode ? (
                            <TextField
                                label="Command Name"
                                defaultValue={item.command_name}
                                onChange={(e) => handleCommandNameChange(index, e.target.value)}
                            />
                        ) : (
                            <ListItemText primary={item.command_name} />
                        )}
                    </Grid>
                    <Grid item xs={4}>
                        {editMode ? (
                            <TextField
                                label="Duration"
                                defaultValue={item.duration}
                                onChange={(e) => handleDurationChange(index, e.target.value)}
                            />
                        ) : (
                            <ListItemText secondary={`Duration: ${item.duration} seconds`} />
                        )}
                    </Grid>
                    <Grid item xs={4}>
                
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
                    </Grid>
                    </Fragment>
                ))}
            
                <Grid item xs={12}>
                <Button 
                    variant="contained" 
                    startIcon={<AddCircleOutlineIcon />}
                    onClick={handleAdd}
                >
                    Add Command
                </Button>
                </Grid>
                <Grid item xs={12}>    
                    <Typography variant="h5" component="h5"> Conditions: </Typography>
                </Grid>
           
                {schedule.conditions.map((condition, index) => (
                    <Fragment>
                    <Grid item xs={3} md={2} lg={2}>    
                    <InputLabel id="combo-box-label">Condition: </InputLabel>
                    </Grid>
                    <Grid item xs={6} md={6} lg={6}>
                    {editMode ? (
                            
                        <Select
                            value={condition}
                            label="Item"
                            onChange={(e) => handleSelectedCondition(index, e.target.value)}
                            fullWidth   
                            >
                                <MenuItem value={""}>No Condition</MenuItem>
                                <MenuItem value={"morning"}>Morning</MenuItem>
                                <MenuItem value={"night"}>Night</MenuItem>
                                <MenuItem value={"evening"}>Evening</MenuItem>
                                <MenuItem value={"week"}>Week</MenuItem>
                                <MenuItem value={"weekend"}>Weekend</MenuItem>
                            </Select>
                         ) : (
                            <Typography> {condition}</Typography>
                        )}
                    </Grid>
                    </Fragment>
                   
                ))}
            
                <Grid item xs={12}>    
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
                </Grid>
            </Grid>
        </div>
    );
}

export default PlaylistViewer;