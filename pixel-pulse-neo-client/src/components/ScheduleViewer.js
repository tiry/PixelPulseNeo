import React, { useEffect, useState } from 'react';
import ApiService from '../services/ApiService';
import {BASE_URL} from '../services/ApiService'
import { IconButton, Button, ListItemText, Typography, Grid, Select, MenuItem, CardMedia} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import SmartDisplayIcon from '@mui/icons-material/SmartDisplay';

function ScheduleViewer() {
    const [schedule, setSchedule] = useState({ commands :[]});
    const [currentCommand, setCurrentCommand] = useState({});
    const [currentCommandName, setCurrentCommandName ] = useState(null);
    const [commands, setCommands] = useState([]);
    const [needSave, setNeedSave] = useState(false);

    useEffect(() => {
        
        ApiService.getSchedule().then(data => {
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
    }, []);

    useEffect(() => {
        ApiService.getCurrentCommand().then(data => {
            setCurrentCommandName(data)
            setCurrentCommand({})
            //console.log("new  command name = '" + data + "'")
        })
    }, []);

    useEffect(() => {
        if (currentCommandName){
            ApiService.getCommand(currentCommandName).then(setCurrentCommand);
        }
    }, [currentCommandName]);

    useEffect(() => {
        ApiService.getCommands().then(commands => {
        setCommands(commands); })
    }, []);

    const handleAdd = () => {
        const newItem = {
            id: `new-item-${Date.now()}`, 
            command_name: 'new_command',
            duration: '10' // Assuming the field is 'duration' and not 'schedule'
        };
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        newSchedule.commands.push(newItem)
        // Create a new array with the old items plus the new item
        setSchedule(newSchedule);
    };

    const handleDelete = (index) => {
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        newSchedule.commands.splice(index, 1);
        setSchedule(newSchedule);
        setNeedSave(true);
    };

    const moveItem = (index, direction) => {
        const newSchedule = {}
        newSchedule.conditions = [...schedule.conditions]
        newSchedule.commands = [...schedule.commands]
        const item = newSchedule.commands.splice(index, 1)[0]; // Remove the item from the array
        newSchedule.commands.splice(index + direction, 0, item)
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
        ApiService.setSchedule(schedule)
        .then(response => {
            // Handle the successful response here
            console.log('Schedule updated successfully:', response);
            setNeedSave(false);
            // Optionally, you can update the local state with the response if needed
            // setSchedule(response);
        })
        .catch(error => {
            // Handle any errors here
            console.error('Error updating schedule:', error);
            // Show an error message to the user if you have a UI component for that
        });
    };


    if (!schedule || ! currentCommand) {
        return <Typography>Loading...</Typography>;
    }

    return (
        <div style={{padding: 5}}>
            <Grid container spacing={2}>
                <Grid item xs={5}>    
                    <Typography > Currently playing </Typography>
                </Grid>
                <Grid item xs={1} >
                    <SmartDisplayIcon fontSize="large"/>
                </Grid>
                <Grid item xs={6} >    
                    <Typography variant="h4" style={{padding: 0}}> &nbsp;{currentCommandName} </Typography>
                </Grid>
                
                <Grid item xs={12} >    
                    <Typography variant="" component="i"> {currentCommand.description}: </Typography>
                </Grid>
                <Grid item xs={12} md={6}>        
                    {currentCommand.screenshots ? (
                        <>
                    <CardMedia
                        component="img"
                        image={`${BASE_URL}/screenshots/${currentCommand.name}/${currentCommand.screenshots[0]}`}
                    />
                    </>
                    ) : ( "no screenshot" ) }
                </Grid>
                <Grid item xs={12}>    
                    <Typography> Next commands: </Typography>
                </Grid>

                {schedule.commands.map((item, index) => (
                <>
                   <Grid item xs={4}>
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
                    </Grid>
                    <Grid item xs={4}>
                        
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
                </>
                ))}
            
            <Grid item xs={12}>    
            <Button 
                variant="contained" 
                startIcon={<AddCircleOutlineIcon />}
                onClick={handleAdd}
                sx={{margin: "2px"}}
            >
                Add Command
            </Button>
            <Button 
                variant="contained" 
                color="secondary" 
                disabled={!needSave}
                onClick={handleSave}
                sx={{margin: "2px"}}
            >
                Save Changes
            </Button>
            </Grid>
            </Grid>
        </div>
    );
}

export default ScheduleViewer;
