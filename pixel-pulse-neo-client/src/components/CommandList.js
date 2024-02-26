import React, { useEffect, useState } from 'react';
import ApiService from '../services/ApiService';
import { List, ListItem, ListItemText, Button, Grid, Card, CardHeader, CardActions, CardMedia,FormControl, Select, MenuItem, InputLabel } from '@mui/material';
import {BASE_URL} from '../services/ApiService'
import QueueIcon from '@mui/icons-material/Queue';
import QueuePlayNextIcon from '@mui/icons-material/QueuePlayNext';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

function CommandList() {
    const [commands, setCommands] = useState([]);
    const [selectedDurations, setSelectedDurations] = useState({});
    const [currentScreenshotIndex, setCurrentScreenshotIndex] = useState({});
    const IMG_TEMPO_S=20

    useEffect(() => {
        ApiService.getCommands().then(setCommands);
    }, []);

    useEffect(() => {
      // Initialize currentScreenshotIndex for each command
      const initialScreenshotIndexes = {};
      commands.forEach((command, index) => {
        if (command.screenshots && command.screenshots.length > 0) {
          initialScreenshotIndexes[command.name] = 0;
        }
      });
      setCurrentScreenshotIndex(initialScreenshotIndexes);
  
      // Set intervals to cycle through screenshots for each command
      const intervals = commands.map((command) => {
        if (command.screenshots && command.screenshots.length > 0) {
          return setInterval(() => {
            setCurrentScreenshotIndex((prevState) => ({
              ...prevState,
              [command.name]: (prevState[command.name] + 1) % command.screenshots.length,
            }));
          }, IMG_TEMPO_S*1000); // Change every 20 seconds
        }
        return null;
      });
  
      return () => intervals.forEach((interval) => clearInterval(interval)); // Cleanup on unmount
    }, [commands]);

    const handleDurationChange = (commandName, duration) => {
        setSelectedDurations({ ...selectedDurations, [commandName]: duration });
    };

    const handleExecute = (name, interupt) => {
        const duration = selectedDurations[name] || 10;
        ApiService.executeCmd(name, duration, interupt)
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
        <Grid container spacing={2}>
                {commands.map((command, index) => (
                    <Grid item key={index} xs={12} md={6} lg={4}>
                            
                            <Card style={{ margin: '10px' }} title={command.name} subheader={command.description}>
                            
                                <CardHeader
                                    title={command.name}
                                    subheader={command.description}
                                />
                            
                                {command.screenshots && command.screenshots.length > 0 && (
                                <CardMedia
                                    component="img"
                                    image={`${BASE_URL}/screenshots/${command.name}/${command.screenshots[currentScreenshotIndex[command.name]]}`}
                                    alt={`Screenshot ${command.screenshots[currentScreenshotIndex[command.name]]}`}
                                />
                            )}
                            <CardActions>
                                <FormControl fullWidth>
                                    <InputLabel>Duration</InputLabel>
                                    <Select
                                    value={selectedDurations[command.name] || command.recommended_duration}
                                    label="Duration"
                                    onChange={(e) => handleDurationChange(command.name, e.target.value)}
                                    displayEmpty
                                    >
                                    <MenuItem value={10}>10s</MenuItem>
                                    <MenuItem value={20}>20s</MenuItem>
                                    <MenuItem value={30}>30s</MenuItem>
                                    <MenuItem value={60}>1 min</MenuItem>
                                    <MenuItem value={120}>2 min</MenuItem>
                                    <MenuItem value={300}>5 min</MenuItem>
                                    <MenuItem value={900}>15 min</MenuItem>
                                    <MenuItem value={1800}>30 min</MenuItem>
                                    </Select>
                                </FormControl>
                                <Button variant="contained" color="primary" startIcon={<QueuePlayNextIcon />}
                                    onClick={() => handleExecute(command.name, false)}>
                                    Next
                                </Button>
                                <Button variant="contained" color="primary" startIcon={<PlayArrowIcon />}
                                onClick={() => handleExecute(command.name, true)}>
                                    Now
                                </Button>
                            </CardActions>
                        </Card>
                    </Grid>
                ))}
        </Grid>
    );
}

export default CommandList;
