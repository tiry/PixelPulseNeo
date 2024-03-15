import React, { useEffect, useState, Fragment } from 'react';
import ApiService from '../services/ApiService';
import { Chip, IconButton, Button, ListItemText, InputLabel, Select, MenuItem, Typography, Grid,Card,CardHeader,CardContent, CardActions } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ModeEditIcon from '@mui/icons-material/ModeEdit';
import BackspaceIcon from '@mui/icons-material/Backspace';
import ListIcon from '@mui/icons-material/List';

function PlaylistViewer() {
    //const [playlists, setPlaylists] = useState(["default"]);
    const [playlistsDetailed, setPlaylistsDetailed] = useState([]);
    
    const [selectedPlaylist, setselectPlaylist] = useState("default");
    const [schedule, setSchedule] = useState({ commands :[], conditions:[]});
    const [commands, setCommands] = useState([]);
    const [needSave, setNeedSave] = useState(false);
    const [editMode, setEditMode] = useState(false);
    
    useEffect(() => {
        ApiService.getPlaylistsDetailed().then(setPlaylistsDetailed)
    }, []);

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
        ApiService.getCommands().then(commands => {
        setCommands(commands); })
    }, []);

    //useEffect(() => {
    //    ApiService.getPlaylists().then(setPlaylists);
    //}, []);

    //const handleSelectedPlaylist = (event) => {
        //console.log(event.target.value)
    //    setselectPlaylist(event.target.value)
    //}

    const handleSelectedCondition = (index, value) => {
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        newSchedule.conditions[index]=value
        setSchedule(newSchedule);       
    }
    const handleAdd = () => {
        const newItem = {
            id: `new-item-${Date.now()}`, 
            command_name: 'mta',
            duration: '10' 
        };
    
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        newSchedule.commands.push(newItem)        
        setSchedule(newSchedule);
        setNeedSave(true);
    };

    const handleAddCondition = () => {
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        newSchedule.conditions.push("")
        setSchedule(schedule);
        setNeedSave(true);
    };

    const handleDelete = (index) => {
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        newSchedule.commands.splice(index, 1)
        setSchedule(newSchedule);
        setNeedSave(true);
    };

    const handleExecute = (playlist) => {
        ApiService.playPlaylist(playlist);
    }

    const handleEditPlaylist = (playlist) => {
        setselectPlaylist(playlist);
        setEditMode(true)
    }

    const moveItem = (index, direction) => {
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        const item = newSchedule.commands.splice(index, 1)[0]; // Remove the item from the array
        newSchedule.commands.splice(index + direction, 0, item); // Add it back in the new position
        setSchedule(newSchedule);
        setNeedSave(true);
    };

    const handleCommandNameChange = (index, newValue) => {
        const updatedSchedule = { "commands": [], "conditions": schedule.conditions}
        updatedSchedule.commands = schedule.commands.map((item, idx) => {
            if (idx === index) {
                return { id: item.id, duration: item.duration, command_name: newValue };
            }
            return item;
        });
        setSchedule(updatedSchedule);
        setNeedSave(true);
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
        setNeedSave(true);


    };

    const handleSave = () => {
        ApiService.setSchedule(schedule, selectedPlaylist)
        .then(response => {
            // Handle the successful response here
            console.log('Schedule updated successfully:', response);
            setNeedSave(false);
            // Optionally, you can update the local state with the response if needed
            //setSchedule(response);
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

            {editMode ? 
                (
                    <>
                <Grid item xs={12}>    
                    <Typography variant="h6" component="h6"> Edit playlist {selectedPlaylist} </Typography>
                </Grid>
                
                <Grid item xs={12}>    
                    <Typography variant="h6" component="h6"> Commands: </Typography>
                </Grid>
        
                {schedule.commands.map((item, index) => (
                    <Fragment>
                    <Grid item xs={4}>
                            <>
                            <ListItemText secondary={`Command:`} />

                            <Select
                            labelId="combo-box-label"
                            id="combo-box"
                            value={item.command_name}
                            label="Item"
                            onChange={(e) => handleCommandNameChange(index, e.target.value)}
                            fullWidth
                            size="small"
                        >
                            {commands.map((item, index) => (
                                <MenuItem key={index} value={item.name}>
                                    {item.name}
                                </MenuItem>
                            ))}
                            </Select>
                        </>
    
                    </Grid>
                    <Grid item xs={4}>
                            <>
                            <ListItemText secondary={`Duration:`} />
                            <Select
                                    value={item.duration}
                                    label="Duration"
                                    onChange={(e) => handleDurationChange(index, e.target.value)}
                                    displayEmpty
                                    fullWidth
                                    size="small"
                                    >
                                    <MenuItem value={5}>5s</MenuItem>
                                    <MenuItem value={10}>10s</MenuItem>
                                    <MenuItem value={15}>15s</MenuItem>
                                    <MenuItem value={20}>20s</MenuItem>
                                    <MenuItem value={30}>30s</MenuItem>
                                    <MenuItem value={40}>40s</MenuItem>
                                    <MenuItem value={60}>1 min</MenuItem>
                                    <MenuItem value={120}>2 min</MenuItem>
                                    <MenuItem value={300}>5 min</MenuItem>
                                    <MenuItem value={900}>15 min</MenuItem>
                                    <MenuItem value={1800}>30 min</MenuItem>
                            </Select>
                            </>
                    </Grid>
                    <Grid item xs={4}>
                    <ListItemText secondary={`Actions:`} />
                                <IconButton onClick={() => handleDelete(index)} size="small">
                                    <DeleteIcon />
                                </IconButton>
                                <IconButton onClick={() => moveItem(index, -1)} disabled={index === 0} size="small">
                                    <ArrowUpwardIcon />
                                </IconButton>
                                <IconButton onClick={() => moveItem(index, 1)} disabled={index === schedule.length - 1} size="small">
                                    <ArrowDownwardIcon />
                                </IconButton>
                    </Grid>
                    </Fragment>
                ))}
            
                <Grid item xs={12}>
                <Button 
                    variant="contained" 
                    startIcon={<AddCircleOutlineIcon />}
                    onClick={handleAdd}
                    sx={{margin:"2px"}}
                >
                    Add Command
                </Button>
                </Grid>
                <Grid item xs={12}>    
                    <Typography variant="h6" component="h6"> Conditions: </Typography>
                    <Button 
                    variant="contained" 
                    startIcon={<AddCircleOutlineIcon />}
                    onClick={handleAddCondition}
                >
                    Add Condition
                </Button>
                </Grid>
           
                {schedule.conditions.map((condition, index) => (
                    <Fragment>
                    <Grid item xs={3} md={2} lg={2}>    
                    <InputLabel id="combo-box-label">Condition: </InputLabel>
                    </Grid>
                    <Grid item xs={6} md={6} lg={6}>
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
                    </Grid>
                    </Fragment>
                   
                ))}
            
                <Grid item xs={12}>    
                    <Button 
                        variant="contained" 
                        color="secondary" 
                        disabled={!needSave}
                        onClick={handleSave}
                        sx={{margin:"2px"}} 
               >
                        Save Changes
                    </Button>
                    <Button 
                    variant="contained" 
                    startIcon={<BackspaceIcon />}
                    onClick={() => setEditMode(false)}
                    sx={{margin:"2px"}}
                >
                    Cancel
                </Button>
               
                </Grid>
            </>
            ) : (<>
            
            {playlistsDetailed.map((playlist, index) => (
                <Grid item xs={12} md={6} lg={4}>
                
                 <Card fullWidth>
                    <CardHeader avatar={<ListIcon></ListIcon>} 
                        title={playlist.name}
                       >
                    </CardHeader>
                    <CardContent>
                    {playlist.commands.map((command, index) => (
                          <Chip label={command}
                          size="medium" variant="outlined"  sx={{margin: "1px"}} />) )
                    }

                    </CardContent>   
                    <CardActions>
                    
                        <Button variant="contained" color="primary" startIcon={<PlayArrowIcon />}
                                onClick={() => handleExecute(playlist.name)}>         
                        </Button>

                        <Button variant="contained" color="primary" startIcon={<ModeEditIcon />}
                                onClick={() => handleEditPlaylist(playlist.name)}>            
                        </Button>

                    </CardActions>
                </Card>
                                    
                </Grid>            
                        ))}
                    
            
            </>)}

            </Grid>
        </div>
    );
}

export default PlaylistViewer;