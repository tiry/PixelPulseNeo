import React, { useEffect, useState } from 'react';
import ApiService from '../services/ApiService';
import { List, ListItem, ListItemText, Button, Grid, Card, CardMedia, CardContent } from '@mui/material';

const BASE_URL = 'http://localhost:5000';

function CommandList() {
    const [commands, setCommands] = useState([]);

    useEffect(() => {
        ApiService.getCommands().then(setCommands);
    }, []);

    return (
       <List>
            {commands.map((command, index) => (
                <ListItem key={index}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={4}>
                            <ListItemText primary={command.name} secondary={command.description} />
                            <Button variant="contained" color="primary">
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
