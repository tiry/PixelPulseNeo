import React, { useEffect, useState } from 'react';
import ApiService from '../services/ApiService';
import { List, ListItem, ListItemText, Button, Grid, Card, CardMedia, CardContent } from '@mui/material';
import BASE_URL from '../services/ApiService'

//const BASE_URL = 'http://localhost:5000';
//const BASE_URL = '';
//const BASE_URL = '/api';
//const BASE_URL = 'http://lcddriver.local:5000/api';

function CommandList() {
    const [commands, setCommands] = useState([]);

    useEffect(() => {
        ApiService.getCommands().then(setCommands);
    }, []);

    const handleExecute = (name) => {
        ApiService.executeCmd(name)
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
       <List>
            {commands.map((command, index) => (
                <ListItem key={index}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={4}>
                            <ListItemText primary={command.name} secondary={command.description} />
                            <Button variant="contained" color="primary"
                            onClick={() => handleExecute(command.name)}>
                                Execute Now
                            </Button>
                        </Grid>
                        <Grid item xs={12} md={8}>
                            {command.screenshots && command.screenshots.map((screenshot, idx) => (
                                <Card key={idx} style={{ maxWidth: 345, margin: '10px' }}>
                                    <CardMedia
                                        component="img"
                                        height="140"
                                        image={`${BASE_URL}/screenshots/${command.name}/${screenshot}`}
                                        alt={`Screenshot ${idx + 1}`}
                                    />
                                </Card>
                            ))}
                        </Grid>
                    </Grid>
                </ListItem>
            ))}
        </List>    );
}

export default CommandList;
