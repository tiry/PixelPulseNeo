import React, { useEffect, useState } from 'react';
import ApiService from '../services/ApiService';
import { List, ListItem, ListItemText } from '@mui/material';

function ScheduleViewer() {
    const [schedule, setSchedule] = useState([]);

    useEffect(() => {
        ApiService.getSchedule().then(setSchedule);
    }, []);

    return (
        <List>
            {schedule.map((item, index) => (
                <ListItem key={index}>
                    <ListItemText primary={item.name} secondary={`Interval: ${item.interval} seconds`} />
                </ListItem>
            ))}
        </List>
    );
}

export default ScheduleViewer;
